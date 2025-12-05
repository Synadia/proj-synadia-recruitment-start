import mqtt from "mqtt";
import fs from "fs";
import path from "path";
import type { Config } from "./types";

/**
 * Basic MQTT Connection Example
 *
 * This example demonstrates how to connect to the ChipTech Virtual Factory
 * using AWS IoT Core with mutual TLS authentication.
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
  keepalive: 60,
  clean: true,
  reconnectPeriod: 1000,
};

console.log("🏭 ChipTech Factory Monitoring - Connection Example\n");
console.log("Connecting to AWS IoT Core...");
console.log(`Client ID: ${config.mqtt.clientId}`);
console.log(`Endpoint: ${config.mqtt.endpoint}:${config.mqtt.port}\n`);

// Create MQTT client
const client = mqtt.connect(options);

// Connection event handlers
client.on("connect", () => {
  console.log("✅ Successfully connected to the Virtual Factory!");
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
  console.log("You are now connected to ChipTech Building 7.");
  console.log("Your assigned production line:", config.factory.assignedLine);
  console.log("\nConnection is active. Press Ctrl+C to disconnect.\n");

  // Keep connection alive for demonstration
  // In your application, you would subscribe to topics here
});

client.on("error", (error) => {
  console.error("❌ Connection error:", error.message);
  process.exit(1);
});

client.on("close", () => {
  console.log("\n🔌 Connection closed");
});

client.on("offline", () => {
  console.log("⚠️  Client is offline, attempting to reconnect...");
});

client.on("reconnect", () => {
  console.log("🔄 Reconnecting to the factory...");
});

// Graceful shutdown
process.on("SIGINT", () => {
  console.log("\n\n👋 Disconnecting from factory...");
  client.end(false, undefined, () => {
    console.log("Goodbye!");
    process.exit(0);
  });
});
