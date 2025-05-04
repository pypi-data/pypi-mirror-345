"""
Hoppr plugin to bundle artifacts to Nexus
"""

from concurrent.futures import Future, ThreadPoolExecutor
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from hoppr import HopprContext, HopprPlugin, Result, hoppr_process
from hoppr.exceptions import HopprPluginError

from nexus_bundler import __version__
from nexus_bundler.publishers.apt_publisher import AptPublisher
from nexus_bundler.publishers.base_publisher import Publisher
from nexus_bundler.publishers.maven_publisher import MavenPublisher
from nexus_bundler.publishers.git_publisher import GitPublisher
from nexus_bundler.publishers.raw_publisher import RawPublisher
from nexus_bundler.publishers.pypi_publisher import PypiPublisher
from nexus_bundler.publishers.helm_publisher import HelmPublisher
from nexus_bundler.publishers.docker_publisher import DockerPublisher
from nexus_bundler.publishers.nuget_publisher import NugetPublisher
from nexus_bundler.publishers.npm_publisher import NpmPublisher
from nexus_bundler.nexus_instance import NexusInstance
from nexus_bundler.publishers.yum_publisher import YumPublisher


def _publish(publisher: Publisher, path: Path) -> Result:
    pub_instance = publisher.__class__(
        publisher.nexus_instance, publisher.context, publisher.config
    )
    return pub_instance.publish(path)


class NexusBundlePlugin(HopprPlugin):
    """
    Hoppr plugin to bundle artifacts to Nexus
    """

    publishers: Dict[str, Publisher] = {}

    def get_version(self) -> str:
        return __version__

    def __init__(self, context: HopprContext, config: Any = None) -> None:
        super().__init__(context, config)

        use_config = {}
        if config is not None:
            use_config = config

        self.nexus_instance = NexusInstance(
            use_config.get("url", f'http://{os.getenv("NEXUS_IP")}:8081/'),
            use_config.get("username", "admin"),
            use_config.get("password_env", "NEXUS_PW"),
            use_config.get("docker_url", f'http://{os.getenv("NEXUS_IP")}:5000/'),
            use_config.get("docker_port", 5000),
            use_config.get("force_http", False),
        )

        self._results: List[Tuple[Publisher, Path, Result]] = []
        self.failures = 0
        self.retries = 0
        self.finalize_failures = 0

    def _append_result(
        self, publisher: Publisher, path: Path, future_result: Result
    ) -> None:
        self._results.append((publisher, path, future_result))

        if future_result.is_fail():
            self.failures += 1
        if future_result.is_retry():
            self.retries += 1

    def _summary_result(self) -> Result:
        if self.failures + self.retries + self.finalize_failures == 0:
            return Result.success()

        messages = []

        if self.failures > 0:
            messages.append(f"{self.failures} 'publish' processes failed")
        if self.retries > 0:
            messages.append(f"{self.retries} 'publish' processes returned 'retry'")
        if self.finalize_failures > 0:
            messages.append(f"{self.finalize_failures} 'finalize' processes failed")
        return Result.fail("; ".join(messages))

    def _get_publisher(  # pylint: disable=too-many-return-statements
        self, directory: str
    ) -> Optional[Publisher]:
        if Path(directory).absolute() == Path(self.context.collect_root_dir).absolute():
            return None

        rel_path = (
            Path(directory)
            .absolute()
            .relative_to(Path(self.context.collect_root_dir).absolute())
        )

        def retrieve_publisher(purl_type: str, publisher) -> Publisher:
            if purl_type not in self.publishers:
                self.publishers[purl_type] = publisher(
                    self.nexus_instance, self.context, self.config
                )
            return self.publishers[purl_type]

        publisher = None
        purl_type = rel_path.parts[0]
        match purl_type:
            case "raw" | "generic":
                publisher = retrieve_publisher("raw", RawPublisher)
            case "maven":
                publisher = retrieve_publisher("maven", MavenPublisher)
            case "pypi":
                publisher = retrieve_publisher("pypi", PypiPublisher)
            case "git" | "gitlab" | "github":
                publisher = retrieve_publisher("git", GitPublisher)
            case "helm":
                publisher = retrieve_publisher("helm", HelmPublisher)
            case "docker":
                publisher = retrieve_publisher("docker", DockerPublisher)
            case "rpm" | "yum":
                publisher = retrieve_publisher("yum", YumPublisher)
            case "deb":
                publisher = retrieve_publisher("apt", AptPublisher)
            case "nuget":
                publisher = retrieve_publisher("nuget", NugetPublisher)
            case "npm":
                publisher = retrieve_publisher("npm", NpmPublisher)

        if publisher is None:
            raise HopprPluginError(
                f"No Nexus Publisher defined for purl type {purl_type}"
            )

        return publisher

    @hoppr_process
    def pre_stage_process(self) -> Result:
        """
        Bundle artifacts from collect_root_dir into Nexus
        """

        self.get_logger().info(
            f"Bundling collected artifacts into Nexus, plugin version {__version__}"
        )
        self.get_logger().flush()

        #### For groundwork, running sequentially.  Multi-process later ####

        futures = []
        future_argument_map: Dict[Future, Tuple[Publisher, Path]] = {}

        with ThreadPoolExecutor(max_workers=self.context.max_processes) as executor:
            for directory, subdirs, files in os.walk(self.context.collect_root_dir):
                publisher = self._get_publisher(directory)
                if publisher is None:
                    continue

                dir_path = Path(directory)
                if publisher.should_process_at(dir_path):
                    future_proc = executor.submit(_publish, publisher, dir_path)
                    future_argument_map[future_proc] = (publisher, dir_path)
                    futures.append(future_proc)
                    subdirs[:] = []
                    files[:] = []

                for file in files:
                    path = dir_path.joinpath(file)
                    # publisher = self._get_publisher(directory)
                    if publisher.should_process_at(path):
                        future_proc = executor.submit(_publish, publisher, path)
                        future_argument_map[future_proc] = (publisher, path)
                        futures.append(future_proc)

            # Save all the results, count failures and retries
            # Note: future.results() blocks until the process is complete

            for future_proc in futures:
                future_result = future_proc.result()
                if not future_result.is_skip():
                    publisher, path = future_argument_map[future_proc]
                    self._append_result(publisher, path, future_result)

        for publisher in self.publishers.values():
            result = publisher.finalize()
            if result.is_fail():
                self.finalize_failures += 1

        return self._summary_result()
