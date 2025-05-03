""" Logger utilities """

import logging
from datetime import datetime
from pictorus.constants import LogMessage
import re
from pictorus.date_utils import utc_timestamp_ms
import json

logging.basicConfig(format="%(asctime)s %(message)s")

# This is duplicated in the backend. Not sure if we want to do this here or
# just upload the raw logs and parse them in the backend.
LOG_PATTERN = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+(?:Z|[+-]\d{2}:\d{2})?) \[(?P<log_level>\w+)\] - (?P<message>.*)"  # noqa: E501
)

# The embedded log pattern for logging messages lacks the timestamp
EMBEDDED_LOG_PATTERN = re.compile(
    r"\[(?P<log_level>\w+)\] - (?P<message>.*)"  # noqa: E501
)


def get_logger():
    """Get logger with common formatting"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    return logger


def format_log_level(log_level: str):
    if log_level == "WARN":
        log_level = "warning"

    return log_level.lower()


def parse_log_entry(line: str,
                    date_now: datetime,
                    client_id: str,
                    embedded_log: bool = False) -> LogMessage:
    # The Linux log expects utc time as the first element, but this isn't available on
    # embedded systems, so package the date_now instead.
    # See initialize_logging() in udp_data_logger.rs in the main Pictorus repo
    # for more information about log formatting.
    match = EMBEDDED_LOG_PATTERN.match(line) if embedded_log else LOG_PATTERN.match(line)

    if match:
        log_entry = match.groupdict()
        timestamp = log_entry["timestamp"] if embedded_log is False else date_now.isoformat()
        # Older versions of datetime don't support the Z suffix
        if timestamp.endswith("Z"):
            timestamp = timestamp[:-1] + "+00:00"

        dt = datetime.fromisoformat(timestamp)
        return LogMessage(
            timestamp=utc_timestamp_ms(dt),
            message=json.dumps(
                {
                    "level": format_log_level(log_entry["log_level"]),
                    "message": log_entry["message"],
                    "device_id": client_id,
                }
            ),
        )

    return LogMessage(
        timestamp=utc_timestamp_ms(date_now),
        message=json.dumps({"message": line, "device_id": client_id}),
    )
