from nornir.core import Nornir
from .credentials import CredentialMap


def update_nornir_credentials(nr: Nornir, cyberark_env_file: str):
    """
    Uses the credential map to update host credentials in this nornir instance
    """
    cred_map = CredentialMap(cyberark_env_file)
    cred_map.set_default_credentials(nr)
    for host in nr.inventory.hosts.values():
        cred_map.set_host_credentials(host)
