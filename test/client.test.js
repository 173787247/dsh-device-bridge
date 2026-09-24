import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { listDevices, resolveDevice } from "../lib/companion_client.js";

describe("device-bridge", () => {
  it("lists devices", () => {
    const d = listDevices([{ id: "p", baseUrl: "http://x/", kind: "phone" }]);
    assert.equal(d[0].kind, "phone");
  });
  it("resolves", () => {
    assert.equal(resolveDevice([{ id: "p", baseUrl: "http://x" }], "p").id, "p");
  });
});
