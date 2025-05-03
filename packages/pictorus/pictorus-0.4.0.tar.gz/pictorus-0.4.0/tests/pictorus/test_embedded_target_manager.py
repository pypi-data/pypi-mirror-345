import json
from unittest import TestCase
from unittest.mock import ANY, MagicMock, patch, Mock

import pytest
import responses
from awscrt import mqtt

from pictorus.command import CmdType, Command, DeployTarget
from pictorus.exceptions import CommandError
from pictorus.target_manager import CommandCtxt
from pictorus.target_state import TargetState
from pictorus.embedded_target_manager import EmbeddedTargetManager
from pictorus.telemetry_manager import TelemetryManager
from pictorus.config import Config
from ..utils import expected_bin_path, setup_update_cmd, wait_for_condition

from pyocd.core.exceptions import ProbeError

LOG_LINES = [
    b"[INFO] - foo",
    b"[WARN] - bar",
    b"[DEBUG] - baz",
    b"Nonsense",
]
config = Config()


def basic_update_command(target_data: dict):
    return setup_update_cmd(
        version_url="http://foo.bar/baz",
        params_url="",
        build_id="newfoo",
        params_hash="",
        target_data=target_data,
    )


@patch("pictorus.embedded_target_manager.ConnectHelper.choose_probe", new=Mock())
@patch("pictorus.target_manager.os.makedirs", new=Mock())
@patch("pictorus.target_manager.os.chmod", new=Mock())
@patch("pictorus.embedded_target_manager.EmbeddedTargetManager._start_app_with_logging")
@patch("pictorus.embedded_target_manager.is_pack_target_available", return_value=True)
@patch("pictorus.embedded_target_manager.ConnectHelper.session_with_chosen_probe")
@patch("pictorus.embedded_target_manager.FileProgrammer")
class TestEmbeddedTargetManager(TestCase):
    @responses.activate
    def test_successful_deploy(self, m_prog, m_session, _, m_start):
        ocd_target = "stm32f4disco"
        target_id = "foo"
        target_data = {"id": target_id, "type": "embedded", "options": {"ocd_target": ocd_target}}
        update_app_cmd, expected_target_state = basic_update_command(target_data)

        target_mgr = EmbeddedTargetManager(
            DeployTarget(target_data), TargetState({}), Mock(), Mock(), Mock()
        )
        with patch("builtins.open"):
            target_mgr.handle_command(update_app_cmd)

        m_session.assert_called_once_with(
            blocking=False,
            return_first=True,
            target_override=ocd_target,
            connect_mode="attach",
        )
        m_prog.return_value.program.assert_called_once_with(
            expected_bin_path(target_id), file_format="elf"
        )
        assert target_mgr.target_state_data == expected_target_state.to_dict()
        m_start.assert_not_called()

    @responses.activate
    def test_failed_deploy_unconnected(self, m_prog, m_session, _, __):
        m_session.return_value = None

        ocd_target = "stm32f4disco"
        target_data = {"id": "foo", "type": "embedded", "options": {"ocd_target": ocd_target}}
        update_app_cmd, expected_target_state = basic_update_command(target_data)

        target_mgr = EmbeddedTargetManager(
            DeployTarget(target_data), TargetState({}), Mock(), Mock(), Mock()
        )
        with patch("builtins.open"), pytest.raises(CommandError):
            target_mgr.handle_command(update_app_cmd)

        m_session.assert_called_once_with(
            blocking=False,
            return_first=True,
            target_override=ocd_target,
            connect_mode="attach",
        )
        m_prog.assert_not_called()

        expected_target_state.error_log = {
            "err_type": "TargetConnectionError",
            "message": "Failed to connect to target. Make sure it is connected and powered on.",
        }
        assert target_mgr.target_state_data == expected_target_state.to_dict()

    @responses.activate
    def test_failed_deploy_failed_flash(self, m_prog, m_session, _, __):
        m_prog.return_value.program.side_effect = ProbeError

        ocd_target = "stm32f4disco"
        target_id = "foo"
        target_data = {"id": target_id, "type": "embedded", "options": {"ocd_target": ocd_target}}
        update_app_cmd, expected_target_state = basic_update_command(target_data)

        target_mgr = EmbeddedTargetManager(
            DeployTarget(target_data), TargetState({}), Mock(), Mock(), Mock()
        )
        with patch("builtins.open"), pytest.raises(ProbeError):
            target_mgr.handle_command(update_app_cmd)

        m_session.assert_called_once_with(
            blocking=False,
            return_first=True,
            target_override=ocd_target,
            connect_mode="attach",
        )

        m_prog.return_value.program.assert_called_once_with(
            expected_bin_path(target_id), file_format="elf"
        )

        expected_target_state.error_log = {
            "err_type": "UnknownError",
            "message": 'Command failed: ',
        }
        assert target_mgr.target_state_data == expected_target_state.to_dict()

    @responses.activate
    def test_auto_selects_target_name(self, m_prog, m_session, _, __):
        ocd_target = "stm32f45678"
        target_id = "foo"
        # No OCD target specified in the target data
        target_data = {"id": target_id, "type": "embedded", "options": {}}
        update_app_cmd, expected_target_state = basic_update_command(target_data)

        target_mgr = EmbeddedTargetManager(
            DeployTarget(target_data), TargetState({}), Mock(), Mock(), Mock()
        )
        with patch("builtins.open"), patch(
            "pictorus.embedded_target_manager.ConnectHelper.choose_probe"
        ) as m_probe:
            # Probe lookup returns a target name
            m_probe.return_value.associated_board_info.target = ocd_target
            target_mgr.handle_command(update_app_cmd)

        m_session.assert_called_once_with(
            blocking=False,
            return_first=True,
            target_override=ocd_target,
            connect_mode="attach",
        )
        m_prog.return_value.program.assert_called_once_with(
            expected_bin_path(target_id), file_format="elf"
        )
        assert target_mgr.target_state_data == expected_target_state.to_dict()

    @responses.activate
    def test_installs_missing_target(self, m_prog, m_session, m_target_avail, _):
        # Target is not installed
        m_target_avail.return_value = False

        ocd_target = "stm32f4disco"
        target_id = "foo"
        target_data = {"id": target_id, "type": "embedded", "options": {"ocd_target": ocd_target}}
        update_app_cmd, expected_target_state = basic_update_command(target_data)

        target_mgr = EmbeddedTargetManager(
            DeployTarget(target_data), TargetState({}), Mock(), Mock(), Mock()
        )
        with patch("builtins.open"), patch(
            "pictorus.embedded_target_manager.cp.Cache"
        ) as m_cache, patch("pictorus.embedded_target_manager.futures.wait"):
            cache = m_cache.return_value
            cache.index = {ocd_target: "bar"}
            packs = ["baz"]
            cache.packs_for_devices.return_value = packs

            target_mgr.handle_command(update_app_cmd)
            cache.download_pack_list.assert_called_once_with(packs)

        m_session.assert_called_once_with(
            blocking=False,
            return_first=True,
            target_override=ocd_target,
            connect_mode="attach",
        )
        m_prog.return_value.program.assert_called_once_with(
            expected_bin_path(target_id), file_format="elf"
        )
        assert target_mgr.target_state_data == expected_target_state.to_dict()

    @patch.object(TelemetryManager, "LOG_BATCH_SIZE", len(LOG_LINES) - 1)
    def test_log_data(self, _, __, ___, ____):
        mock_up_chan = MagicMock()
        is_first_call = True

        def mock_read():
            nonlocal is_first_call
            if is_first_call:
                is_first_call = False
                return b"\n".join(LOG_LINES)

            return b""

        mock_up_chan.read.side_effect = mock_read

        mqtt_connection = MagicMock(spec=mqtt.Connection)
        build_hash = "abcdef"
        target_state = TargetState({"run_app": False, "build_hash": build_hash})

        target_id = "foo"
        ocd_target = "stm32f4disco"
        target = DeployTarget(
            {"id": target_id, "type": "embedded", "options": {"ocd_target": ocd_target}}
        )
        mgr = EmbeddedTargetManager(target, target_state, Mock(), mqtt_connection, Mock())
        set_ttl_cmd = Command(
            {
                "type": CmdType.SET_TELEMETRY_TLL.value,
                "data": {"ttl_s": 60},
                "target_id": target_id,
            }
        )
        mgr.handle_command(CommandCtxt(set_ttl_cmd))
        mgr._start_logging(mock_up_chan)
        wait_for_condition(lambda: mqtt_connection.publish.call_count > 0)
        mgr._stop_logging()

        mqtt_connection.publish.assert_called_once_with(
            topic=f"$aws/rules/log_ingest/logs/pictorus/{config.client_id}",
            payload=ANY,
            qos=mqtt.QoS.AT_MOST_ONCE,
        )
        expected_payload = [
            {
                "timestamp": ANY,
                "message": json.dumps(
                    {
                        "level": "info",
                        "message": "foo",
                        "device_id": config.client_id,
                    }
                ),
            },
            {
                "timestamp": ANY,
                "message": json.dumps(
                    {
                        "level": "warning",
                        "message": "bar",
                        "device_id": config.client_id,
                    }
                ),
            },
            {
                "timestamp": ANY,
                "message": json.dumps(
                    {
                        "level": "debug",
                        "message": "baz",
                        "device_id": config.client_id,
                    }
                ),
            },
            {
                "timestamp": ANY,
                "message": json.dumps({"message": "Nonsense", "device_id": config.client_id}),
            },
        ]
        actual_payload = json.loads(mqtt_connection.publish.call_args[1]["payload"])
        assert actual_payload == expected_payload
