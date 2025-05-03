from typing import Union
from enum import Enum

from .logging_utils import get_logger

logger = get_logger()


class DeployTargetType(Enum):
    """Supported deployment targets for pictorus apps"""

    PROCESS = "process"
    EMBEDDED = "embedded"


class CmdType(Enum):
    """Supported commands for the device command topic"""

    UPDATE_APP = "UPDATE_APP"
    SET_LOG_LEVEL = "SET_LOG_LEVEL"
    UPLOAD_LOGS = "UPLOAD_LOGS"
    SET_TELEMETRY_TLL = "SET_TELEMETRY_TTL"
    RUN_APP = "RUN_APP"


class DeployTarget:
    """Base class for command targets"""

    def __init__(self, data: dict):
        if "type" not in data or "id" not in data:
            logger.warning("Received invalid command target: %s", data)
            raise ValueError("Invalid command target")

        self.id = data["id"]
        self.type = DeployTargetType(data["type"])
        self.options = data.get("options", {})

    def to_dict(self):
        return {"id": self.id, "type": self.type.value, "options": self.options}


class Command:
    def __init__(self, data: dict):
        if "type" not in data or "data" not in data:
            logger.warning("Received invalid command: %s", data)
            raise ValueError("Invalid command")

        self.type = CmdType(data["type"])
        self.data = data["data"]

        # Targets can be passed in as a full object or just an id
        self.target_id: Union[str, None] = None
        if "target" in data:
            self.target_id = data["target"].get("id")
        else:
            self.target_id = data.get("target_id")

        if self.target_id is None:
            logger.warning("Received command with no target")
            raise ValueError("Invalid command")

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Command):
            return False

        return self.to_dict() == __value.to_dict()

    def to_dict(self):
        return {"type": self.type.value, "data": self.data, "target_id": self.target_id}
