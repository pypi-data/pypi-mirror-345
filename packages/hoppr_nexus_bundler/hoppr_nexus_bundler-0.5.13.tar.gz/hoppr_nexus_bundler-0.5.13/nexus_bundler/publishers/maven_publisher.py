"""
Nexus publisher for maven artifacts
"""

from pathlib import Path
from typing import Dict
import re
from hoppr import Result, hoppr_rerunner
from nexus_bundler.publishers.base_publisher import Publisher


class MavenPublisher(Publisher):
    """
    Nexus publisher for maven artifacts
    """

    nexus_repository_type = "maven"
    nexus_repository_format = "maven2"

    @hoppr_rerunner
    def push_artifact(self, path: Path) -> Result:
        """
        Publishes the artifact at the specified path to Nexus
        """
        group_id = path.parts[-2]
        artifact = path.parts[-1]
        parser = r"(.*?)_(\d+(?:\.\d+)*)\.(.*)"
        match = re.search(parser, artifact)
        if match is None:
            return Result.fail(f"Invalid maven path: {path}")

        artifact_id = match.group(1)
        version = match.group(2)
        extension = match.group(3)

        with open(path, "rb") as asset_file:

            result = self.upload_component(
                repository=self.get_repository_name(path),
                files={"maven2.asset1": asset_file},
                data={
                    "maven2.groupId": group_id,
                    "maven2.artifactId": artifact_id,
                    "maven2.version": version,
                    "maven2.asset1.extension": extension,
                },
                verify=True,
            )

        if result.is_success():
            self.get_logger().info(f"Complete maven artifact copy for {path}")

        return result

    def _build_repository_request(self, path: Path) -> Dict:
        """
        Create the data block to request the required repo be built
        """

        data = super()._build_repository_request(path)

        ##### Additional fields for maven #####
        data["maven"] = {"versionPolicy": "MIXED", "layoutPolicy": "STRICT"}

        return data
