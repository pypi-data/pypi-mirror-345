from datetime import datetime, timedelta, timezone
import json
import os
from dataclasses import asdict
from typing import List

from awscrt import mqtt

from .constants import LogMessage
from .config import Config
from .date_utils import utc_timestamp_ms
from .logging_utils import get_logger
from .local_server import COMMS

try:
    from backports.datetime_fromisoformat import MonkeyPatch  # pyright: ignore
    # Patch fromisoformat for Python < 3.7
    MonkeyPatch.patch_fromisoformat()
except ImportError:
    pass

logger = get_logger()
config = Config()


def get_basic_ingest_topic(rule_name: str, topic: str):
    """Get the basic ingest topic for a given rule and base topic"""
    return os.path.join("$aws/rules/", rule_name, topic)


class TelemetryManager:
    """
    Class for managing telemetry from a running pictorus app.
    This class is responsible for communication between the app and device manager,
    as well as publishing telemetry to the backend at the correct interval
    """

    TELEM_PUBLISH_INTERVAL_MS = 100
    MAX_LOG_INTERVAL_MS = 1000
    LOG_BATCH_SIZE = 100

    def __init__(
        self,
        mqtt_connection: mqtt.Connection,
    ):
        self._build_id = ""
        self._message_topic = get_basic_ingest_topic(
            "app_telemetry_test",
            f"dt/pictorus/{config.client_id}/telem",
        )
        self._log_topic = get_basic_ingest_topic(
            "log_ingest",
            f"logs/pictorus/{config.client_id}",
        )
        self._mqtt_connection = mqtt_connection
        self._last_publish_time = datetime.now(timezone.utc)
        self._ttl_dt = datetime.now(timezone.utc)
        # TODO: This should come from config
        self._publish_interval = timedelta(milliseconds=self.TELEM_PUBLISH_INTERVAL_MS)

        self._log_entries: List[LogMessage] = []
        self._last_log_transmit = datetime.now(timezone.utc)

    def set_ttl(self, ttl_s: int):
        """Set the telemetry TTL"""
        self._ttl_dt = datetime.now(timezone.utc) + timedelta(seconds=ttl_s)
        logger.debug("Updated TTL to: %s (UTC)", self._ttl_dt)

    def reset_log_start_time(self):
        self._last_log_transmit = datetime.now(timezone.utc)

    def set_build_id(self, build_id: str):
        """Set the build ID for the telemetry"""
        self._build_id = build_id

    def add_log_entries(self, log_entries: List[LogMessage]):
        COMMS.add_logs(log_entries)
        self._log_entries.extend(log_entries)

    def check_publish_logs(self, date_now: datetime):
        publish_interval_elapsed = date_now - self._last_log_transmit >= timedelta(
            milliseconds=self.MAX_LOG_INTERVAL_MS
        )
        should_publish = len(self._log_entries) >= self.LOG_BATCH_SIZE or (
            publish_interval_elapsed and len(self._log_entries) > 0
        )
        if should_publish:
            self.publish_logs(date_now)

    def publish_logs(self, date_now: datetime):
        ttl_active = self.is_ttl_active(date_now)
        if not self._log_entries or not ttl_active:
            logger.debug(
                "No logs to publish or TTL expired: %s, (%s)", ttl_active, len(self._log_entries)
            )
            # Make sure we're not accumulating too many logs
            self._log_entries = self._log_entries[-self.LOG_BATCH_SIZE :]
            return

        logger.debug("Publishing %s logs", len(self._log_entries))
        self._mqtt_connection.publish(
            topic=self._log_topic,
            payload=json.dumps(list(map(asdict, self._log_entries))),
            qos=mqtt.QoS.AT_MOST_ONCE,
        )

        self._log_entries = []
        self._last_log_transmit = date_now

    def _publish_app_telem(self, app_data: dict, utc_timestamp: int):
        # any value in the dict that is a list (or list of lists) must be converted to a string
        # before being sent to MQTT
        for key, value in app_data.items():
            if isinstance(value, list):
                # Convert list to string
                app_data[key] = json.dumps(value)

        publish_data = {
            "data": app_data,
            "time_utc": utc_timestamp,
            "meta": {"build_id": self._build_id},
        }
        logger.debug("Publishing most recent app data: %s", publish_data)

        json_publish_data = json.dumps(publish_data)

        self._mqtt_connection.publish(
            topic=self._message_topic,
            payload=json_publish_data,
            qos=mqtt.QoS.AT_LEAST_ONCE,
        )

    def add_telem_sample(self, data: dict, date_now: datetime):
        utc_timestamp = utc_timestamp_ms(dt=date_now)
        ttl_active = self.is_ttl_active(date_now)
        # Currently this just throws away data unless we're publishing.
        # Possible we might want to batch and upload everything in the future.
        if ttl_active and date_now - self._last_publish_time >= self._publish_interval:
            self._publish_app_telem(data, utc_timestamp)
            self._last_publish_time = date_now

        data["utctime"] = utc_timestamp
        COMMS.update_telem(data)

    def is_ttl_active(self, date_now: datetime):
        return date_now < self._ttl_dt
