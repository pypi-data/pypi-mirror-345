"""
Nexus publisher for raw artifacts
"""

from pathlib import Path
from typing import Dict
from hoppr import Result, hoppr_rerunner
from nexus_bundler.publishers.base_publisher import Publisher


class RawPublisher(Publisher):
    """
    Nexus publisher for raw artifacts
    """

    nexus_repository_type = "raw"

    @hoppr_rerunner
    def push_artifact(self, path: Path) -> Result:
        """
        Publishes the artifact at the specified path to Nexus
        """

        path_from_root = path.absolute().relative_to(self.root_dir)
        upload_dir = f"/{'/'.join(path_from_root.parts[2:-1])}/"

        with open(path, "rb") as asset_file:

            result = self.upload_component(
                repository=self.get_repository_name(path),
                files={"raw.asset1": asset_file},
                data={
                    "raw.directory": upload_dir,
                    "raw.asset1.filename": path.parts[-1],
                },
                verify=True,
            )

        if result.is_success():
            self.get_logger().info(f"Complete raw artifact copy for {path}")

        return result

    def get_repository_name(self, path: Path) -> str:
        """
        Meta-data should go in a special repository
        """
        rel_path = path.absolute().relative_to(self.root_dir)
        if rel_path.parts[1] == "_metadata_":
            return "hoppr_metadata"

        return super().get_repository_name(path)

    def _build_repository_request(self, path: Path) -> Dict:
        """
        Create the data block to request the required repo be built
        """

        data = super()._build_repository_request(path)

        ##### Additional fields for raw #####

        data["raw"] = {"contentDisposition": "ATTACHMENT"}
        data["storage"]["strictContentTypeValidation"] = False

        return data
