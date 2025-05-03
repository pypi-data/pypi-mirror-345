"""
Various nornir-netbox inventory filters that are relevant to our interests
"""

import re


def routers_filter(host):
    """
    Netbox roles that indicate a router
    """
    return host.data["role"]["slug"] in [
        "core",
        "bin",
        "data-center",
        "distribution",
        "security",
        # ilab roles
        "pe",
        "agg",
        "bgw",
        "ngfw",
        "legacy-bin",
        "legacy-core",
        "legacy-data-center",
        "legacy-distribution",
    ]


def mpls_filter(host):
    """
    Netbox roles for devices that run mpls
    """

    return host.data["role"]["slug"] in [
        "core",
        "pe",
        # ilab roles
        "legacy-core",
        "legacy-data-center",
        "legacy-distribution",
    ]


def vxlan_filter(host):
    """
    Netbox roles for vxlan devices - note vxlan
    devices are easier to match based on their hostname
    than their role
    """
    return bool(re.match(r"(pe|bgw|leaf|dl)-", host.name))


def non_security_filter(host):
    """
    All routers and switches (but not firewalls)
    """
    return host.data["role"]["slug"] != "security"


def active_filter(host):
    """Active host filter"""
    return host.data["status"]["value"] == "active"
