import os
import time
from typing import Callable

import responses

from pictorus.config import APP_ASSETS_DIR
from pictorus.command import Command, CmdType
from pictorus.target_manager import CommandCtxt
from pictorus.target_state import TargetState


def wait_for_condition(condition: Callable[[], bool], timeout=1):
    start = time.time()
    while not condition():
        if time.time() - start > timeout:
            raise TimeoutError()

        time.sleep(0.1)


def expected_assets_dir(target_id: str):
    return os.path.join(APP_ASSETS_DIR, target_id)


def expected_error_log_path(target_id: str):
    return os.path.join(expected_assets_dir(target_id), "pictorus_errors.json")


def expected_bin_path(target_id: str):
    return os.path.join(expected_assets_dir(target_id), "pictorus_managed_app")


def setup_update_cmd(
    version_url: str, params_url: str, build_id: str, params_hash: str, target_data: dict
):
    responses.add(responses.GET, version_url, body="")
    responses.add(responses.GET, params_url, body="")

    version_data = {
        "build_hash": build_id,
        "app_bin_url": version_url,
        "params_hash": params_hash,
        "params_url": params_url,
    }

    expected_target_state = TargetState({"build_hash": build_id, "params_hash": params_hash})
    cmd_data = {"type": CmdType.UPDATE_APP.value, "data": version_data, "target": target_data}

    return CommandCtxt(Command(cmd_data)), expected_target_state
