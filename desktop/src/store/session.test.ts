import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@tauri-apps/api/core", () => ({ invoke: vi.fn().mockResolvedValue({ port: 4312, token: "test" }) }));
vi.mock("@tauri-apps/plugin-dialog", () => ({ open: vi.fn() }));

import { useSession } from "./session";

describe("session conversion", () => {
  beforeEach(() => {
    vi.stubGlobal("location", { search: "" });
    useSession.setState({ file: { path: "C:/model.stl", name: "model.stl", ext: "stl" }, convert: { status: "idle", data: null, error: null }, diff: { status: "idle", data: null, error: null }, prepareMode: "preserve", settingsSummary: null });
  });

  it("passes the chosen prepare mode to convert", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ output_path: "C:/out.3mf", output_name: "out.3mf", validated_ok: true, prepare_mode: "recommended", settings_summary: {} }) });
    vi.stubGlobal("fetch", fetchMock);
    await useSession.getState().runConvert("recommended");
    expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toMatchObject({ path: "C:/model.stl", prepare_mode: "recommended" });
  });
});
