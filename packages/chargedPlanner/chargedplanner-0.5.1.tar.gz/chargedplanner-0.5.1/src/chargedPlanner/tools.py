import os
import sys

from pathlib import Path

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)


def is_running_under_pytest():
    return "PYTEST_CURRENT_TEST" in os.environ

def get_config_filePath() -> Path :

    user_config_path = os.path.expanduser("~/.config/chargedPlanner/config.json")
    if os.path.exists(user_config_path):
        return Path(user_config_path)

    else:
        from colorama import init, Fore

        init(autoreset=True)
        print(
            Fore.RED
            + "Please add your own config.json in : ~/.config/chargedPlanner/config.json"
        )
        print(
            "local config.json will be used in the meanwhile : "
            + current_dir
            + "/config.json"
        )
        return Path(current_dir + "/data/config.json")

