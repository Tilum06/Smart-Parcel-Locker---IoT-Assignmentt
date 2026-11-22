"""Test 5, steps 2-4: publish simulated locker telemetry to CoreIOT.

Run from the repository root: python tests/coreiot/test5_telemetry.py
Requires paho-mqtt>=2,<3. Set COREIOT_ACCESS_TOKEN or enter it securely.
Exit codes: 0 = PASS (MQTT acknowledgements only), 1 = FAIL, 2 = BLOCKED.
"""

import getpass
from importlib.metadata import PackageNotFoundError, version
import json
import os
import threading
import warnings


BROKER = "app.coreiot.io"
PORT = 1883
TOPIC = "v1/devices/me/telemetry"
CONNECT_TIMEOUT = 10
PUBLISH_TIMEOUT = 10
MESSAGE_INTERVAL = 2


class TelemetryError(RuntimeError):
    """A test failure with a message that contains no credentials."""


def main():
    try:
        if version("paho-mqtt").split(".")[0] != "2":
            print('BLOCKED: Requires paho-mqtt>=2,<3.')
            return 2
        import paho.mqtt.client as mqtt
    except (PackageNotFoundError, ImportError):
        print('BLOCKED: Install with python -m pip install "paho-mqtt>=2,<3".')
        return 2

    token = os.environ.get("COREIOT_ACCESS_TOKEN", "").strip()
    if not token:
        try:
            # Refuse an insecure echoing fallback when no terminal is available.
            with warnings.catch_warnings():
                warnings.simplefilter("error", getpass.GetPassWarning)
                token = getpass.getpass("CoreIOT Device Access Token: ").strip()
        except (EOFError, KeyboardInterrupt, getpass.GetPassWarning):
            print("BLOCKED: No Access Token available through secure input.")
            return 2
    if not token:
        print("BLOCKED: Access Token is required; no connection attempted.")
        return 2

    connection_ready = threading.Event()
    connection_lost = threading.Event()
    state = {"error": None, "network_blocked": False}

    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            state["error"] = f"Connection/authentication rejected: {reason_code}"
        else:
            print(f"Connected to {BROKER}:{PORT} (Callback API v2).")
        connection_ready.set()

    def on_connect_fail(client, userdata):
        state["error"] = "Cannot reach broker; check Internet, DNS and port 1883."
        state["network_blocked"] = True
        connection_ready.set()

    def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
        if reason_code.is_failure:
            state["error"] = f"Unexpected MQTT disconnect: {reason_code}"
        connection_lost.set()
        connection_ready.set()

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        protocol=mqtt.MQTTv311,
        reconnect_on_failure=False,
    )
    client.username_pw_set(token)
    client.connect_timeout = CONNECT_TIMEOUT
    client.on_connect = on_connect
    client.on_connect_fail = on_connect_fail
    client.on_disconnect = on_disconnect
    loop_started = False

    try:
        print(f"Connecting to {BROKER}:{PORT}...")
        client.connect_async(BROKER, PORT, keepalive=30)
        if client.loop_start() != mqtt.MQTT_ERR_SUCCESS:
            raise TelemetryError("Cannot start MQTT network loop.")
        loop_started = True
        if not connection_ready.wait(CONNECT_TIMEOUT):
            raise TimeoutError("Connection timed out before MQTT CONNACK.")
        if state["network_blocked"]:
            raise OSError("Broker unreachable.")
        if state["error"] or not client.is_connected():
            raise TelemetryError(state["error"] or "MQTT connection not established.")

        for counter, door in enumerate(("CLOSED", "OPEN", "CLOSED"), start=1):
            if connection_lost.is_set() or not client.is_connected():
                raise TelemetryError(state["error"] or "Connection lost before publish.")
            payload = json.dumps({
                "simulated": True,
                "test5_l01_door": door,
                "test5_counter": counter,
            })
            print(f"Sending message {counter}/3...")
            info = client.publish(TOPIC, payload, qos=1, retain=False)
            if info.rc != mqtt.MQTT_ERR_SUCCESS:
                raise TelemetryError(f"Publish {counter} failed (rc={info.rc}).")
            info.wait_for_publish(timeout=PUBLISH_TIMEOUT)
            if not info.is_published():
                raise TimeoutError(f"Publish {counter} timed out waiting for PUBACK.")
            print(f"Publish {counter}/3: QoS 1 PUBACK received; {payload}")
            if counter < 3 and connection_lost.wait(MESSAGE_INTERVAL):
                raise TelemetryError(state["error"] or "Connection lost between messages.")

        print("PASS: All 3 messages acknowledged by MQTT broker.")
        print("CoreIOT storage is unverified; check the device's Latest Telemetry.")
        return 0
    except (OSError, TimeoutError):
        print("BLOCKED: Network/connection/PUBACK timeout; check broker access and retry.")
        return 2
    except TelemetryError as error:
        print(f"FAIL: {error}")
        return 1
    except (RuntimeError, ValueError) as error:
        # Do not print arbitrary exception text, which could contain credentials.
        if state["error"]:
            print(f"FAIL: {state['error']}")
        else:
            print(f"FAIL: MQTT operation failed ({type(error).__name__}).")
        return 1
    except KeyboardInterrupt:
        print("BLOCKED: Test interrupted.")
        return 2
    finally:
        try:
            client.disconnect()
        finally:
            if loop_started:
                client.loop_stop()
        print("MQTT connection and network loop closed.")


if __name__ == "__main__":
    raise SystemExit(main())
