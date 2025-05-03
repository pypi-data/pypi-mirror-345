import re
from typing import Union
from dataclasses import dataclass
import logging

from nornir.core import Nornir
from nornir.core.inventory import Host, ConnectionOptions
import yaml

from .cyberark import Cyberark, CyberarkLookupError

logger = logging.getLogger(__name__)


@dataclass
class CustomCredential:
    """
    Class that holds data around a custom credential stored in cyberark.
    """

    _c: Cyberark
    host_match: re.Pattern
    env: str
    username: str
    password_host: str

    # cached credentials for this object
    _user_password = False
    _user_enable = False

    def get_user_password(self) -> Union[str, None]:
        """
        Attempts to look up the password tied to this username and 'host' in cyberark.
        Returns None if no password was found
        """
        if self._user_password is False:
            try:
                self._user_password = self._c.lookup_username_password(
                    self.username, host=self.password_host, environment=self.env
                )
            except CyberarkLookupError:
                self._user_password = None

        return self._user_password

    def get_user_enable(self) -> Union[str, None]:
        """
        Returns enable secret after loooking it up in cyberark
        """
        if self._user_enable is False:
            try:
                self._user_enable = self._c.lookup_enable(
                    host=self.password_host, environment=self.env
                )
            except CyberarkLookupError:
                self._user_enable = None

        return self._user_enable


class CredentialMap:
    """
    Class that stores custom credentials defined in the
    credential map and can look up credentials in cyberark
    """

    def __init__(
        self,
        cyberark_env_file: str,
    ):
        """
        Parses credential map file into list of credential objects
        """

        # yeah kind of sketch but it's fine
        map_file = __file__.replace("/credentials.py", "/credential_map.yml")

        with open(map_file, encoding="utf-8") as fh:
            credential_map = yaml.load(fh, yaml.Loader)

        self.default_user = None
        self.default_enable = None
        self.default_cyberark_env = None

        # three default values are required in the credential map file
        for default in ["default_user", "default_enable", "default_cyberark_env"]:
            if default not in credential_map:
                raise ValueError(f"{default} must be set in credential map!")
            setattr(self, default, credential_map[default])

        self.cyberark = Cyberark(cyberark_env_file)

        # parsing each custom value
        self.custom = []
        for custom in credential_map["custom"]:

            # host match is required
            if not custom.get("host_match"):
                raise ValueError(
                    f"No host match specified for custom credential {custom}"
                )

            # and it must be a valid regex string
            try:
                host_match = re.compile(custom["host_match"])
            except TypeError as e:
                raise ValueError(
                    f"Uncompileable host match {custom['host_match']}"
                ) from e

            self.custom.append(
                CustomCredential(
                    _c=self.cyberark,
                    host_match=host_match,
                    env=custom.get("env", self.default_cyberark_env),
                    username=custom.get("username"),
                    password_host=custom.get("password_host"),
                )
            )

    def set_default_credentials(self, nr: Nornir):
        """
        Sets default username/password for nornir
        """
        nr.inventory.defaults.username = self.default_user
        nr.inventory.defaults.password = self.cyberark.lookup_username_password(
            self.default_user
        )

    def set_host_credentials(self, host: Host):
        """
        Sets the host credentials of a given nornir object if a custom credential is
        found for it. If there isn't a custom credential in the credential map
        it's assumed the default credentials are set and those are sufficient
        """

        for cred in self.custom:
            if re.match(cred.host_match, host.name):

                custom_password = cred.get_user_password()
                if custom_password:
                    host.username = cred.username
                    host.password = custom_password
                    logger.debug(
                        "Setting custom user/pass for %s: %s %s",
                        host.name,
                        host.username,
                        host.password,
                    )
                else:
                    logger.error(
                        "No password found in cyberark for %s and cred_map match %s",
                        host.name,
                        cred.host_match,
                    )

                # in general we expect a corresponding custom enable if there's a custom password
                # but that's not always the case
                custom_enable = cred.get_user_enable()
                if custom_enable:
                    conn_options = ConnectionOptions(
                        extras={"optional_args": {"secret": custom_enable}}
                    )
                    host.connection_options["umnet_napalm"] = conn_options
                    logger.debug(
                        "Setting custom secret for %s: %s", host.name, custom_enable
                    )

                return
