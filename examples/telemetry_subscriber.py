#!/usr/bin/env python3
"""
Telemetry Subscriber Example

This example shows how to subscribe to telemetry data from all production
lines in the factory and process the incoming sensor readings.
"""

import json
import ssl
import signal
import sys
from pathlib import Path
from paho.mqtt import client as mqtt_client


def load_config():
    """Load configuration from config.json"""
    config_path = Path(__file__).parent.parent / "config.json"
    with open(config_path, "r") as f:
        return json.load(f)


def on_connect(client, userdata, flags, rc):
    """Callback when connected to MQTT broker"""
    if rc == 0:
        print("✅ Connected to Virtual Factory\n")
        print("📡 Subscribing to factory telemetry...\n")
        
        # Subscribe to telemetry from all lines and all machines
        client.subscribe("factory/+/+/telemetry", qos=1)
        print("✅ Subscribed to: factory/+/+/telemetry")
        
        # Subscribe to state changes from all lines and all machines
        client.subscribe("factory/+/+/state", qos=1)
        print("✅ Subscribed to: factory/+/+/state")
        
        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("Waiting for messages... (Press Ctrl+C to exit)\n")
    else:
        print(f"❌ Connection failed with code {rc}")
        sys.exit(1)


def on_message(client, userdata, msg):
    """Callback when a message is received"""
    try:
        raw_data = json.loads(msg.payload.decode())
        print(f"📥 Message received: {raw_data}")
    except json.JSONDecodeError as e:
        print(f"Error parsing message: {e}")
    except Exception as e:
        print(f"Error processing message: {e}")


def on_subscribe(client, userdata, mid, granted_qos):
    """Callback when subscription is confirmed"""
    # Optional: handle subscription confirmation
    pass


def on_disconnect(client, userdata, rc):
    """Callback when disconnected from MQTT broker"""
    if rc != 0:
        print("⚠️  Unexpected disconnection.")


def main():
    # Load configuration
    config = load_config()
    mqtt_config = config["mqtt"]
    
    print("🏭 ChipTech Factory Monitoring - Telemetry Subscriber\n")
    print("Connecting to factory...\n")
    
    # Create MQTT client
    client = mqtt_client.Client(client_id=mqtt_config["clientId"])
    
    # Set callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.on_disconnect = on_disconnect
    
    # Configure TLS/SSL
    base_path = Path(__file__).parent.parent
    ca_path = base_path / mqtt_config["ca"].lstrip("./")
    cert_path = base_path / mqtt_config["cert"].lstrip("./")
    key_path = base_path / mqtt_config["key"].lstrip("./")
    
    client.tls_set(
        ca_certs=str(ca_path),
        certfile=str(cert_path),
        keyfile=str(key_path),
        cert_reqs=ssl.CERT_REQUIRED,
        tls_version=ssl.PROTOCOL_TLSv1_2
    )
    
    # Connect to broker
    try:
        client.connect(
            mqtt_config["endpoint"],
            mqtt_config["port"],
            keepalive=60
        )
    except Exception as e:
        print(f"❌ Connection error: {e}")
        sys.exit(1)
    
    # Setup graceful shutdown
    def signal_handler(sig, frame):
        print("\n\n👋 Shutting down...")
        client.disconnect()
        client.loop_stop()
        print("Disconnected from factory.")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start network loop
    client.loop_forever()


if __name__ == "__main__":
    main()
