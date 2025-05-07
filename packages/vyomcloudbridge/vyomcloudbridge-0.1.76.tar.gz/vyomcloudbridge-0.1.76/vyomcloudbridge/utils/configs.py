import configparser
import os
import signal
import sys
from typing import Dict, Any
import json
from vyomcloudbridge.utils.logger_setup import setup_logger

logger = setup_logger(name=__name__, show_terminal=False)


class Configs:
    @staticmethod
    def get_machine_config() -> Dict[str, Any]:
        config = configparser.ConfigParser()
        config_path = "/etc/vyomcloudbridge/machine.conf"
        if os.path.exists(config_path):
            config.read(config_path)
            try:
                return {
                    "machine_id": int(config["MACHINE"]["machine_id"]),
                    "organization_id": int(config["MACHINE"]["organization_id"]),
                    "device_id": str(config["MACHINE"]["machine_model_type"])
                    + str(config["MACHINE"]["machine_id"]),
                }
            except (KeyError, ValueError):
                logger.error(f"Failed to parse configuration from {config_path}")
        logger.warning(
            f"Using default values because config file {config_path} was not found or is invalid"
        )
        return {
            "machine_id": "-",
            "organization_id": "-",
        }


def main():
    machine_config = Configs.get_machine_config()
    machine_id = machine_config.get("machine_id", "-") or "-"
    device_id = machine_config.get("device_id", "-") or "-"
    organization_id = machine_config.get("organization_id", "-") or "-"
    print("machine_id-", machine_id)
    print("device_id-", device_id)
    print("organization_id-", organization_id)


if __name__ == "__main__":
    main()
