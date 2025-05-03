from typing import Optional, Dict
import ipaddress

from os import getenv
from os.path import isdir
import re

from git import Repo
import yaml
from decouple import UndefinedValueError, Config, RepositoryEnv
from cron_converter import Cron

from nornir.core.inventory import Host

from umnet_napalm.abstract_base import AbstractUMnetNapalm

from .nornir import inventory_filters
from .mappers import save_to_db, save_to_file


class AgadorError(Exception):
    pass


class CommandMapError(Exception):
    def __init__(self, cmd: str, error_str: str):
        super().__init__(f"command map error for '{cmd}' - {error_str}")


def get_config_settings(cfg_file: Optional[str]) -> Config:
    """
    Get config settings from file, or if 'None' is provided, look for 'AGADOR_CFG'
    in environment
    """

    cfg_file = cfg_file if cfg_file else getenv("AGADOR_CFG")
    if not cfg_file:
        raise AgadorError("No config file provided, and no AGADOR_CFG env set!")

    try:
        return Config(RepositoryEnv(cfg_file))
    except FileNotFoundError:
        raise AgadorError(f"Cannot locate agador config file {cfg_file}")


def is_ip_address(ip: str) -> bool:
    """
    Returns whether a string is an IP (eg 10.233.0.10 or fe80::1)
    """
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        return False
    return True


def is_ip_or_prefix(ip: str) -> bool:
    """
    Returns whether a string is an ip (10.233.0.10) or
    IP + prefix (10.233.0.10/24). IPv6 works as well.
    """
    try:
        ipaddress.ip_interface(ip)
    except ValueError:
        return False
    return True


def validate_email_list(input_str: str):
    """
    Makes sure that the input string is a comma-separated list
    of email addresses. Fun fact - the 'local' part of the email address
    can have a super wide range of characters, so we're just checking for non-whitespace
    The domain can have a-zA-Z0-9 and -, so we can be a bit more circumspect there.

    Function does nothing but throw an exception if the email is invalid
    """
    for email in re.split(r",", input_str):
        if not re.match(r"\S+@[\w\-.]+\.\w+$", email):
            raise ValueError(f"Invalid email {email}")


def git_update(repo_path: str, commit_message: str):
    """
    Updates git repo and if applicable, the remote origin.
    Will overwrite origin.
    """
    repo = Repo(repo_path)
    repo.git.status()

    repo.git.add(all=True)
    repo.index.commit(commit_message)
    try:
        origin = repo.remote(name="origin")
    except ValueError:
        origin = None

    if origin:
        origin.push()


def parse_command_map(cfg: Config) -> dict:
    """
    Parses and validates command_map file, replacing text references
    to functions to references to the actual functions where applicable.

    Future task: pydantic-based validation
    """

    db_module = save_to_db
    file_module = save_to_file

    with open(cfg.get("CMD_MAP"), encoding="utf-8") as fh:
        cmd_map = yaml.safe_load(fh)

    output = {}
    for cmd, data in cmd_map["commands"].items():

        output[cmd] = {}

        # validating frequency, which is required
        if "frequency" not in data:
            raise CommandMapError(cmd, "Must specify frequency")
        try:
            output[cmd]["frequency"] = Cron(data["frequency"])
        except ValueError:
            raise CommandMapError(cmd, "Invalid frequency - must be in crontab format")

        # validating umnet_napalm getter specification
        if "getter" not in data:
            raise CommandMapError(cmd, "Must specify umnet_napalm getter")
        if data["getter"] not in dir(AbstractUMnetNapalm):
            raise CommandMapError(cmd, f"Unknown umnet_napalm getter {data['getter']}")
        output[cmd]["getter"] = data["getter"]

        # validating and retrieving inventory filter fuction
        inv_filter = data.get("inventory_filter", None)
        if inv_filter:
            if inv_filter not in dir(inventory_filters):
                raise CommandMapError(cmd, f"Unknown inventory filter {inv_filter}")

            output[cmd]["inventory_filter"] = getattr(inventory_filters, inv_filter)

        # validating and retrieving save_to_file class
        file_data = data.get("save_to_file", None)
        if file_data:
            if "mapper" not in file_data:
                raise CommandMapError(cmd, "Must specify mapper for save_to_file")

            if "destination" not in file_data:
                raise CommandMapError(cmd, "Must specify destination for save_to_file")

            destination = resolve_envs(file_data["destination"], cfg)
            if not isdir(destination):
                raise CommandMapError(
                    cmd, f"Invalid desintation {destination} for save_to_file"
                )

            if file_data["mapper"] not in dir(file_module):
                raise CommandMapError(
                    cmd, f"Unknown save_to_file mapper {file_data['mapper']}"
                )

            output[cmd]["save_to_file"] = {
                "mapper": getattr(file_module, file_data["mapper"])(destination),
            }

        # validating and retrieving save_to_db class
        db_data = data.get("save_to_db", None)
        if db_data:
            if db_data not in dir(db_module):
                raise CommandMapError(cmd, f"Unknown save_to_db mapper {db_data}")

            output[cmd]["save_to_db"] = getattr(db_module, db_data)

        if not db_data and not file_data:
            raise CommandMapError(
                cmd, "Must specifiy either save_to_db or save_to_file"
            )

    return output


def get_device_cmd_list(
    cmd_map: dict, host: Host, cmd_list_filter: Optional[list] = None
) -> Dict[str, str]:
    """
    Gets list of commands tied to a device based on its
    host inventory data. Optionally provide a list of commands to
    restrict the output to.

    Returns a dict mapping the agador command to the umnet_napalm getter
    """
    cmd_list = {}
    for cmd, data in cmd_map.items():

        if cmd_list_filter and cmd not in cmd_list_filter:
            continue

        if not data.get("inventory_filter") or data["inventory_filter"](host):
            cmd_list[cmd] = data["getter"]

    return cmd_list


def resolve_envs(input_str: str, cfg: Config) -> str:
    """
    Takes an input string and searches for all instances of '${ENV_VAR}', replacing
    ENV_VAR with the value in the .env file. Raises an exception
    if the ENV_VAR is not found
    """
    for m in re.finditer(r"\${(\w+)}", input_str):
        var = m.group(1)
        try:
            input_str = re.sub(r"\${" + var + "}", cfg.get(var), input_str)
        except UndefinedValueError:
            raise ValueError(f"Invalid env var {m.group(1)} in {input_str}")

    return input_str
