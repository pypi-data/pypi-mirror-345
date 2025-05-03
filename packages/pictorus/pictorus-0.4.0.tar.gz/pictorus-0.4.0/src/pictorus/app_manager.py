""" Class for managing pictorus apps and any associated run settings """

import json
from subprocess import run
from tempfile import TemporaryFile
import threading
import time
from queue import Empty
import socket
from typing import Dict, Union

import requests
from awscrt import mqtt
from awscrt.exceptions import AwsCrtError
from awsiot import iotshadow, mqtt_connection_builder

from . import __version__ as CURRENT_VERSION
from .exceptions import TargetMissingError
from .updates_manager import UpdatesManager
from .config import load_app_manifest, store_app_manifest, Config
from .logging_utils import get_logger
from .command import Command, CmdType, DeployTarget, DeployTargetType
from .target_state import TargetState
from .target_manager import CommandCtxt, TargetManager
from .proc_target_manager import ProcTargetManager
from .embedded_target_manager import EmbeddedTargetManager
from .constants import PICTORUS_SERVICE_NAME, THREAD_SLEEP_TIME_S
from .local_server import create_server, COMMS

logger = get_logger()
config = Config()

CONNECT_RETRY_TIMEOUT_S = 15


def connect_mqtt(mqtt_connection: mqtt.Connection):
    connect_future = mqtt_connection.connect()
    while True:
        try:
            connect_future.result()
            break
        except AwsCrtError:
            logger.warning(
                "Connection failed. Retrying in: %ss", CONNECT_RETRY_TIMEOUT_S, exc_info=True
            )
            connect_future = mqtt_connection.connect()
            time.sleep(CONNECT_RETRY_TIMEOUT_S)

    logger.info("Connected to MQTT broker")


def cmd_topic(subtopic: str):
    return f"cmd/pictorus/{config.client_id}/{subtopic}"


def get_ip():
    ip_addr = None
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(0)
        try:
            sock.connect(("10.254.254.254", 1))
            ip_addr = sock.getsockname()[0]
        except socket.error:
            ip_addr = None

    return ip_addr


# Should this be called AppManager still?
class AppManager:
    """Manager responsible for pictorus apps on this device"""

    TARGET_STATES_SHADOW_PROP = "target_states"
    RUN_APP_SHADOW_PROP = "run_app"

    CMD_REQUEST_SUBTOPIC = "req"
    RETAINED_CMD_SUBTOPIC = "ret"

    def __init__(self, version_mgr: UpdatesManager):
        self._mqtt_connection = self._create_mqtt_connection()
        threading.Thread(target=connect_mqtt, args=(self._mqtt_connection,), daemon=True).start()

        self._version_manager = version_mgr
        self._shadow_client = iotshadow.IotShadowClient(self._mqtt_connection)
        self._last_published_shadow_state = None

        self.complete = threading.Event()
        self._cmd_thread: Union[threading.Thread, None] = None
        self._server_thread: Union[threading.Thread, None] = None
        self._network_data = {
            "ip_address": get_ip(),
            "hostname": socket.gethostname(),
        }

        self._app_manifest = load_app_manifest()
        targets = [DeployTarget(t) for t in self._app_manifest.get("targets", [])]
        target_states = {
            k: TargetState(v) for k, v in self._app_manifest.get("target_states", {}).items()
        }
        self._target_managers: Dict[str, TargetManager] = {
            t.id: self._init_target_manager(t, target_state=target_states[t.id], start=False)
            for t in targets
            if t.id in target_states
        }
        self._active_embedded_target: Union[EmbeddedTargetManager, None] = None

        try:
            # TODO: Port should be configurable
            self._server = create_server()
        except Exception as e:
            logger.error("Error creating local server: %s", e, exc_info=True)
            self._server = None

    def __enter__(self):
        self._init_threads()
        self._init_subscriptions()

        self._update_reported_shadow_state()

        for mgr in self._target_managers.values():
            if isinstance(mgr, ProcTargetManager):
                mgr.open()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.complete.set()

        self._mqtt_connection.unsubscribe(cmd_topic(self.CMD_REQUEST_SUBTOPIC))
        self._mqtt_connection.unsubscribe(cmd_topic(self.RETAINED_CMD_SUBTOPIC))

        self._stop_threads()

        for mgr in self._target_managers.values():
            mgr.close()

    def _init_threads(self):
        self._cmd_thread = threading.Thread(target=self._handle_thread_commands)
        self._cmd_thread.start()

        if self._server:
            self._server_thread = threading.Thread(target=self._server.serve_forever)
            self._server_thread.start()

    def _stop_threads(self):
        if self._cmd_thread and self._cmd_thread.is_alive():
            self._cmd_thread.join()

        if self._server and self._server_thread and self._server_thread.is_alive():
            self._server.shutdown()
            self._server_thread.join()

    def _on_connection_interrupted(self, connection, error, **kwargs):
        # Callback when connection is accidentally lost.
        logger.warning("Connection interrupted. error: %s", error)

    def _on_connection_resumed(self, connection, return_code, session_present, **kwargs):
        # Callback when an interrupted connection is re-established.
        logger.info(
            "Connection resumed. return_code: %s session_present: %s", return_code, session_present
        )

        if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
            logger.debug("Session did not persist. Resubscribing to existing topics...")
            connection.resubscribe_existing_topics()

        # Re-publish shadow state so device gets marked as connected
        self._last_published_shadow_state = None
        self._update_reported_shadow_state()

    def _create_mqtt_connection(self):
        """Connect to the MQTT broker"""
        # AWS does not update device shadows from LWT messages, so we need to publish
        # to a standard topic and then republish on the backend:
        # https://docs.aws.amazon.com/iot/latest/developerguide/device-shadow-comms-app.html#thing-connection
        lwt = mqtt.Will(
            topic=f"my/things/{config.client_id}/shadow/update",
            qos=1,
            payload=json.dumps({"state": {"reported": {"connected": False}}}).encode(),
            retain=False,
        )
        mqtt_connection = mqtt_connection_builder.mtls_from_bytes(
            client_id=config.client_id,
            endpoint=config.mqtt_endpoint,
            cert_bytes=config.credentials["certificatePem"].encode(),
            pri_key_bytes=config.credentials["keyPair"]["PrivateKey"].encode(),
            ca_bytes=config.credentials["certificateCa"].encode(),
            on_connection_interrupted=self._on_connection_interrupted,
            on_connection_resumed=self._on_connection_resumed,
            will=lwt,
            keep_alive_secs=30,
            reconnect_min_timeout_secs=5,
            reconnect_max_timeout_secs=30,
        )

        return mqtt_connection

    def _handle_thread_commands(self):
        # Communicating between a flask app and a separate thread is a pain.
        # I was hoping to just pass a reference of the app manager into the server
        # and be able to directly call methods but Flask doesn't support this in a nice way
        # Instead we use a global queue to communicate between the two threads
        while not self.complete.is_set():
            try:
                cmd_data = COMMS.commands.get(timeout=THREAD_SLEEP_TIME_S)
            except Empty:
                continue

            logger.debug("Received local command: %s", cmd_data)
            cmd = Command(cmd_data)
            target = None
            if "target" in cmd_data:
                target = DeployTarget(cmd_data["target"])

            desired_changes = None
            # Special case here to make sure the desired shadow state reflects the commanded state
            if cmd.type == CmdType.RUN_APP:
                desired_changes = {
                    self.TARGET_STATES_SHADOW_PROP: {
                        cmd.target_id: {"run_app": cmd.data["run_app"]}
                    }
                }

            try:
                self._process_cmd(cmd, target=target)
            except Exception as e:
                logger.error("Error processing local command: %s", e, exc_info=True)
            finally:
                self._persist_changes(desired_state=desired_changes)

    def _persist_changes(self, desired_state: Union[Dict, None] = None):
        self._update_manifest()
        self._update_reported_shadow_state(desired_state=desired_state)

    def _aggregate_target_states(self):
        return {
            k: v.target_state_data for k, v in self._target_managers.items() if v.target_state_data
        }

    def _update_manifest(self):
        target_data = sorted(
            [v.target_data for v in self._target_managers.values()], key=lambda x: x["id"]
        )
        manifest = {
            "targets": target_data,
            "target_states": self._aggregate_target_states(),
        }

        store_app_manifest(manifest)
        self._app_manifest = manifest

    def _update_reported_shadow_state(self,
                                      desired_state: Union[Dict, None] = None):
        cached_version = self._version_manager.last_installed if self._version_manager else None
        reported_state = {
            "connected": True,
            self.TARGET_STATES_SHADOW_PROP: self._aggregate_target_states(),
            "version": CURRENT_VERSION,
            "cached_version": cached_version,
            "network": self._network_data,
        }

        state_data = {"reported": reported_state}
        if desired_state:
            state_data["desired"] = desired_state

        logger.info("Updating shadow state: %s", state_data)
        # Don't publish an update if nothing changed. Otherwise we can get in a bad state
        # where IoT backend continuously publishes deltas and we respond with the
        # same reported state
        if state_data == self._last_published_shadow_state:
            return

        request = iotshadow.UpdateShadowRequest(
            thing_name=config.client_id,
            state=iotshadow.ShadowState(**state_data),
        )
        self._shadow_client.publish_update_shadow(request, mqtt.QoS.AT_LEAST_ONCE)
        self._last_published_shadow_state = state_data
        COMMS.reported_state = reported_state

    def _init_subscriptions(self):
        self._shadow_client.subscribe_to_shadow_delta_updated_events(
            request=iotshadow.ShadowDeltaUpdatedSubscriptionRequest(thing_name=config.client_id),
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=self._on_shadow_delta_updated,
        )

        self._mqtt_connection.subscribe(
            cmd_topic(self.CMD_REQUEST_SUBTOPIC),
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=self._on_cmd_request,
        )

        self._mqtt_connection.subscribe(
            cmd_topic(self.RETAINED_CMD_SUBTOPIC),
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=self._on_retained_cmd,
        )

    def _upload_logs(self, cmd: Command):
        upload_data = cmd.data["upload_dest"]
        line_count = str(cmd.data["line_count"])

        with TemporaryFile("rb+") as tmp_log:
            run(
                ["journalctl", "-u", PICTORUS_SERVICE_NAME, "-n", line_count, "--no-pager"],
                check=True,
                stdout=tmp_log,
            )
            tmp_log.flush()
            tmp_log.seek(0)

            # TODO: This loads the entire uncompressed log contents into memory.
            # Would be nicer to write to a (possible compressed?) file and then upload in chunks
            # if data exceeds a certain size
            response = requests.post(
                upload_data["url"], data=upload_data["fields"], files={"file": tmp_log}
            )
            response.raise_for_status()

    def _init_target_manager(
        self, target: DeployTarget, target_state: Union[TargetState, None] = None, start=True
    ) -> TargetManager:
        if not target_state:
            target_state = TargetState({})

        mgr_class = None
        if target.type == DeployTargetType.PROCESS:
            mgr_class = ProcTargetManager
        elif target.type == DeployTargetType.EMBEDDED:
            mgr_class = EmbeddedTargetManager
        else:
            raise ValueError(f"Unknown target type: {target.type}")

        mgr = mgr_class(
            target,
            target_state,
            self._version_manager,
            self._mqtt_connection,
            self._update_reported_shadow_state,
        )

        # This is an intentionally delayed start for the class to initialize until
        # _get_target_manager is called. Note: ProcTargetManager will start immediately
        # and EmbeddedTargetManager will start when commands are dispatched.
        if start:
            mgr.open()

        return mgr

    def _get_target_manager(
        self, cmd: Command, target: Union[DeployTarget, None] = None
    ) -> TargetManager:
        if cmd.target_id is None:
            raise ValueError("Empty target ID specified")

        if cmd.target_id not in self._target_managers:
            if not target:
                raise TargetMissingError(
                    f"Target ID: {cmd.target_id} not found and no target provided for command"
                )

            self._target_managers[target.id] = self._init_target_manager(target)

        target_mgr = self._target_managers[cmd.target_id]
        curr_target = target_mgr._target
        if target is not None and (
            curr_target.type != target.type
            or curr_target.options.get("platform_target") != target.options.get("platform_target")
        ):
            logger.info("Target type has changed. Reinitializing target manager")
            target_mgr.close()
            target_mgr = self._init_target_manager(target)
            self._target_managers[cmd.target_id] = target_mgr

        return self._target_managers[cmd.target_id]

    def _process_cmd(self, cmd: Command, target: Union[DeployTarget, None] = None):
        logger.info("Received command: %s", cmd.to_dict())

        if target:
            logger.info("With target: %s", target.to_dict())

        # First handle any commands that aren't target-specific
        if cmd.type == CmdType.UPLOAD_LOGS:
            self._upload_logs(cmd)
            return

        # Check if there is an active embedded target and compare it to the
        # command target. If they don't match, close the active target, it
        # will be opened in the subsequent _get_target_manager call.
        if self._active_embedded_target:
            if cmd.target_id != self._active_embedded_target.target_id:
                self._active_embedded_target.close()
                self._active_embedded_target = None

        mgr = self._get_target_manager(cmd, target=target)
        if isinstance(mgr, EmbeddedTargetManager):
            self._active_embedded_target = mgr
        cmd_ctxt = CommandCtxt(cmd=cmd)
        mgr.handle_command(cmd_ctxt)

    def _on_retained_cmd(self, topic: str, payload: bytes):
        # This is an echo of the message we published to clear the retained message
        if not payload:
            return

        try:
            self._on_cmd_request(topic, payload)
        finally:
            # This is a retained message so clear it by publishing an empty payload
            # This is a barebones implementation for being able to queue actions for a device.
            # Right now it only allows a single queued command.
            # Eventually we can implement the full jobs API for more robust control of actions
            self._mqtt_connection.publish(
                topic=topic,
                payload="",
                qos=mqtt.QoS.AT_LEAST_ONCE,
                retain=True,
            )

    def _on_cmd_request(self, topic: str, payload: bytes):
        logger.debug("Received message on topic %s: %s", topic, payload)

        cmd_data = json.loads(payload)
        cmd = Command(cmd_data)
        target = DeployTarget(cmd_data["target"])

        try:
            self._process_cmd(cmd, target=target)
        except Exception as e:
            logger.error("Error processing command: %s", e, exc_info=True)
        finally:
            self._persist_changes()

    def _on_shadow_delta_updated(self, delta: iotshadow.ShadowDeltaUpdatedEvent):
        if not delta.state:
            return

        logger.debug("Received shadow delta: %s", delta.state)

        cmds = []
        if self.TARGET_STATES_SHADOW_PROP in delta.state:
            run_app_changes = {
                target_id: target_state[self.RUN_APP_SHADOW_PROP]
                for target_id, target_state in delta.state[self.TARGET_STATES_SHADOW_PROP].items()
                if self.RUN_APP_SHADOW_PROP in target_state
            }
            for target_id, run_app in run_app_changes.items():
                run_cmd = Command(
                    {
                        "type": CmdType.RUN_APP.value,
                        "data": {"run_app": run_app},
                        # Normally commands pass in a full target object,
                        # but we don't have a way to do that currently with shadow deltas
                        "target_id": target_id,
                    },
                )
                cmds.append(run_cmd)

        desired_state = {}
        for cmd in cmds:
            try:
                self._process_cmd(cmd)
            except TargetMissingError:
                logger.warning(
                    "Received shadow delta command for missing target: %s", cmd.target_id
                )
                # Clear the desired state for the missing target
                # so we don't keep getting change events for it
                if self.TARGET_STATES_SHADOW_PROP not in desired_state:
                    desired_state[self.TARGET_STATES_SHADOW_PROP] = {}

                desired_state[self.TARGET_STATES_SHADOW_PROP][cmd.target_id] = None
            except Exception:
                logger.error(
                    "Error processing shadow delta command: %s", cmd.to_dict(), exc_info=True
                )

        if cmds:
            self._persist_changes(desired_state=desired_state)
