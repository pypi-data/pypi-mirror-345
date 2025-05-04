"""
Nexus publisher for docker artifacts
"""
import json
import re

from importlib.metadata import version as dist_version
from pathlib import Path
from typing import Any, Dict

import requests

from hoppr import HopprContext, Result, hoppr_rerunner
from hoppr.exceptions import HopprError
from semver.version import Version

from nexus_bundler.nexus_instance import NexusInstance
from nexus_bundler.publishers.base_publisher import Publisher


class DockerPublisher(Publisher):
    """
    Nexus publisher for docker artifacts
    """

    nexus_repository_type = "docker"
    required_tools = ["skopeo"]

    def __init__(
        self, nexus_instance: NexusInstance, context: HopprContext, config: Any = None
    ) -> None:
        super().__init__(nexus_instance, context, config)

        if self.config is not None and "skopeo_command" in self.config:
            self.required_tools = [self.config["skopeo_command"]]

    @hoppr_rerunner
    def push_artifact(self, path: Path) -> Result:
        """
        Publishes the artifact at the specified path to Nexus
        """

        path_from_root = path.absolute().relative_to(self.root_dir)
        dest = "/".join(path_from_root.parts[2:])
        docker_url = re.sub(
            r"https?://", "docker://", str(self.nexus_instance.docker_url)
        )

        hoppr_version = dist_version("hoppr")
        hoppr_version = re.sub(
            r"v?(?P<version>[\d\.]+\d)(\.dev.*)?", r"\g<version>", hoppr_version
        )

        if Version.parse(hoppr_version) < Version.parse("1.8.6"):
            dest = docker_url + re.sub(r"(.*)_(.*)", r"\1:\2", dest)
        else:
            dest = docker_url + re.sub(r"(.*)@(.*)", r"\1:\2", dest)

        src = f"docker-archive:{path}"

        command = [
            self.required_tools[0],
            "copy",
            "--dest-creds",
            f"{self.nexus_instance.userid}:{self.nexus_instance.password}",
        ]

        if (
            re.match("^http://", str(self.nexus_instance.docker_url))
            or self.nexus_instance.force_http
        ):
            command.append("--dest-tls-verify=false")

        command.extend((src, dest))
        proc = self.run_command(command, [self.nexus_instance.password])

        if proc.returncode != 0:
            msg = (
                f"Skopeo failed to copy docker image to {dest}, "
                + f"return_code={proc.returncode}"
            )
            self.get_logger().error(msg)
            return Result.retry(msg)

        self.get_logger().info(f"Complete docker artifact copy for {path}")

        return Result.success()

    @hoppr_rerunner
    def prepare_push_artifact(self, path: Path) -> Result:
        """Activate a realm required for the requested repo"""

        headers = {"Content-Type": "application/json", "accept": "application/json"}

        address = f"{self.nexus_instance.url}service/rest/beta/security/realms/active"

        response = requests.get(
            address,
            auth=(self.nexus_instance.userid, self.nexus_instance.password),
            headers=headers,
            timeout=600,
        )

        if response.status_code != 200:
            msg = (
                f"Response code {response.status_code} returned from nexus API to retrieve "
                + "active realms.\n"
                + f"Response text: {response.text}"
            )
            self.get_logger().error(msg)
            return Result.from_http_response(response)

        realms = response.json()

        if "DockerToken" not in realms:
            realms.append("DockerToken")
            response = requests.put(
                address,
                auth=(self.nexus_instance.userid, self.nexus_instance.password),
                data=json.dumps(realms),
                headers=headers,
                timeout=600,
            )
            if response.status_code != 204:
                msg = (
                    f"Response code {response.status_code} returned from "
                    + "Nexus API call to add DockerToken realm.\n"
                    + f"Response text: {response.text}"
                )
                self.get_logger().error(msg)
                return Result.from_http_response(response)

        return super().prepare_push_artifact(path)

    def _is_good_repository(self, repo: Dict, path: Path):
        """
        See if this repo is appropriate for the selected artifact
        """

        requested_repo = self.get_repository_name(path)

        if repo["name"] == requested_repo and (
            self.nexus_instance.docker_port
            in (repo["docker"]["httpsPort"], repo["docker"]["httpPort"])
        ):
            return True

        if repo["name"] == self.get_repository_name(path):
            msg = (
                f"Docker Repository {repo['name']} already exists, "
                + f"but the HTTPS port is {repo['docker']['httpsPort']} "
                + f"and the HTTP port is {repo['docker']['httpPort']}, "
                + f"one must be {self.nexus_instance.docker_port}"
            )
            self.get_logger().error(msg)
            raise HopprError(msg)

        if repo["format"] == "docker" and (
            self.nexus_instance.docker_port
            in [repo["docker"]["httpPort"], repo["docker"]["httpsPort"]]
        ):
            msg = (
                f"Port {self.nexus_instance.docker_port} is already in use by "
                + f"docker Repository {repo['name']}"
            )
            self.get_logger().error(msg)
            raise HopprError(msg)

        return super()._is_good_repository(repo, path)

    def _has_good_repository(self, path: Path) -> bool:
        if self.get_repository_name(path) != self.get_repository_name(path).lower():
            msg = f"Docker repo name {self.get_repository_name(path)}\
            is invalid. Must be all lower case."
            raise HopprError(msg)

        return super()._has_good_repository(path)

    def _build_repository_request(self, path: Path) -> Dict:
        """
        Create the data block to request the required repo be built
        """

        data = super()._build_repository_request(path)

        ##### Additional fields for docker #####

        if (
            re.match("^http://", str(self.nexus_instance.docker_url))
            or self.nexus_instance.force_http
        ):
            port_type = "httpPort"
        else:
            port_type = "httpsPort"

        data["docker"] = {
            "v1Enabled": True,
            "forceBasicAuth": False,
            port_type: self.nexus_instance.docker_port,
        }

        return data
