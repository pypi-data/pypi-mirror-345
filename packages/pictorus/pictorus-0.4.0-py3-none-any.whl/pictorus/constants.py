""" Common constants and enums """

from enum import Enum
from dataclasses import dataclass

PICTORUS_SERVICE_NAME = "pictorus"
THREAD_SLEEP_TIME_S = 0.1


JWT_PUB_KEY = "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0gBnoEVmDKWmtSH3+BgK\nr/tAfxlHpTJ5igsVFJOqzrorCfpE0JwFlMk6EjvMAWZ3kNkX7PhIqBRxPYQPK1pw\n6W0Wf6Ywox/ojUECTPD9/TTGqqRQSaumiw3SIDMNzBDwAUUYIEuynOv/575+tMM/\nh9a8f4EaQFqLUVZ7B+a21zwdLSx5Bg0YdsNYlF32jNM8cosB3AJ6IpbstSW3ox7d\nhUzWAE5qyPm1oF9Nw8WHk0iYaDgLqacX1TJePOf8gruhznzRADINw+TGIBBmnQEA\noAQ1i9UPOtZlduo5CKvARwtWPeT3jyxHppo4iaOo0ZCMeh8HU0VvL0vqklUuzu7u\n4QIDAQAB\n-----END PUBLIC KEY-----\n"  # noqa: E501
JWT_ALGORITHM = "RS256"


class AppLogLevel(Enum):
    """Log levels that can be set for pictorus apps"""

    OFF = "off"
    ERROR = "error"
    WARN = "warn"
    INFO = "info"
    DEBUG = "debug"


@dataclass
class LogMessage:
    timestamp: int
    message: str


EMPTY_ERROR = {
    "err_type": None,
    "message": None,
}
