#!/usr/bin/env python3
"""
Basic MQTT Connection Example

This example demonstrates how to connect to the ChipTech Virtual Factory
using AWS IoT Core with mutual TLS authentication.
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
        print("✅ Successfully connected to the Virtual Factory!")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        print(f"You are now connected to ChipTech Building 7.")
        print(f"Your assigned production line: {userdata['assigned_line']}")
        print("\nConnection is active. Press Ctrl+C to disconnect.\n")
    else:
        print(f"❌ Connection failed with code {rc}")
        sys.exit(1)


def on_disconnect(client, userdata, rc):
    """Callback when disconnected from MQTT broker"""
    if rc != 0:
        print("⚠️  Unexpected disconnection. Attempting to reconnect...")
    else:
        print("\n🔌 Connection closed")


def on_log(client, userdata, level, buf):
    """Callback for logging (optional, for debugging)"""
    # Uncomment to see detailed logs
    # print(f"LOG: {buf}")
    pass


def main():
    # Load configuration
    config = load_config()
    mqtt_config = config["mqtt"]
    factory_config = config["factory"]
    
    print("🏭 ChipTech Factory Monitoring - Connection Example\n")
    print("Connecting to AWS IoT Core...")
    print(f"Client ID: {mqtt_config['clientId']}")
    print(f"Endpoint: {mqtt_config['endpoint']}:{mqtt_config['port']}\n")
    
    # Create MQTT client
    client = mqtt_client.Client(client_id=mqtt_config["clientId"])
    
    # Set user data (to pass assigned line to callback)
    client.user_data_set({"assigned_line": factory_config["assignedLine"]})
    
    # Set callbacks
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_log = on_log
    
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
    client.connect(
        mqtt_config["endpoint"],
        mqtt_config["port"],
        keepalive=60
    )
    
    # Setup graceful shutdown
    def signal_handler(sig, frame):
        print("\n\n👋 Disconnecting from factory...")
        client.disconnect()
        client.loop_stop()
        print("Goodbye!")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start network loop
    client.loop_forever()


if __name__ == "__main__":
    main()
