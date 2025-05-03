from datetime import datetime, timezone
from subprocess import PIPE, STDOUT
from unittest import TestCase
from unittest.mock import ANY, MagicMock, patch, Mock, mock_open
import threading
import json

import responses
from awscrt import mqtt

from pictorus.constants import AppLogLevel, EMPTY_ERROR
from pictorus.local_server import COMMS
from pictorus.target_manager import CommandCtxt
from pictorus.proc_target_manager import ProcTargetManager
from pictorus.command import DeployTarget, Command, CmdType
from pictorus.target_state import TargetState
from pictorus.telemetry_manager import TelemetryManager
from pictorus.config import Config
from ..utils import (
    expected_assets_dir,
    expected_bin_path,
    expected_error_log_path,
    wait_for_condition,
    setup_update_cmd,
)


ADDR_DATA = ("127.0.0.1", 1234)
LOG_LINES = [
    b"2023-01-01T00:00:00.000Z [INFO] - foo",
    b"2023-01-01T00:00:01.000Z [WARN] - bar",
    b"2023-01-01T00:00:02.000Z [DEBUG] - baz",
    b"Nonsense",
]
config = Config()


def _assert_correct_app_start(
    mgr: ProcTargetManager, m_popen: Mock, target_id: str, log_level=AppLogLevel.INFO
):
    m_popen.assert_called_once_with(
        expected_bin_path(target_id),
        stdout=PIPE,
        stderr=STDOUT,
        env={
            "APP_PUBLISH_SOCKET": f"{ADDR_DATA[0]}:{ADDR_DATA[1]}",
            "APP_RUN_PATH": expected_assets_dir(target_id),
            "LOG_LEVEL": log_level.value,
        },
    )

    assert mgr._telem_listener_thread is not None
    assert mgr._telem_listener_thread.is_alive() is True

    assert mgr._logging_thread is not None
    # TODO: We currently mock the log behavior so the log thread will terminate immediately
    # assert mgr._logging_thread.is_alive() is True


def _assert_correct_app_stop(mgr: ProcTargetManager, m_popen: Mock):
    m_popen.assert_not_called()
    m_popen.return_value.terminate.assert_called_once()


def _mock_popen(m_popen: Mock):
    mock_proc = MagicMock()
    mock_proc.poll.return_value = 0
    m_popen.return_value = mock_proc


@patch("pictorus.target_manager.os.makedirs", new=Mock())
@patch("pictorus.target_manager.os.chmod", new=Mock())
@patch("pictorus.proc_target_manager._path_exists", return_value=True)
@patch("pictorus.proc_target_manager.Popen")
class TestProcTargetManager(TestCase):
    BUILD_HASH = "abc123"
    TARGET_ID = "foo"
    TARGET = DeployTarget({"id": TARGET_ID, "type": "process"})

    def setUp(self) -> None:
        socket_patch = patch("pictorus.proc_target_manager.socket.socket")
        m_socket = socket_patch.start()
        self.mock_socket = MagicMock()
        self.mock_socket.getsockname.return_value = ADDR_DATA
        self.mock_socket.recv.return_value = b""
        m_socket.return_value.__enter__.return_value = self.mock_socket
        self.addCleanup(socket_patch.stop)
        COMMS.clear_all()

        return super().setUp()

    def test_starts_app_on_entry(self, m_popen, _):
        _mock_popen(m_popen)
        target_state = TargetState({"run_app": True, "build_hash": self.BUILD_HASH})
        with ProcTargetManager(self.TARGET, target_state, Mock(), Mock(), Mock()) as mgr:
            # m_telem.return_value.start_listening.assert_called_once_with(self.BUILD_HASH)
            _assert_correct_app_start(mgr, m_popen, self.TARGET_ID)

        m_popen.return_value.terminate.assert_called_once()

    def test_does_not_start_app_on_entry(self, m_popen, _):
        target_state = TargetState({"run_app": False, "build_hash": self.BUILD_HASH})
        with ProcTargetManager(self.TARGET, target_state, Mock(), Mock(), Mock()):
            m_popen.assert_not_called()

        m_popen.return_value.terminate.assert_not_called()

    def test_starts_and_stops_app(self, m_popen, _):
        _mock_popen(m_popen)
        target_state = TargetState({"run_app": False, "build_hash": self.BUILD_HASH})
        with ProcTargetManager(self.TARGET, target_state, Mock(), Mock(), Mock()) as mgr:
            # Start the app
            start_app_cmd = Command(
                {
                    "type": CmdType.RUN_APP.value,
                    "data": {"run_app": True},
                    "target_id": self.TARGET_ID,
                }
            )
            cmd_ctxt = CommandCtxt(start_app_cmd)
            m_popen.reset_mock()
            mgr.handle_command(cmd_ctxt)
            _assert_correct_app_start(mgr, m_popen, self.TARGET_ID)

            # Calling start again should do nothing
            m_popen.reset_mock()
            mgr.handle_command(cmd_ctxt)
            m_popen.assert_not_called()

            # Stop the app
            stop_app_cmd = Command(
                {
                    "type": CmdType.RUN_APP.value,
                    "data": {"run_app": False},
                    "target_id": self.TARGET_ID,
                }
            )
            cmd_ctxt = CommandCtxt(stop_app_cmd)
            m_popen.reset_mock()
            mgr.handle_command(cmd_ctxt)
            _assert_correct_app_stop(mgr, m_popen)

    @responses.activate
    def test_starts_app_on_update(self, m_popen, _):
        _mock_popen(m_popen)
        new_build_id = "newfoo"
        update_app_cmd, expected_target_state = setup_update_cmd(
            version_url="http://foo.bar/baz",
            params_url="http://foo.bar/params.json",
            build_id=new_build_id,
            params_hash="newparams123",
            target_data=self.TARGET.to_dict(),
        )

        target_state = TargetState({"run_app": True, "build_hash": self.BUILD_HASH})
        with patch("builtins.open"), ProcTargetManager(
            self.TARGET, target_state, Mock(), Mock(), Mock()
        ) as mgr:
            m_popen.reset_mock()

            mgr.handle_command(update_app_cmd)
            _assert_correct_app_start(mgr, m_popen, self.TARGET_ID)

            expected_target_state.run_app = True
            assert mgr.target_state_data == expected_target_state.to_dict()

    def test_set_telemetry_ttl(self, _, __):
        ttl_s = 99
        set_ttl_cmd = Command(
            {
                "type": CmdType.SET_TELEMETRY_TLL.value,
                "data": {"ttl_s": ttl_s},
                "target_id": self.TARGET_ID,
            }
        )
        cmd_ctxt = CommandCtxt(set_ttl_cmd)
        target_state = TargetState({"run_app": False, "build_hash": self.BUILD_HASH})
        with ProcTargetManager(self.TARGET, target_state, Mock(), Mock(), Mock()) as mgr:
            assert mgr._telemetry_manager.is_ttl_active(datetime.now(timezone.utc)) is False
            mgr.handle_command(cmd_ctxt)
            assert mgr._telemetry_manager.is_ttl_active(datetime.now(timezone.utc)) is True

    def test_set_log_level(self, m_popen, __):
        _mock_popen(m_popen)
        log_level = AppLogLevel.DEBUG
        set_ttl_cmd = Command(
            {
                "type": CmdType.SET_LOG_LEVEL.value,
                "data": {"log_level": log_level.value},
                "target_id": self.TARGET_ID,
            }
        )
        cmd_ctxt = CommandCtxt(set_ttl_cmd)

        target_state = TargetState({"run_app": True, "build_hash": self.BUILD_HASH})
        with ProcTargetManager(self.TARGET, target_state, Mock(), Mock(), Mock()) as mgr:
            m_popen.reset_mock()
            mgr.handle_command(cmd_ctxt)
            _assert_correct_app_start(mgr, m_popen, self.TARGET_ID, log_level=log_level)

    @patch("pictorus.proc_target_manager.os.remove")
    def test_sets_error_from_file_on_unexpected_crash(self, m_remove, m_popen, __):
        app_complete = threading.Event()
        m_popen.return_value.wait.side_effect = app_complete.wait

        expected_err = {"err_type": "Foo", "message": "Bar"}
        target_state = TargetState({"run_app": True, "build_hash": self.BUILD_HASH})
        m_shadow_cb = Mock()
        with ProcTargetManager(
            self.TARGET, target_state, Mock(), Mock(), m_shadow_cb
        ) as mgr, patch("builtins.open", mock_open(read_data=json.dumps(expected_err))):
            # Error should get cleared on init
            wait_for_condition(lambda: m_shadow_cb.call_count == 1)
            assert mgr.target_state_data["error_log"] == EMPTY_ERROR
            app_complete.set()

            # Wait for app to get marked as stopped
            wait_for_condition(lambda: not mgr.app_is_running)

        m_remove.assert_called_once_with(expected_error_log_path(self.TARGET_ID))
        assert m_shadow_cb.call_count == 2
        assert mgr.target_state_data["error_log"] == expected_err

    @patch("pictorus.proc_target_manager.os.remove")
    def test_sets_default_error_on_unexpected_crash(self, m_remove, m_popen, m_exists):
        app_complete = threading.Event()
        m_popen.return_value.wait.side_effect = app_complete.wait

        m_exists.side_effect = lambda p: p != expected_error_log_path(self.TARGET_ID)

        target_state = TargetState({"run_app": True, "build_hash": self.BUILD_HASH})
        m_shadow_cb = Mock()
        with ProcTargetManager(self.TARGET, target_state, Mock(), Mock(), m_shadow_cb) as mgr:
            # Error should get cleared on init
            wait_for_condition(lambda: m_shadow_cb.call_count == 1)
            assert mgr.target_state_data["error_log"] == EMPTY_ERROR
            app_complete.set()

            # Wait for app to get marked as stopped
            wait_for_condition(lambda: not mgr.app_is_running)

        m_remove.assert_not_called()
        assert m_shadow_cb.call_count == 2
        assert mgr.target_state_data["error_log"] == ProcTargetManager.NO_LOG_ERROR

    def test_listen_for_telem(self, _, __):
        mqtt_connection = MagicMock(spec=mqtt.Connection)
        target_state = TargetState({"run_app": False, "build_hash": self.BUILD_HASH})
        mgr = ProcTargetManager(self.TARGET, target_state, Mock(), mqtt_connection, Mock())
        mgr._ready.wait(timeout=1)
        set_ttl_cmd = Command(
            {
                "type": CmdType.SET_TELEMETRY_TLL.value,
                "data": {"ttl_s": 60},
                "target_id": self.TARGET_ID,
            }
        )
        mgr.handle_command(CommandCtxt(set_ttl_cmd))

        # Send some data to the socket
        data = {"foo": 1.0}
        encoded_data = json.dumps(data).encode("utf-8")

        def mock_recv(*args, **kwargs):
            assert mgr._socket_data == ADDR_DATA
            # Hack to stop thread after one loop
            mgr._listen = False
            return encoded_data

        self.mock_socket.recv.side_effect = mock_recv

        # Start listening
        build_id = "test_build_id"
        mgr._start_listening(build_id)
        wait_for_condition(lambda: mqtt_connection.publish.call_count > 0)

        # Check that the data was received and processed
        expected_payload = {"data": data, "time_utc": ANY, "meta": {"build_id": build_id}}
        mqtt_connection.publish.assert_called_once_with(
            topic=f"$aws/rules/app_telemetry_test/dt/pictorus/{config.client_id}/telem",
            payload=ANY,
            qos=mqtt.QoS.AT_LEAST_ONCE,
        )
        actual_payload = json.loads(mqtt_connection.publish.call_args[1]["payload"])
        assert actual_payload == expected_payload

        telem = COMMS.get_telem(0, 60)
        assert telem == {"foo": [1.0], "utctime": [ANY]}

    @patch.object(TelemetryManager, "LOG_BATCH_SIZE", len(LOG_LINES))
    def test_log_data(self, m_popen, _):
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        mock_proc.stdout.readline.side_effect = LOG_LINES

        mqtt_connection = MagicMock(spec=mqtt.Connection)
        target_state = TargetState({"run_app": False, "build_hash": self.BUILD_HASH})
        mgr = ProcTargetManager(self.TARGET, target_state, Mock(), mqtt_connection, Mock())
        set_ttl_cmd = Command(
            {
                "type": CmdType.SET_TELEMETRY_TLL.value,
                "data": {"ttl_s": 60},
                "target_id": self.TARGET_ID,
            }
        )
        mgr.handle_command(CommandCtxt(set_ttl_cmd))
        mgr._listen = True
        mgr._start_logging(mock_proc)
        wait_for_condition(lambda: mqtt_connection.publish.call_count > 0)

        mqtt_connection.publish.assert_called_once_with(
            topic=f"$aws/rules/log_ingest/logs/pictorus/{config.client_id}",
            payload=ANY,
            qos=mqtt.QoS.AT_MOST_ONCE,
        )
        expected_payload = [
            {
                "timestamp": 1672531200000,
                "message": json.dumps(
                    {
                        "level": "info",
                        "message": "foo",
                        "device_id": config.client_id,
                    }
                ),
            },
            {
                "timestamp": 1672531201000,
                "message": json.dumps(
                    {
                        "level": "warning",
                        "message": "bar",
                        "device_id": config.client_id,
                    }
                ),
            },
            {
                "timestamp": 1672531202000,
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
