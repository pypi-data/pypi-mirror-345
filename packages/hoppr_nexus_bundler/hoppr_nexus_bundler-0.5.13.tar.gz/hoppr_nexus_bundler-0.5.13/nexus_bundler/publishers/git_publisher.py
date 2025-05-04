"""
Nexus publisher for git artifacts
"""

from contextlib import ExitStack
import os
from pathlib import Path
from typing import Dict
from hoppr import Result, hoppr_rerunner
from nexus_bundler.publishers.base_publisher import Publisher


class GitPublisher(Publisher):
    """
    Nexus publisher for git artifacts
    """

    nexus_repository_type = "raw"

    @hoppr_rerunner
    def push_artifact(self, path: Path) -> Result:
        """
        Publishes the artifact at the specified path to Nexus
        """

        # Use an exitstack to ensure the files get closed
        with ExitStack() as stack:
            path_from_root = path.absolute().relative_to(self.root_dir)
            upload_dir = f"/{'/'.join(path_from_root.parts[2:-1])}/"
            payload = {}
            values = {"raw.directory": upload_dir}

            # Iterate through all files to upload, strip directories
            files = [f for f in path.glob("**/*") if f.is_file()]

            for i, file in enumerate(files, start=1):
                payload[f"raw.asset{i}"] = stack.enter_context(open(file, "rb"))
                values[f"raw.asset{i}.filename"] = str(file.relative_to(path))

            result = self.upload_component(
                repository=self.get_repository_name(path),
                files=payload,
                data=values,
                verify=True,
            )

            if result.is_success():
                self.get_logger().info(f"Complete raw artifact copy for {path}")

        return result

    def _build_repository_request(self, path: Path) -> Dict:
        """
        Create the data block to request the required repo be built
        """

        data = super()._build_repository_request(path)

        ##### Additional fields for git #####
        data["raw"] = {"contentDisposition": "ATTACHMENT"}
        data["storage"]["strictContentTypeValidation"] = False

        return data

    def should_process_at(self, path: Path) -> bool:
        """
        Returns whether or not to perform processing at this level.

        Some publishers (e.g. git) will process at a directory level.  Those publishers will need
        to override this method.
        """

        return path.parts[-1].endswith(".git") and os.path.isdir(path)
