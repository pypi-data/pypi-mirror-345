from unittest import TestCase
from unittest.mock import MagicMock

from awscrt import mqtt

from pictorus.telemetry_manager import TelemetryManager, COMMS
from pictorus.config import Config

config = Config()


class TestTelemetryManager(TestCase):
    def setUp(self):
        COMMS.clear_telem()

    def test_set_ttl(self):
        mqtt_connection = MagicMock(spec=mqtt.Connection)
        telemetry_manager = TelemetryManager(mqtt_connection)
        telemetry_manager.set_ttl(60)
        assert telemetry_manager._ttl_dt is not None
