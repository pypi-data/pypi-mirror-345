from typing import Mapping, Union
from .constants import EMPTY_ERROR

ErrorLogType = Mapping[str, Union[str, None]]


class TargetState:
    def __init__(self, data: dict):
        self.error_log: ErrorLogType = EMPTY_ERROR.copy()
        self.run_app = data.get("run_app", False)
        self.build_hash = data.get("build_hash", "")
        self.params_hash = data.get("params_hash", "")

    def to_dict(self):
        return {
            "run_app": self.run_app,
            "build_hash": self.build_hash,
            "params_hash": self.params_hash,
            "error_log": self.error_log,
        }
