"""
Nexus publisher for docker artifacts
"""
from pathlib import Path
import time
from typing import Any, Dict, Optional

from hoppr import HopprContext, Result, hoppr_rerunner
from hoppr.exceptions import HopprError

from nexus_bundler.publishers.base_publisher import Publisher
from nexus_bundler.nexus_instance import NexusInstance


class AptPublisher(Publisher):
    """
    Nexus publisher for apt artifacts

    Note that Nexus instances before v3.38.0 will fail to upload any
    .deb files that use .zst compression for their control files.
    See https://issues.sonatype.org/browse/NEXUS-28889
    """

    nexus_repository_type = "apt"
    required_tools = ["gpg"]

    def __init__(
        self, nexus_instance: NexusInstance, context: HopprContext, config: Any = None
    ) -> None:
        super().__init__(nexus_instance, context, config)

        if self.config is not None:
            if "gpg_command" in self.config:
                self.required_tools = [self.config["gpg_command"]]

    @hoppr_rerunner
    def push_artifact(self, path: Path) -> Result:
        """
        Publishes the artifact at the specified path to Nexus
        """

        with open(path, "rb") as asset_file:

            result = self.upload_component(
                repository=self.get_repository_name(path),
                files={"apt.asset": asset_file},
                verify=True,
            )

        if result.is_success():
            self.get_logger().info(f"Complete apt artifact copy for {path}")

        return result

    def _build_repository_request(self, path: Path) -> Dict:
        """
        Create the data block to request the required repo be built
        """

        data = super()._build_repository_request(path)

        ##### Additional fields for apt #####

        data["apt"] = {
            "distribution": "bionic",
            "forceBasicAuth": False,
        }

        gpg_key = self._generate_gpg_keys()
        if gpg_key is None:
            raise HopprError("Failed to generate GPG key set for APT repository")

        data["aptSigning"] = {
            "keypair": gpg_key,
        }

        return data

    def _generate_gpg_keys(self) -> Optional[str]:
        gpg_user = f"hoppr_apt_{time.strftime('%Y%m%d-%H%M%S')}"

        # Create GPG keyset

        command = [
            self.required_tools[0],
            "--batch",
            "--passphrase",
            "",
            "--quick-generate-key",
            gpg_user,
        ]

        result = self.run_command(command)
        if result.returncode != 0:
            self.get_logger().error(
                f"Attempt to generate gpg keys returned {result.returncode}"
            )
            return None

        # Export Secret Key

        command = [self.required_tools[0], "--armor", "--export-secret-key", gpg_user]

        result = self.run_command(command)
        if result.returncode != 0:
            self.get_logger().error(
                f"Attempt to export gpg keys returned {result.returncode}"
            )
            return None
        gpg_key = result.stdout.decode("utf-8").strip()

        # Find key fingerprint

        command = [self.required_tools[0], "--with-colons", "--list-keys", gpg_user]

        result = self.run_command(command)
        if result.returncode != 0:
            self.get_logger().error(
                f"Attempt to obtain gpg fingerprint returned {result.returncode}"
            )
            return None
        key_data = result.stdout.decode("utf-8").strip().split("\n")
        figerprint_index = (
            next(item for item in enumerate(key_data) if item[1].startswith("pub:"))[0]
            + 1
        )
        fingerprint = key_data[figerprint_index].split(":")[9]
        print(f"DEUBG: fingerprint={len(fingerprint)}")

        # Delete Keys

        for del_command in ["--delete-secret-keys", "--delete-keys"]:

            command = [
                self.required_tools[0],
                "--batch",
                "--yes",
                del_command,
                fingerprint,
            ]

            result = self.run_command(command)
            if result.returncode != 0:
                self.get_logger().error(
                    f"Attempt to gpg {del_command} returned {result.returncode}"
                )
                return None

        return gpg_key
