import { listDevices, resolveDevice, health, invoke } from "./lib/companion_client.js";

export const name = "dsh-device-bridge";
export const inject = ["tools", "systemPrompt"];

function positive(v, d) {
  const n = Number(v);
  return Number.isFinite(n) && n > 0 ? n : d;
}

export function apply(ctx, config = {}) {
  if (config.enabled === false) {
    console.log("[dsh-device-bridge] disabled");
    return;
  }
  const timeoutMs = positive(config.timeoutMs, 30_000);
  const devices = listDevices(config.devices);
  const defaultAllow = Array.isArray(config.defaultAllowActions)
    ? config.defaultAllowActions.map(String)
    : ["health", "ping", "status"];
  console.log(`[dsh-device-bridge] devices=${devices.length}`);

  ctx.systemPrompt.section({
    name: "tool:device-bridge",
    order: 142,
    text: "dsh-device-bridge talks to any device that implements Companion protocol v1 (/v1/health, /v1/invoke). Use for phones, IoT, or thin agents when SSH is not enough. Prefer device_list then device_status before device_invoke.",
  });

  ctx.tools.register({
    name: "device_list",
    description: "List configured companion devices (id, kind, baseUrl).",
    parameters: { type: "object", additionalProperties: false, properties: {} },
    output: {
      schema: { type: "object", additionalProperties: true },
      render: (_a, v) => [{ type: "text", text: JSON.stringify(v, null, 2) }],
    },
    timeoutMs,
    isConcurrencySafe: () => true,
    async execute() {
      return {
        ok: true,
        devices: devices.map((x) => ({
          id: x.id,
          kind: x.kind,
          baseUrl: x.baseUrl,
          allowActions: x.allowActions,
        })),
        protocol: "companion-v1",
      };
    },
    presentCall: () => ({ card: "generic", title: "device list" }),
    presentResult: (_a, r) => ({ card: "generic", title: "device list", content: r.content }),
  });

  ctx.tools.register({
    name: "device_status",
    description: "GET /v1/health on a device.",
    parameters: {
      type: "object",
      additionalProperties: false,
      properties: { deviceId: { type: "string" } },
    },
    output: {
      schema: { type: "object", additionalProperties: true },
      render: (_a, v) => [{ type: "text", text: JSON.stringify(v, null, 2) }],
    },
    timeoutMs,
    isConcurrencySafe: () => true,
    async execute(args) {
      try {
        const device = resolveDevice(devices, args.deviceId);
        const h = await health(device, { timeoutMs });
        return { ok: h.ok, deviceId: device.id, kind: device.kind, health: h };
      } catch (e) {
        return { ok: false, error: e instanceof Error ? e.message : String(e) };
      }
    },
    presentCall: () => ({ card: "generic", title: "device status" }),
    presentResult: (_a, r) => ({ card: "generic", title: "device status", content: r.content }),
  });

  ctx.tools.register({
    name: "device_invoke",
    description: "POST /v1/invoke on a device (action must be allowlisted).",
    parameters: {
      type: "object",
      additionalProperties: false,
      required: ["action"],
      properties: {
        deviceId: { type: "string" },
        action: { type: "string" },
        args: { type: "object", additionalProperties: true },
        confirm: { type: "boolean" },
      },
    },
    output: {
      schema: { type: "object", additionalProperties: true },
      render: (_a, v) => [{ type: "text", text: JSON.stringify(v, null, 2) }],
    },
    timeoutMs,
    isConcurrencySafe: () => true,
    async execute(args) {
      try {
        const device = resolveDevice(devices, args.deviceId);
        const allow = device.allowActions && device.allowActions.length ? device.allowActions : defaultAllow;
        return await invoke(device, {
          action: args.action,
          args: args.args && typeof args.args === "object" ? args.args : {},
          confirm: args.confirm === true,
          timeoutMs,
          allowActions: allow,
        });
      } catch (e) {
        return { ok: false, error: e instanceof Error ? e.message : String(e) };
      }
    },
    presentCall: () => ({ card: "generic", title: "device invoke" }),
    presentResult: (_a, r) => ({ card: "generic", title: "device invoke", content: r.content }),
  });
}
