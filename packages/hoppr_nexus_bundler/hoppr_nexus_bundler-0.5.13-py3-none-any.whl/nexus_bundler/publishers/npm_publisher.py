"""
Nexus publisher for npm artifacts
"""

from pathlib import Path
from hoppr import Result, hoppr_rerunner
from nexus_bundler.publishers.base_publisher import Publisher


class NpmPublisher(Publisher):
    """
    Nexus publisher for npm artifacts
    """

    nexus_repository_type = "npm"

    @hoppr_rerunner
    def push_artifact(self, path: Path) -> Result:
        """
        Publishes the artifact at the specified path to Nexus
        """
        with open(path, "rb") as asset_file:

            result = self.upload_component(
                repository=self.get_repository_name(path),
                files={"npm.asset1": asset_file},
                verify=True,
            )

        if result.is_success():
            self.get_logger().info(f"Complete npm artifact copy for {path}")

        return result
