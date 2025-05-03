from unittest import TestCase
from unittest.mock import patch, Mock, MagicMock, ANY, mock_open
import time
import json

from awscrt import mqtt
from awsiot.iotshadow import ShadowDeltaUpdatedEvent
import responses

from pictorus.config import Config
from pictorus.app_manager import AppManager, COMMS
from pictorus.command import CmdType, Command
from pictorus.target_manager import CommandCtxt
from ..utils import wait_for_condition

config = Config()

ADDR_DATA = ("127.0.0.1", 1234)
BUILD_HASH = "bob"


@patch("pictorus.app_manager.mqtt_connection_builder.mtls_from_bytes")
@patch(
    "pictorus.app_manager.load_app_manifest",
    new=Mock(return_value={"build_hash": BUILD_HASH, "params_hash": "bar"}),
)
@patch("pictorus.app_manager.iotshadow.IotShadowClient", new=Mock())
@patch("pictorus.app_manager.create_server", new=Mock())
class TestAppManager(TestCase):
    def setUp(self):
        self.start_time = time.time()
        config.store_config(
            {
                "clientId": "foo_device",
                "mqttEndpoint": "foo_endpoint",
                "credentials": {
                    "certificatePem": "foo_cert",
                    "certificateCa": "foo_ca",
                    "keyPair": {
                        "PrivateKey": "foo_key",
                    },
                },
            }
        )

    @patch("pictorus.app_manager.iotshadow.UpdateShadowRequest")
    def test_starts_and_stops_app_based_on_shadow(self, m_shadow_req, _):
        target_id = "foo"
        target_data = {"id": target_id, "type": "process"}
        target_state_data = {"build_hash": BUILD_HASH}
        target_states = {target_id: target_state_data}
        manifest_data = {"targets": [target_data], "target_states": target_states}

        target_mgr = MagicMock()
        target_mgr.target_data = {"id": target_id, "type": "process"}
        target_mgr.target_state_data = target_state_data

        m_write = mock_open()
        with AppManager(Mock()) as mgr, patch("builtins.open", m_write):
            mgr._target_managers = {target_id: target_mgr}

            # Start the app
            mgr._on_shadow_delta_updated(
                ShadowDeltaUpdatedEvent(state={"target_states": {target_id: {"run_app": True}}})
            )
            target_mgr.handle_command.assert_called_once_with(
                CommandCtxt(
                    Command(
                        {
                            "type": CmdType.RUN_APP.value,
                            "data": {"run_app": True},
                            "target_id": target_id,
                        }
                    ),
                )
            )
            handle = m_write()
            handle.write.assert_called_once_with(json.dumps(manifest_data))
            assert m_shadow_req.mock_calls[1][2]["state"].reported["target_states"] == target_states

            # Stop the app
            target_mgr.handle_command.reset_mock()
            mgr._on_shadow_delta_updated(
                ShadowDeltaUpdatedEvent(state={"target_states": {target_id: {"run_app": False}}})
            )
            target_mgr.handle_command.assert_called_once_with(
                CommandCtxt(
                    Command(
                        {
                            "type": CmdType.RUN_APP.value,
                            "data": {"run_app": False},
                            "target_id": target_id,
                        }
                    ),
                )
            )

    @patch("pictorus.app_manager.iotshadow.UpdateShadowRequest")
    def test_run_deleted_target_removes_from_desired_state(self, m_shadow_req, _):
        target_id = "foo"

        target_mgr = MagicMock()
        with AppManager(Mock()) as mgr:
            # Attempt to start an app for a target that doesn't exist
            mgr._on_shadow_delta_updated(
                ShadowDeltaUpdatedEvent(state={"target_states": {target_id: {"run_app": True}}})
            )
            target_mgr.handle_command.assert_not_called()
            assert m_shadow_req.mock_calls[1][2]["state"].desired["target_states"] == {
                target_id: None
            }

    @patch("pictorus.app_manager.iotshadow.UpdateShadowRequest")
    def test_starts_and_stops_app_based_on_thread_comms(self, m_shadow_req, _):
        target_id = "foo"
        target_data = {"id": target_id, "type": "process"}
        target_state_data = {"build_hash": BUILD_HASH}
        target_states = {target_id: target_state_data}
        manifest_data = {"targets": [target_data], "target_states": target_states}

        target_mgr = MagicMock()
        target_mgr.target_data = {"id": target_id, "type": "process"}
        target_mgr.target_state_data = target_state_data

        m_write = mock_open()
        with AppManager(Mock()) as mgr, patch("builtins.open", m_write):
            mgr._target_managers = {target_id: target_mgr}

            # Start the app
            cmd_data = {
                "type": CmdType.RUN_APP.value,
                "data": {"run_app": True},
                "target_id": target_id,
            }
            COMMS.add_command(cmd_data)
            wait_for_condition(lambda: COMMS.commands.qsize() == 0)
            target_mgr.handle_command.assert_called_once_with(CommandCtxt(Command(cmd_data)))
            handle = m_write()
            handle.write.assert_called_once_with(json.dumps(manifest_data))
            assert m_shadow_req.mock_calls[1][2]["state"].reported["target_states"] == target_states

            # Stop the app
            target_mgr.handle_command.reset_mock()
            cmd_data = {
                "type": CmdType.RUN_APP.value,
                "data": {"run_app": False},
                "target_id": target_id,
            }
            COMMS.add_command(cmd_data)
            wait_for_condition(lambda: COMMS.commands.qsize() == 0)
            target_mgr.handle_command.assert_called_once_with(CommandCtxt(Command(cmd_data)))

    @responses.activate
    @patch("pictorus.app_manager.run")
    def test_set_upload_logs(self, m_run, m_mqtt_builder):
        upload_url = "https://example.com/upload"

        upload_logs_cmd = json.dumps(
            {
                "type": CmdType.UPLOAD_LOGS.value,
                "data": {
                    "upload_dest": {"url": upload_url, "fields": {"foo": "bar"}},
                    "line_count": 500,
                },
                # Kind of dumb, but we require a target to be set.
                # Maybe should be optional for commands that aren't target specific
                "target": {
                    "id": "",
                    "type": "process",
                },
            }
        )
        responses.add(responses.POST, upload_url, body="")
        m_mqtt = m_mqtt_builder.return_value
        with AppManager(Mock()) as mgr:
            mgr._on_retained_cmd("ret", upload_logs_cmd.encode("utf-8"))
            m_run.assert_called_once_with(
                ["journalctl", "-u", "pictorus", "-n", "500", "--no-pager"],
                check=True,
                stdout=ANY,
            )
            m_mqtt.publish.assert_called_once_with(
                topic="ret",
                payload="",
                qos=ANY,
                retain=True,
            )

    @patch("pictorus.app_manager.iotshadow.UpdateShadowRequest")
    def test_resubscribes_to_topics_and_republishes_shadow_state_on_reconnect(
        self, m_shadow_req, _
    ):
        m_connection = Mock()
        with AppManager(Mock()) as mgr:
            # Shadow gets published on init, so clear the initial call
            m_shadow_req.reset_mock()
            mgr._on_connection_resumed(m_connection, mqtt.ConnectReturnCode.ACCEPTED, False)
            m_connection.resubscribe_existing_topics.assert_called_once()
            m_shadow_req.assert_called_once()
