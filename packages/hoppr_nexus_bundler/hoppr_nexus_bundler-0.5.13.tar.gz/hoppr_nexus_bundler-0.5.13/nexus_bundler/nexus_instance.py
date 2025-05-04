"""
Dataclass specifying a Nexus instance
"""

from dataclasses import dataclass
import multiprocessing
from os import environ
import re
from typing import Optional

from hoppr.exceptions import HopprCredentialsError


@dataclass
class NexusInstance:  # pylint: disable=too-many-instance-attributes
    """
    Dataclass specifying a Nexus instance
    """

    url: str
    userid: str
    password_env: str
    password: str
    docker_url: Optional[str] = None
    docker_port: int = 5000
    force_http: bool = False

    def __init__(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        url: str,
        userid: str,
        password_env: str,
        docker_url: str = None,
        docker_port: int = 5000,
        force_http: bool = False,
    ):

        self.url = url
        self.userid = userid
        self.password_env = password_env
        self.docker_url = docker_url
        self.docker_port = docker_port
        self.force_http = force_http
        self.repository_lock = multiprocessing.Manager().RLock()

        if self.password_env not in environ:
            raise HopprCredentialsError(
                f"'{self.password_env}' not found in environment variables.",
            )
        self.password = environ[self.password_env]

        if self.docker_url is None:
            self.docker_url = re.sub(
                r"(https?://[^/:]*)(\:\d+)?(/?)",
                r"\1:" + str(self.docker_port) + r"\3",
                self.url,
            )

        if not self.url.endswith("/"):
            self.url += "/"

        if not self.docker_url.endswith("/"):
            self.docker_url += "/"

    def get_repository_api(self) -> str:
        """
        Return the base url for the Nexus repositories api
        """
        return f"{self.url}service/rest/beta/repositories"

    def get_component_api(self) -> str:
        """
        Return the base url for the Nexus components api
        """
        return f"{self.url}service/rest/v1/components"
