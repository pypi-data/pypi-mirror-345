"""
Base class for all nexus publishers
"""

from abc import ABC, abstractmethod
import itertools
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any, Dict, List, Optional
import requests
from hoppr import HopprContext, HopprLogger, Result, hoppr_rerunner
from hoppr.exceptions import HopprError
from hoppr.plugin_utils import check_for_missing_commands, repo_url_from_dir_name
from hoppr.utils import obscure_passwords
from nexus_bundler.nexus_instance import NexusInstance


class Publisher(ABC):
    """
    Base class for all nexus publishers
    """

    id_iter = itertools.count()

    nexus_repository_type = "raw"
    nexus_repository_format = None
    required_tools: List[str] = []

    def __init__(
        self, nexus_instance: NexusInstance, context: HopprContext, config: Any = None
    ) -> None:
        self.instance_id = next(self.id_iter)
        self.nexus_instance = nexus_instance
        if self.nexus_repository_format is None:
            self.nexus_repository_format = self.nexus_repository_type
        log_name = f"pub--{self.__class__.__name__}--{os.getpid()}-{self.instance_id}"
        self.context = context
        self._logger = HopprLogger(
            name=log_name,
            filename=str(context.logfile_location),
            lock=context.logfile_lock,
        )
        self.root_dir = Path(context.collect_root_dir).absolute()
        self.config = config

    def get_logger(self) -> HopprLogger:
        """
        Returns the logger for this publisher (needed by hoppr_rerunner)
        """
        return self._logger

    def close_logger(self) -> None:
        """
        Close (and flush) all handlers for this publisher's logger
        """
        self._logger.close()

    def publish(self, path: Path) -> Result:
        """
        Publish an artifact to nexus
        """
        self.get_logger().info(f">>> Started publish to Nexus for {path}")
        result = self.prepare_push_artifact(path)
        if result.is_success():
            result = self.push_artifact(path)

        self.get_logger().info(f"Completed publish for {path}, result: {result}")

        self.get_logger().close()

        return result

    @abstractmethod
    def push_artifact(self, path: Path) -> Result:
        """
        Publishes the artifact at the specified path to Nexus

        Implementations should use @hoppr_rerunner decorator to handle retries

        Basic structure should be:
          - Build files/data and call upload_component (1 or more times)

        Not all purl types follow this pattern.
        """

    @hoppr_rerunner
    def prepare_push_artifact(self, path: Path) -> Result:
        """
        Common preparatory steps before pushing an artifact:
          - Create logger
          - Check for required commands
          - Check for repository, create if necessary
        """

        command_result = check_for_missing_commands(self.required_tools)
        if command_result.is_fail():
            self.get_logger().error(command_result.message)
            return command_result

        with self.nexus_instance.repository_lock:
            try:
                build_repo = not self._has_good_repository(path)
            except HopprError as err:
                # An exception may be raised if the required repository can not be created
                return Result.fail(str(err))

            if build_repo:
                data = self._build_repository_request(path)
                headers = {
                    "Content-Type": "application/json",
                    "accept": "application/json",
                }

                repo_name = self.get_repository_name(path)
                self.get_logger().info(f"Creating Repository {repo_name}")

                response = requests.post(
                    f"{self.nexus_instance.get_repository_api()}/"
                    + f"{self.nexus_repository_type}/hosted",
                    auth=(self.nexus_instance.userid, self.nexus_instance.password),
                    data=json.dumps(data),
                    headers=headers,
                    timeout=600,
                )

                if response.status_code != 201:
                    msg = (
                        f"Response code {response.status_code} returned from nexus API call to "
                        + f"create {self.nexus_repository_type} repository '{repo_name}'.\n"
                        + f"Response text: {response.text}"
                    )
                    self.get_logger().error(msg)
                    return Result(Result.from_http_response(response).status, msg)

        return Result.success()

    @hoppr_rerunner
    def finalize(self) -> Result:
        """
        Post-processor for after all attributes have been pushed
        """

        return Result.skip()

    def should_process_at(self, path: Path) -> bool:
        """
        Returns whether or not to perform processing at this level.

        Some publishers (e.g. git) will process at a directory level.  Those publishers will need
        to override this method.
        """

        return path.is_file()

    ##### Repository Methods #####

    def get_repository_name(self, path: Path) -> str:
        """
        Returns the appropriate nexus repository name for the artifact at the specified path
        """
        rel_path = path.absolute().relative_to(self.root_dir)
        repo_name = "transfer-" + rel_path.parts[0]
        source_url = repo_url_from_dir_name(rel_path.parts[1])

        ##### If the source looks like a Nexus repository, use the Nexus repository name #####

        match_data = re.match("^.*/repository/(.*?)/", source_url + "/")
        if match_data:
            repo_name = match_data.group(1)

        return repo_name

    def _has_good_repository(self, path: Path) -> bool:
        """
        Check if a matching nexus repository already exists
        """

        ### Get existing repos, and see if the requested repo name is already created

        repo_list = requests.get(
            f"{self.nexus_instance.get_repository_api()}/",
            auth=(self.nexus_instance.userid, self.nexus_instance.password),
            timeout=600,
        )

        if repo_list.status_code != 200:
            msg = (
                f"Error code retrieving list of repositories: {repo_list.status_code}\n"
                + f"Reason: {repo_list.reason}"
            )
            self.get_logger().error(msg)
            raise HopprError(msg)

        for repo in repo_list.json():
            if self._is_good_repository(repo, path):
                self.get_logger().info(
                    f"Repository {repo['name']} already exists with format {repo['format']}, "
                    + "was not re-created"
                )
                return True

        return False

    def _is_good_repository(self, repo: Dict, path: Path):
        """
        See if this repo is appropriate for the selected artifact
        """

        requested_repo = self.get_repository_name(path)

        if (
            repo["name"] == requested_repo
            and repo["format"] == self.nexus_repository_format
        ):
            return True

        if (
            repo["name"] == self.get_repository_name(path)
            and repo["format"] != self.nexus_repository_format
        ):
            msg = (
                f"Repository {repo['name']} already exists with format '{repo['format']}'. "
                + f"Format '{self.nexus_repository_format}' required."
            )
            self.get_logger().error(msg)
            raise HopprError(msg)

        return False

    def _build_repository_request(self, path: Path) -> Dict:
        """
        Create the data block to request the required repo be built
        """

        data = {
            "name": self.get_repository_name(path),
            "online": True,
            "storage": {
                "blobStoreName": "default",
                "strictContentTypeValidation": True,
                "writePolicy": "allow",
            },
            "cleanup": {"policyNames": []},
        }

        return data

    ##### Component Methods #####

    def upload_component(
        self,
        repository: str,
        files: Optional[Dict] = None,
        data: Optional[Dict] = None,
        verify: bool = True,
    ) -> Result:
        """
        Upload a single component to Nexus
        """

        response = requests.post(
            f"{self.nexus_instance.get_component_api()}?repository={repository}",
            files=files,
            data=data,
            auth=(self.nexus_instance.userid, self.nexus_instance.password),
            allow_redirects=True,
            verify=verify,
            timeout=600,
        )

        return Result.from_http_response(response)

    def run_command(self, command, password_list=None, cwd=None):
        """
        Run a command and log any errors
        """
        result = subprocess.run(command, check=False, capture_output=True, cwd=cwd)
        if result.returncode != 0:
            obscured_command = obscure_passwords(command, password_list)
            self.get_logger().error(f"Failed to execute command: {obscured_command}")
            self.get_logger().info(
                f"PROCESS STDOUT:\n{result.stdout.decode('utf-8').strip()}"
            )
            self.get_logger().info(
                f"PROCESS STDERR:\n{result.stderr.decode('utf-8').strip()}"
            )

        return result
