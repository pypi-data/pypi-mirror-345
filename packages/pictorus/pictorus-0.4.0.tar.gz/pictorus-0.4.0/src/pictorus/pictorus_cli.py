#!/usr/bin/env python3

""" CLI entrypoint for pictorus device manager """
import argparse
import platform
import socket
import sys
from urllib.parse import urljoin
import shutil
import os
from enum import Enum
import json
from typing import Union
import requests
from pictorus.config import API_PREFIX, PICTORUS_ENV, Config, Environment, delete_app_manifest
from pictorus.constants import PICTORUS_SERVICE_NAME
from pictorus.daemons.launchd import Launchd
from pictorus.daemons.sudosystemd import SudoSystemd
from pictorus.daemons.systemd import Systemd

config = Config()

DEFAULT_AUTH_ERROR = "Unable to authenticate with pictorus"


class TextFormat(Enum):
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"


def printf(message: str, fmt: TextFormat):
    print(f"{fmt.value}{message}{TextFormat.ENDC.value}")


def configure_additional_settings():
    """Configure any additional settings that require user input"""
    # Disabling this prompt for now, if users want to opt out of auto updates they can
    # edit the config file directly. We are still making a lot of breaking changes to the API,
    # so better to keep people up-to-date
    config.auto_update = True
    config.use_prerelease = PICTORUS_ENV != Environment.PROD


def configure(args: argparse.Namespace):
    """Configure the device manager"""
    configure_device(token=args.token)
    setup_device_manager()
    configure_additional_settings()


def setup_device_manager():
    """Setup and start the device manager service"""
    print("Setting up device manager service")
    bin_path = shutil.which("pictorus-device-manager")
    if not bin_path:
        printf("Unable to set up device manager: executable missing", TextFormat.WARNING)
        return

    operating_system = os.uname().sysname
    if operating_system == "Darwin":
        daemon = Launchd()

        if not shutil.which("launchctl"):
            printf("Unable to set up device manager: launchctl not found", TextFormat.WARNING)
            return
    elif operating_system == "Linux":
        if os.getuid() == 0:  # Running as root
            daemon = SudoSystemd()
        else:
            daemon = Systemd()

        if not shutil.which("systemctl"):
            printf("Unable to set up device manager: systemctl not found", TextFormat.WARNING)
            return
    else:
        printf("Unsupported operating system", TextFormat.FAIL)
        return

    daemon.create_service(
        PICTORUS_SERVICE_NAME,
        "Service to manage Pictorus apps",
        bin_path,
    )
    printf("Configured device manager service", TextFormat.OKGREEN)


def try_device_configuration(
    device_name: str,
    system_data: dict,
    token: str,
) -> bool:
    """Try to configure the device"""
    if not token:
        raise ValueError("Access token must be provided")

    res = requests.post(
        urljoin(API_PREFIX, "v2/devices"),
        json={
            "name": device_name,
            "system": system_data,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    if not res.ok:
        try:
            message = res.json().get("message", DEFAULT_AUTH_ERROR)
        except json.JSONDecodeError:
            message = DEFAULT_AUTH_ERROR

        printf(f"Failed to configure device: {message}", TextFormat.FAIL)
        return False

    config.store_config(res.json())
    return True


def configure_device(token: Union[str, None] = None):
    """Configure this device to connect to pictorus"""
    if not config.is_empty():
        confirm = input(
            "It looks like this device is already configured."
            " Would you like to overwrite it [y/N]? "
        )
        if confirm.lower() != "y":
            printf("Skipping device registration", TextFormat.OKCYAN)
            return

        # Delete the existing app manifest since a reconfigure should remove
        # any previous targets
        printf("Deleting existing app manifest", TextFormat.OKCYAN)
        delete_app_manifest()

    hostname = socket.gethostname()
    device_name = input(f"Device Name [{hostname}]: ")
    device_name = device_name or hostname

    system_data = {
        "platform": platform.platform(),
        "system": platform.system(),
        "machine": platform.machine(),
    }

    token = token or input("Enter access token for pictorus: ")
    if not try_device_configuration(device_name, system_data, token):
        raise SystemExit(1)

    printf(f"Successfully configured device: {device_name}", TextFormat.OKGREEN)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Pictorus device manager")
    subparsers = parser.add_subparsers()

    parser_config = subparsers.add_parser("configure", help="Configure this device")
    parser_config.add_argument(
        "--token",
        help="Authentication token. If not provided, you will be prompted to enter it",
    )
    parser_config.set_defaults(func=configure)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
