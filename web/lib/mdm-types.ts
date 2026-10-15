export type DeviceStatus = "enrolled" | "authenticated" | "unenrolled" | string;

export interface MdmDevice {
  id: number;
  serial: string | null;
  udid: string;
  ip: string | null;
  timestamp: string | null;
  last_status: DeviceStatus | null;
  product_name: string | null;
  os_version: string | null;
  push_topic: string | null;
  has_push_token: 0 | 1;
}

export interface DevicesResponse {
  devices: MdmDevice[];
}

export interface ApiError {
  error: string;
  allowed?: string[];
}

export interface QueueCommandRequest {
  command_type: MdmCommandType;
  payload?: Record<string, unknown>;
}

export interface QueueCommandResponse {
  status: "queued";
  command_uuid: string;
  apns_notified: boolean;
}

export type MdmCommandType =
  | "DeviceInformation"
  | "DeviceLock"
  | "EraseDevice"
  | "RestartDevice"
  | "InstallProfile"
  | "ProfileList"
  | "InstalledApplicationList";

export const MDM_COMMANDS: readonly MdmCommandType[] = [
  "DeviceInformation",
  "DeviceLock",
  "EraseDevice",
  "RestartDevice",
  "InstallProfile",
  "ProfileList",
  "InstalledApplicationList",
] as const;
