from datetime import datetime, timedelta, timezone
import json
import re
import fnmatch
from concurrent import futures
import sys
import threading
from time import sleep
from typing import Callable, List, Optional, Tuple, Union, cast

from awscrt.mqtt import Connection
from pyocd.core.session import Session
from pyocd.core.helpers import ConnectHelper
from pyocd.target.pack.pack_target import is_pack_target_available
from pyocd.probe.debug_probe import DebugProbe
from pyocd.flash.file_programmer import FileProgrammer
from pyocd.target import TARGET
from pyocd.coresight.cortex_m import CortexM
from pyocd.core.soc_target import SoCTarget
from pyocd.core.target import Target

try:
    from pyocd.debug.rtt import RTTControlBlock, RTTUpChannel
except ImportError:
    RTTControlBlock = None

from pyocd.core.exceptions import ProbeError
import cmsis_pack_manager as cp

from .command import DeployTarget
from .target_state import TargetState
from .updates_manager import UpdatesManager
from .exceptions import CommandError
from .logging_utils import format_log_level, get_logger, parse_log_entry
from .target_manager import TargetManager, CommandCtxt
from .constants import EMPTY_ERROR, LogMessage
from .config import Config

logger = get_logger()
config = Config()

LOG_CHANNEL_ID = 0
# TODO: Embedded logs do not have timestamps yet
LOG_PATTERN = re.compile(r"\[(?P<log_level>\w+)\] - (?P<message>.*)")


def _parse_log_entry(line: bytes, timestamp_ms: int) -> Optional[LogMessage]:
    try:
        decoded = line.decode("utf-8")
    except UnicodeDecodeError:
        return None

    match = LOG_PATTERN.match(decoded)
    if not match:
        return None

    # Print directly to stdout since this is already formatted as a log entry
    print(decoded)
    # Flush is required to ensure the data is sent immediately
    sys.stdout.flush()

    log_entry = match.groupdict()
    return LogMessage(
        timestamp=timestamp_ms,
        message=json.dumps(
            {
                "level": format_log_level(log_entry["log_level"]),
                "message": log_entry["message"],
                "device_id": config.client_id,
            }
        ),
    )


def _parse_all_log_entries(log_data: bytes, timestamp_ms: int) -> Tuple[List[LogMessage], bytes]:
    lines = log_data.split(b"\n")
    if not lines:
        return [], b""

    # Either the last entry ends with "\n", in which case the last element is an empty string
    # or the last entry does not end with "\n", in which case we want to include it in the next
    # batch
    remainder = lines.pop()
    logs = [_parse_log_entry(line, timestamp_ms) for line in lines if line]
    return [log for log in logs if log is not None], remainder


def _get_matches(cache: cp.Cache, target: str):
    pat = re.compile(fnmatch.translate(target).rsplit("\\Z")[0], re.IGNORECASE)
    return {name for name in cache.index.keys() if pat.search(name)}


def _get_target_name(probe: DebugProbe):
    board_info = probe.associated_board_info
    return board_info.target if board_info else None


def _is_target_installed(target_name: str):
    return (target_name in TARGET) or is_pack_target_available(target_name, Session.get_current())


def _install_target(target_name: str):
    logger.info(f"Installing OCD target: {target_name}")

    cache = cp.Cache(True, False)
    matches = _get_matches(cache, target_name)
    if not matches:
        logger.error(f"Could not find OCD target: {target_name}")
        return

    devices = [cache.index[dev] for dev in matches]
    packs = cache.packs_for_devices(devices)
    logger.info("Downloading packs:")
    for pack in packs:
        logger.info("    " + str(pack))

    cache.download_pack_list(packs)


def _determine_target_name():
    probe = ConnectHelper.choose_probe(
        blocking=False,
        return_first=True,
    )
    if not probe:
        return None

    return _get_target_name(probe)


class ProbeSession:
    # Wrapper around pyocd Session that adds thread synchronization
    def __init__(self, session: Session) -> None:
        self._session = session
        self._lock = threading.Lock()

    def __enter__(self):
        self._lock.acquire()
        if not self._session.is_open:
            self._session.open()

        return self._session

    def __exit__(self, exc_type, exc_value, traceback):
        self._lock.release()

    def close(self):
        self._session.close()


class EmbeddedTargetManager(TargetManager):
    def __init__(
        self,
        target: DeployTarget,
        target_state: TargetState,
        updates_mgr: UpdatesManager,
        connection: Connection,
        update_shadow_cb: Callable[[], None],
    ) -> None:
        super().__init__(target, target_state, updates_mgr, connection, update_shadow_cb)
        self._session: Optional[ProbeSession] = None

        self._listen = False
        self._logging_thread: Union[threading.Thread, None] = None
        self.up_chan: Union["RTTUpChannel", None] = None

    def handle_command(self, cmd_ctxt: CommandCtxt):
        try:
            return super().handle_command(cmd_ctxt)
        except ProbeError as e:
            logger.error("Encountered probe error, disconnecting")
            # If there's an issue with the probe, close the session so we
            # attempt to reconnect on the next command
            self._close_probe()
            raise e

    def _get_session(self):
        if not self._session:
            # This can return None if no targets are found. Need to check this
            # before attempting to use as a ContextManager
            target_name = self._target.options.get("ocd_target", _determine_target_name())
            if not target_name:
                logger.error("Unable to determine target type")
                msg = "Unable to choose target type. Verify target is connected and powered on."
                raise CommandError("TargetSelectError", msg)

            target_available = _is_target_installed(target_name)
            if not target_available:
                # Make sure the target index is installed
                futures.wait([self._updates_mgr.ocd_update_future])
                _install_target(target_name)

            session = ConnectHelper.session_with_chosen_probe(
                blocking=False,
                return_first=True,
                target_override=target_name,
                connect_mode="attach",
            )
            if not session:
                return None

            self._session = ProbeSession(session)

        return self._session

    def _deploy_app(self):
        self._target_state.error_log = EMPTY_ERROR.copy()

        probe = self._get_session()
        if not probe:
            logger.error("Failed to connect to target")
            raise CommandError(
                "TargetConnectionError",
                "Failed to connect to target. Make sure it is connected and powered on.",
            )

        self._stop_logging()
        # Connect to the target
        with probe as session:
            # Create a file programmer and flash the ELF file
            FileProgrammer(session, no_reset=True).program(self._bin_path, file_format="elf")

        if self._target_state.run_app:
            self._start_app_with_logging()

    def handle_set_log_level_cmd(self, cmd_ctxt: CommandCtxt):
        pass

    def _control_app_running(self, run_app: bool):
        if run_app:
            self._start_app_with_logging()
        else:
            self._stop_app_and_logging()

    def close(self):
        self._close_probe()

    def _get_reset_type(self, session: Session) -> Optional[Target.ResetType]:
        if not session.target:
            return None

        return cast("CortexM", session.target.selected_core).default_reset_type

    def _get_target_state(self, session: Session) -> Optional[Target.State]:
        if not session.target:
            return None

        if session.target.selected_core is None:
            # Assume core 0
            session.target.selected_core = 0

        return session.target.get_state()

    def _start_rtt_logging(self, target: SoCTarget):
        """
        Attempts to start the RTT logging for the target. Some chips, like the Cortex-M0+,
        do not support the RTT logger but the code will still run.
        """
        if RTTControlBlock is None:
            return

        try:
            if target.part_number.startswith("STM32H743"):
                # This is a workaround for the STM32H743 where the RTT control block is
                # not found in the usual location. This is a temporary solution until
                # the issue is fixed in pyocd.
                control_block = RTTControlBlock.from_target(target,
                                                            address=0x24000000,
                                                            size=0x7d000)
            else:
                control_block = RTTControlBlock.from_target(target)

            control_block.start()

            if len(control_block.up_channels) > 0:
                self.up_chan = control_block.up_channels[LOG_CHANNEL_ID]
                up_name = self.up_chan.name if self.up_chan.name is not None else ""
                logger.info(f'Reading logs from RTT up channel {LOG_CHANNEL_ID} \
                            ("{up_name}")')
            else:
                logger.info("No RTT channels found, not attempting to read logs")
        except Exception:
            logger.error(
                "Failed to start RTT logging for device {}".format(target.part_number),
                exc_info=True)
            logger.info("Running target {} without RTT Logging".format(target.part_number))

    def _start_app_with_logging(self):
        logger.info("Starting app")
        probe = self._get_session()
        if not probe:
            logger.error("Failed to connect to target")
            return

        self._stop_logging()
        with probe as session:
            if not session.board:
                logger.error("No board found")
                return

            target: SoCTarget = session.board.target
            self._start_rtt_logging(target)

            if self._get_target_state(session) == target.State.RUNNING:
                target.resume()
            else:
                target.reset(reset_type=self._get_reset_type(session))

        if self.up_chan is not None:
            self._start_logging(self.up_chan)

    def _stop_app_and_logging(self):
        logger.info("Stopping app")
        self._stop_logging()
        probe = self._get_session()
        if not probe:
            logger.error("Failed to connect to target")
            return

        with probe as session:
            if not session.target:
                logger.error("No target found")
                return

            if self._get_target_state(session) != session.target.State.HALTED:
                session.target.reset_and_halt(reset_type=self._get_reset_type(session))

    def _start_logging(self, up_chan: "RTTUpChannel"):
        self._listen = True
        self._telemetry_manager.set_build_id(self._target_state.build_hash)
        self._logging_thread = threading.Thread(target=self._log_data, args=(up_chan,))
        self._logging_thread.start()

    def _stop_logging(self):
        self._listen = False
        if self._logging_thread:
            logger.debug("Stopping logging thread")
            try:
                if self._logging_thread.is_alive():
                    self._logging_thread.join()
            except RuntimeError:
                logger.error("Failed to join logging thread", exc_info=True)
            self._logging_thread = None

    def _close_probe(self):
        if self._session:
            self._session.close()
            self._session = None
        self._stop_logging()

    def _log_data(self, up_chan: "RTTUpChannel"):
        logger.debug("Listening for logs")

        logging_start_time = datetime.now(timezone.utc)

        while self._listen:
            try:
                # poll at most 100 times per second to limit CPU use
                sleep(0.01)

                # read data from up buffer
                probe = self._get_session()
                if not probe:
                    continue

                with probe:
                    data = up_chan.read()

                if data:
                    # Multiple JSON objects are being sent over RTT using rpintln and are
                    # delimited by '\n'. These need to be split and handled individually.
                    data_as_str = data.decode("utf-8").split("\n")

                    # RTT Data should just be json telemetry or logging info. If the data can't be
                    # parsed as json, it's likely a log entry.
                    for d in data_as_str:
                        try:
                            j = json.loads(d)
                            app_time = j['app_time_us']
                            time = logging_start_time + timedelta(microseconds=app_time)
                            self._telemetry_manager.add_telem_sample(j, date_now=time)
                        except json.JSONDecodeError:
                            if not d:
                                continue
                            log_entry = parse_log_entry(d,
                                                        datetime.now(timezone.utc),
                                                        config.client_id,
                                                        True)
                            if log_entry:
                                self._telemetry_manager.add_log_entries([log_entry])

                self._telemetry_manager.check_publish_logs(datetime.now(timezone.utc))
            except ProbeError:
                # This can happen if a user unplugs the USB cable, try to handle
                # this gracefully by closing the session.
                logger.error("Error with with connection to probe", exc_info=True)
                self._close_probe()
                break
