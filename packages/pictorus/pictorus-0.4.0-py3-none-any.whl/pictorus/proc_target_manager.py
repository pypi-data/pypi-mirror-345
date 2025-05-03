import os
import socket
from subprocess import Popen, PIPE, STDOUT
import sys
import time
import threading
import json
from typing import Callable, Union
from datetime import datetime, timezone
from awscrt import mqtt
from .updates_manager import UpdatesManager
from .target_state import TargetState
from .config import Config
from .logging_utils import get_logger, parse_log_entry
from .target_manager import TargetManager, CommandCtxt
from .command import DeployTarget
from .constants import AppLogLevel, THREAD_SLEEP_TIME_S, EMPTY_ERROR

config = Config()
logger = get_logger()


# Mocking os.path.exists directly on this module causes issues with requests
# So add a wrapper function to mock instead
def _path_exists(path: str) -> bool:
    return os.path.exists(path)


TELEM_HOST = "127.0.0.1"
UDP_BUFFER_SIZE_BYTES = 65507  # Max buffer for IPv4


class ProcTargetManager(TargetManager):
    NO_LOG_ERROR = {
        "err_type": "NoLogError",
        "message": "App crashed unexpectedly",
    }

    def __init__(
        self,
        target: DeployTarget,
        target_state: TargetState,
        updates_mgr: UpdatesManager,
        connection: mqtt.Connection,
        update_shadow_cb: Callable[[], None],
    ):
        super().__init__(target, target_state, updates_mgr, connection, update_shadow_cb)
        self._app_log_level = AppLogLevel.INFO
        self._pictorus_app_process: Union[Popen, None] = None
        self._error_log_path = os.path.join(self._assets_dir, "pictorus_errors.json")

        self._listen = False
        self._app_watcher_thread: Union[threading.Thread, None] = None
        self._telem_listener_thread: Union[threading.Thread, None] = None
        self._logging_thread: Union[threading.Thread, None] = None
        self._ready = threading.Event()

        self._socket_data = None

    @property
    def app_is_running(self) -> bool:
        """Return whether the app is currently running"""
        return bool(self._pictorus_app_process)

    def _deploy_app(self):
        self._target_state.error_log = EMPTY_ERROR.copy()
        self._restart_app()

    def handle_set_log_level_cmd(self, cmd_ctxt: CommandCtxt):
        log_level = cmd_ctxt.cmd.data["log_level"]
        try:
            log_level = AppLogLevel(log_level)
        except ValueError:
            logger.warning("Received invalid log level: %s", log_level)
            return

        self._app_log_level = log_level
        self._restart_app()

    def _control_app_running(self, run_app: bool):
        if run_app:
            self._maybe_start_app()
        else:
            self._stop_app()

    def open(self):
        self._control_app_running(self._target_state.run_app)

    def close(self):
        self._stop_app()

        logger.info("Stopping listening...")
        self._listen = False
        if self._telem_listener_thread:
            self._telem_listener_thread.join()
        self._telem_listener_thread = None

        if self._logging_thread:
            self._logging_thread.join()
        self._logging_thread = None

        if self._app_watcher_thread:
            self._app_watcher_thread.join()
        self._app_watcher_thread = None

        logger.info("Stopped listening...")

    def _notify_app_crash(self, error_log: dict):
        self._target_state.error_log = error_log
        self._stop_app()
        self._update_shadow_cb()

    def _watch_app(self):
        while self._listen:
            # If an app process has started, communicate() to catch unexpected terminations.
            if self._pictorus_app_process:
                logger.info("Watching for app crashes")

                # Reset Error shadow state for each new app run
                self._target_state.error_log = EMPTY_ERROR.copy()
                self._update_shadow_cb()

                # Blocks until the app process ends
                self._pictorus_app_process.wait()

                # If app manager knows about shutdown, everything's fine
                if not self.app_is_running:
                    logger.info("Detected normal termination of Pictorus App")
                    continue

                logger.warning("Pictorus App unexpectedly crashed!")
                # Check for PictorusError json file and set the shadow state error log to that.
                if _path_exists(self._error_log_path):
                    logger.warning("Sending Pictorus error logs...")
                    with open(self._error_log_path, "r", encoding="utf-8") as error_file:
                        error_log = json.load(error_file)

                    logger.warning("Error log: %s", error_log)
                    os.remove(self._error_log_path)
                else:
                    # There should always be a log. If not, return a special error so we know.
                    logger.warning("No error logs!")
                    error_log = self.NO_LOG_ERROR.copy()

                self._notify_app_crash(error_log)

            # If no app is currently running, prevent tight loop
            time.sleep(THREAD_SLEEP_TIME_S)

        # Exit once self.complete Event() is set
        logger.info("Closing App Watcher thread...")

    def _maybe_start_app(self):
        # Don't start if we're already running or not configured to run
        if not self._target_state.run_app or self._pictorus_app_process:
            logger.debug("Not starting app")
            return

        build_hash = self._target_state.build_hash
        if build_hash and _path_exists(self._bin_path):
            logger.info("Starting pictorus app")
            self._start_listening(build_hash)
            # Wait for telemetry thread to be in a good state, but continue if it takes too long
            # so we're able to communicate with device manager even if something goes wrong
            self._ready.wait(timeout=30)
            # Could potentially pipe app output back to the backend/user if we want to
            if not self._socket_data:
                logger.error(
                    "Unable to bind communication socket for app telemetry. Not starting app."
                )
                return

            host, port = self._socket_data
            try:
                self._pictorus_app_process = Popen(
                    self._bin_path,
                    stdout=PIPE,
                    stderr=STDOUT,
                    env={
                        "APP_PUBLISH_SOCKET": f"{host}:{port}",
                        "APP_RUN_PATH": self._assets_dir,
                        "LOG_LEVEL": self._app_log_level.value,
                    },
                )
                # Logs need a handle to the process,
                # so can't start logging until after the process is created
                self._start_logging(self._pictorus_app_process)
            except OSError as e:
                logger.error("Failed to start app", exc_info=True)
                self._notify_app_crash(
                    {
                        "err_type": "AppStartError",
                        "message": f"Failed to start app: {e}",
                    }
                )

        else:
            logger.info("No pictorus apps installed")

    def _stop_app(self):
        if self._pictorus_app_process:
            logger.info("Stopping pictorus app")
            app_handle = self._pictorus_app_process
            self._pictorus_app_process = None
            app_handle.terminate()
            app_handle.wait()

    def _restart_app(self):
        self._stop_app()
        self._maybe_start_app()

    def _start_logging(self, proc: Popen):
        if self._logging_thread:
            try:
                self._logging_thread.join(timeout=5)
            except TimeoutError:
                logger.error("Failed to stop previous logging thread", exc_info=True)

            self._logging_thread = None

        self._logging_thread = threading.Thread(target=self._log_data, args=(proc,))
        self._logging_thread.start()

    def _log_data(self, proc: Popen):
        pipe = proc.stdout
        if not pipe:
            logger.error("No pipe provided for logging")
            return

        self._telemetry_manager.reset_log_start_time()
        os.set_blocking(pipe.fileno(), False)
        while self._listen and proc.poll() is None:
            date_now = datetime.now(timezone.utc)
            try:
                line = pipe.readline()
                if line:
                    data = line.decode().rstrip()

                    # Print directly to stdout since this is already formatted as a log entry
                    print(data)
                    # Flush is required to ensure the data is sent immediately
                    sys.stdout.flush()

                    log_entry = parse_log_entry(data, date_now, config.client_id)
                    if log_entry:
                        self._telemetry_manager.add_log_entries([log_entry])
                else:
                    time.sleep(0.1)
            except BlockingIOError:
                # If no data is available, continue to check if we should publish
                time.sleep(0.1)
                pass
            except StopIteration:
                break

            self._telemetry_manager.check_publish_logs(date_now)

        pipe.close()
        self._telemetry_manager.publish_logs(datetime.now(timezone.utc))

    def _start_listening(self, build_id: str):
        """Start listening to the specified app"""
        self._telemetry_manager.set_build_id(build_id)
        self._listen = True
        if not self._app_watcher_thread:
            logger.info("Starting new app watcher thread...")
            self._app_watcher_thread = threading.Thread(target=self._watch_app)
            self._app_watcher_thread.start()
        else:
            logger.info("App watcher already active!")

        if not self._telem_listener_thread:
            logger.info("Starting new listener thread...")
            self._telem_listener_thread = threading.Thread(target=self._listen_for_telem)
            self._telem_listener_thread.start()
        else:
            logger.info("Listener already active!")

    def _listen_for_telem(self):
        """Main function for listening to app telem"""
        # Create UDP socket
        logger.info("Listening...")
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
            sock.settimeout(1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Bind to any available port
            sock.bind((TELEM_HOST, 0))

            self._socket_data = sock.getsockname()
            self._ready.set()
            while self._listen:
                try:
                    data = sock.recv(UDP_BUFFER_SIZE_BYTES)
                    json_data = json.loads(data)
                    # Maybe this should come from the received data?
                    # TODO: When a message is logged in Linux, Local::now().format("%+") used
                    # to get the current time. Would we rather use app_time_us like in the
                    # embedded system case?
                    date_now = datetime.now(timezone.utc)
                    self._telemetry_manager.add_telem_sample(json_data, date_now)
                except json.JSONDecodeError:
                    logger.warning("Failed to read socket data", exc_info=True)
                except socket.timeout:
                    continue

        self.socket_data = None
