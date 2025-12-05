import mqtt from "mqtt";
import fs from "fs";
import path from "path";
import type { Config } from "./types";

/**
 * Telemetry Subscriber Example
 *
 * This example shows how to subscribe to telemetry data from all production
 * lines in the factory and process the incoming sensor readings.
 */

// Load configuration
const config: Config = JSON.parse(
  fs.readFileSync(path.resolve(__dirname, "../config.json"), "utf-8")
);

// Read certificate files
const ca = fs.readFileSync(path.resolve(__dirname, "..", config.mqtt.ca));
const cert = fs.readFileSync(path.resolve(__dirname, "..", config.mqtt.cert));
const key = fs.readFileSync(path.resolve(__dirname, "..", config.mqtt.key));

// MQTT connection options
const options = {
  host: config.mqtt.endpoint,
  port: config.mqtt.port,
  protocol: config.mqtt.protocol,
  clientId: config.mqtt.clientId,
  ca: ca,
  cert: cert,
  key: key,
  rejectUnauthorized: true,
};

console.log("🏭 ChipTech Factory Monitoring - Telemetry Subscriber\n");
console.log("Connecting to factory...\n");

const client = mqtt.connect(options);

client.on("connect", () => {
  console.log("✅ Connected to Virtual Factory\n");

  // Subscribe to all telemetry from all lines
  console.log("📡 Subscribing to factory telemetry...\n");

  // Subscribe to telemetry from all lines and all machines
  client.subscribe("factory/+/+/telemetry", { qos: 1 }, (err) => {
    if (err) {
      console.error("❌ Subscription error:", err);
      return;
    }
    console.log("✅ Subscribed to: factory/+/+/telemetry");
  });

  // Subscribe to state changes from all lines and all machines
  client.subscribe("factory/+/+/state", { qos: 1 }, (err) => {
    if (err) {
      console.error("❌ Subscription error:", err);
      return;
    }
    console.log("✅ Subscribed to: factory/+/+/state");
  });

  console.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  console.log("Waiting for messages... (Press Ctrl+C to exit)\n");
});

client.on("message", (topic, message) => {
  try {
    const rawData = JSON.parse(message.toString());
    console.log("📥 Message received:", rawData);
  } catch (error) {
    const errorMessage =
      error instanceof Error ? error.message : "Unknown error";
    console.error("Error parsing message:", errorMessage);
  }
});

client.on("error", (error) => {
  // Graceful shutdown
  process.on("SIGINT", () => {
    console.log("\n\n👋 Shutting down...");
    client.end(false, undefined, () => {
      console.log("Disconnected from factory.");
      process.exit(0);
    });
  });
  client.end(false, {}, () => {
    console.log("Disconnected from factory.");
    process.exit(0);
  });
});
