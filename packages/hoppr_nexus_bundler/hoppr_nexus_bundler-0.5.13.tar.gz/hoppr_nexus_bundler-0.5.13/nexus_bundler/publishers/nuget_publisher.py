"""
Nexus publisher for nuget artifacts
"""

from pathlib import Path
from hoppr import Result, hoppr_rerunner
from nexus_bundler.publishers.base_publisher import Publisher


class NugetPublisher(Publisher):
    """
    Nexus publisher for nuget artifacts
    """

    nexus_repository_type = "nuget"

    @hoppr_rerunner
    def push_artifact(self, path: Path) -> Result:
        """
        Publishes the artifact at the specified path to Nexus
        """
        with open(path, "rb") as asset_file:

            result = self.upload_component(
                repository=self.get_repository_name(path),
                files={"nuget.asset1": asset_file},
                verify=True,
            )

        if result.is_success():
            self.get_logger().info(f"Complete nuget artifact copy for {path}")

        return result
