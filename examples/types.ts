import { MqttProtocol } from "mqtt";

export interface MqttConfig {
  endpoint: string;
  port: number;
  protocol: MqttProtocol;
  clientId: string;
  ca: string;
  cert: string;
  key: string;
}

export interface FactoryConfig {
  assignedLine: string;
  machineTypes: string[];
}

export interface Config {
  mqtt: MqttConfig;
  factory: FactoryConfig;
}

export interface StartCommand {
  command: "start";
  parameters: any;
}

export interface StopCommand {
  command: "stop";
}

export type MachineCommand = StartCommand | StopCommand;
