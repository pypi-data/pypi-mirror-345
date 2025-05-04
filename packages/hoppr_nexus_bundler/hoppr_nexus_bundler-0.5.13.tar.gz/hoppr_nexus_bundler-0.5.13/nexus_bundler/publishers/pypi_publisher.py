"""
Nexus publisher for pypi artifacts
"""

from pathlib import Path
from hoppr import Result, hoppr_rerunner
from nexus_bundler.publishers.base_publisher import Publisher


class PypiPublisher(Publisher):
    """
    Nexus publisher for pypi artifacts
    """

    nexus_repository_type = "pypi"

    @hoppr_rerunner
    def push_artifact(self, path: Path) -> Result:
        """
        Publishes the artifact at the specified path to Nexus
        """
        with open(path, "rb") as asset_file:

            result = self.upload_component(
                repository=self.get_repository_name(path),
                files={"pypi.asset1": asset_file},
                verify=True,
            )

        if result.is_success():
            self.get_logger().info(f"Complete pypi artifact copy for {path}")

        return result
