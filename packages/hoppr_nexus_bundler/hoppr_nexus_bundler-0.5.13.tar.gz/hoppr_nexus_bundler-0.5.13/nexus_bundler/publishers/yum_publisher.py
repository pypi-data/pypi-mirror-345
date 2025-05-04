"""
Nexus publisher for yum artifacts
"""

import json
from pathlib import Path
import re
from typing import Any, Dict, List
import requests
from hoppr import HopprContext, Result, hoppr_rerunner
from hoppr.exceptions import HopprPluginError
from nexus_bundler.publishers.base_publisher import Publisher
from nexus_bundler.nexus_instance import NexusInstance


class YumPublisher(Publisher):
    """
    Nexus publisher for yum artifacts
    """

    nexus_repository_type = "yum"

    def __init__(
        self, nexus_instance: NexusInstance, context: HopprContext, config: Any = None
    ) -> None:
        super().__init__(nexus_instance, context, config)
        self.yum_data_depth = -1

    @hoppr_rerunner
    def push_artifact(self, path: Path) -> Result:
        """
        Publishes the artifact at the specified path to Nexus
        """

        path_from_root = path.absolute().relative_to(self.root_dir)
        yum_dir = f"/{'/'.join(path_from_root.parts[2:-1])}/"

        with open(path, "rb") as asset_file:

            result = self.upload_component(
                repository=self.get_repository_name(path),
                files={"yum.asset": asset_file},
                data={
                    "yum.directory": yum_dir,
                    "yum.asset.filename": path.parts[-1],
                },
                verify=True,
            )

        if result.is_success():
            self.get_logger().info(f"Complete yum artifact publish for {path}")

        return result

    @hoppr_rerunner
    def finalize(self) -> Result:
        """
        Group yum repositories of different data depths
        """

        repository_list = requests.get(
            f"{self.nexus_instance.get_repository_api()}/",
            auth=(self.nexus_instance.userid, self.nexus_instance.password),
            timeout=600,
        )

        if repository_list.status_code != 200:
            msg = (
                f"Error code retrieving list of yum repositories: {repository_list.status_code}\n"
                + f"Reason: {repository_list.reason}"
            )
            self.get_logger().error(msg)
            return Result.from_http_response(repository_list)

        yum_groups: Dict[str, List[str]] = {}

        for repo in repository_list.json():
            match = re.search(r"^(.*)--d\d+$", repo["name"])
            if match is None or repo["format"] != "yum":
                continue

            group_name = match.group(1)

            if group_name not in yum_groups:
                yum_groups[group_name] = []

            if repo["name"] not in yum_groups[group_name]:
                yum_groups[group_name].append(repo["name"])

        headers = {"Content-Type": "application/json", "accept": "application/json"}

        for group_name, group_list in yum_groups.items():
            self.get_logger().info(f"Creating yum repo group {group_name}")

            data = {
                "name": group_name,
                "online": True,
                "storage": {
                    "blobStoreName": "default",
                    "strictContentTypeValidation": True,
                },
                "group": {"memberNames": group_list},
            }

            response = requests.post(
                f"{self.nexus_instance.get_repository_api()}/yum/group",
                auth=(
                    self.nexus_instance.userid,
                    self.nexus_instance.password,
                ),
                data=json.dumps(data),  # pylint: disable=duplicate-code
                headers=headers,
                timeout=600,
            )

            if response.status_code != 201:
                msg = (
                    f"Failed to create yum group repo {group_name}. "
                    + f"Response code: {response.status_code}. "
                    + f"Response message: {response.text}"
                )
                self.get_logger().error(msg)
                return Result.from_http_response(response)

            self.get_logger().info(f"Yum repo group {group_name} successfully created")

        return Result.success()

    def get_repository_name(self, path: Path) -> str:
        """
        Repo name must include yum data depth
        """

        if self.yum_data_depth < 0:
            rel_path = path.absolute().relative_to(self.root_dir)
            if "Packages" in rel_path.parts:
                self.yum_data_depth = rel_path.parts.index("Packages") - 2
            elif "RPMS" in rel_path.parts:
                self.yum_data_depth = rel_path.parts.index("RPMS") - 2
            else:
                self.yum_data_depth = len(rel_path.parts) - 3

        return f"{super().get_repository_name(path)}--d{self.yum_data_depth}"

    def _is_good_repository(self, repo: Dict, path: Path):
        """See if this repo matches the requested yum repo"""

        if not super()._is_good_repository(repo, path):
            return False

        if repo["yum"]["repodataDepth"] != self.yum_data_depth:
            msg = (
                f"Repository {repo['name']} already exists with Repodata Depth of "
                + f"\"{repo['yum']['repodataDepth']}\".  Cannot be combined with "
                + f'requested depth of "{self.yum_data_depth}"'
            )
            self.get_logger().error(msg)
            raise HopprPluginError(msg)

        return True

    def _build_repository_request(self, path: Path) -> Dict:
        """
        Create the data block to request the required repo be built
        """

        data = super()._build_repository_request(path)

        ##### Additional fields for yum #####

        data["yum"] = {"repodataDepth": self.yum_data_depth, "deployPolicy": "STRICT"}

        return data
