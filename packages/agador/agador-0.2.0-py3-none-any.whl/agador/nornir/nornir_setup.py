from typing import Optional
from decouple import Config

from nornir import InitNornir
from nornir.core import Nornir

from ..credentials import update_nornir_credentials
from .logging import configure_nornir_logging
from .connection_options import configure_connection_options

NETBOX_DEVICE_ROLES = [
    "av",
    "access-layer-switch",
    "bin",
    "core",
    "data-center",
    "distribution",
    "out-of-band",
    "security",
    "umd",
    "legacy-bin",
    "legacy-core",
    "legacy-distribution",
    "voice",
]

NETBOX_ILAB_DEVICE_ROLES = [
    "access",
    "agg",
    "bgw",
    "core",
    "data-center",
    "distribution",
    "legacy-bin",
    "legacy-core",
    "legacy-data-center",
    "legacy-distribution",
    "ngfw",
    "pe",
]


def nornir_setup(
    cfg: Config,
    log_level: str = "DEBUG",
    log_globally: Optional[bool] = False,
    log_to_console: Optional[bool] = False,
    device_filter: Optional[str] = None,
    role_filter: Optional[str] = None,
) -> Nornir:
    """
    Initializes Nornir to point at netbox, and to only care about active
    devices tied to a specific subset of device roles.
    Sets up logging. Populates default and custom passwords from cyberark. Returns
    customized Nornir instance
    """

    logfile = cfg.get("LOG_DIR") + "/agador.log"

    configure_nornir_logging(log_level, log_globally, logfile, log_to_console)

    nb_url = cfg.get("NB_URL")

    filter_params = {"status": "active", "has_primary_ip": "True"}

    # Restrict what the netbox inventory plugin pulls if it was indicated
    # on the CLI
    if device_filter:
        filter_params["name"] = device_filter
    elif role_filter:
        filter_params["role"] = [role_filter]
    elif "ilab" in nb_url:
        filter_params["role"] = NETBOX_ILAB_DEVICE_ROLES
    else:
        filter_params["role"] = NETBOX_DEVICE_ROLES

    # Nornir initialization
    nr = InitNornir(
        runner={
            "plugin": "multiprocess",
            "options": {
                "num_workers": int(cfg.get("NUM_WORKERS")),
            },
        },
        inventory={
            "plugin": "NetBoxInventory2",
            "options": {
                "nb_url": nb_url,
                "nb_token": cfg.get("NB_TOKEN"),
                "filter_parameters": filter_params,
                "ssl_verify": False,
            },
        },
        logging={
            "enabled": False,
        },
    )

    update_nornir_credentials(nr, cfg.get("CYBERARK_ENV_FILE"))
    configure_connection_options(nr)

    return nr
