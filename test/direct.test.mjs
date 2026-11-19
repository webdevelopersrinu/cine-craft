import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const script = fileURLToPath(new URL("../skills/cine-craft/scripts/direct.mjs", import.meta.url));
const example = fileURLToPath(new URL("../examples/coffee-commercial.json", import.meta.url));

const run = (...args) => execFileSync("node", [script, ...args], { encoding: "utf8" });

test("example spec produces one prompt per shot with the continuity block in each", () => {
  const dir = mkdtempSync(join(tmpdir(), "cine-"));
  const stdout = run(example, "--out", dir);
  assert.match(stdout, /wrote 5 shot prompts .* \(18s total\)/);
  const files = readdirSync(dir).sort();
  assert.deepEqual(files, ["shot-01.txt", "shot-02.txt", "shot-03.txt", "shot-04.txt", "shot-05.txt"]);
  for (const file of files) {
    const text = readFileSync(join(dir, file), "utf8");
    assert.match(text, /CHARACTER \(keep identical in every shot\): Woman in her 30s/);
    assert.match(text, /ENVIRONMENT \(keep identical in every shot\): Small neighbourhood coffee shop/);
    assert.match(text, /Exclude: waxy or airbrushed skin/);
  }
  assert.match(readFileSync(join(dir, "shot-02.txt"), "utf8"), /motivation: draw the viewer/);
});

test("lints the AI-tells: uniform pacing, unmotivated moves, repeated transitions, sourceless light", async () => {
  const dir = mkdtempSync(join(tmpdir(), "cine-"));
  const shot = (over) => ({
    beat: "action", size: "medium", camera: "slow push in", lighting: "cinematic glow",
    action: "x", duration: 3, transition: "cross dissolve", ...over,
  });
  const spec = { title: "t", type: "cinematic", character: "c", environment: "e", shots: [shot(), shot(), shot()] };
  const file = join(dir, "slop.json");
  writeFileSync(file, JSON.stringify(spec));
  const { spawnSync } = await import("node:child_process");
  const result = spawnSync("node", [script, file, "--out", dir], { encoding: "utf8" });
  assert.equal(result.status, 0);
  assert.match(result.stderr, /uniform pacing/);
  assert.match(result.stderr, /no "reason"/);
  assert.match(result.stderr, /repeated 3×/);
  assert.match(result.stderr, /names no physical source/);
  assert.match(result.stdout, /\d+ warnings/);
});

test("build_reel.py dry-run validates and plans the example reel spec", () => {
  const reel = fileURLToPath(new URL("../skills/cine-craft/scripts/build_reel.py", import.meta.url));
  const spec = fileURLToPath(new URL("../examples/reel-spec.json", import.meta.url));
  const out = execFileSync("python", [reel, spec, "--dry-run"], { encoding: "utf8" });
  assert.match(out, /dry-run ok: 4 scenes -> my_reel\.mp4/);
  assert.match(out, /\[title \] VALKEY/);
  assert.throws(() => execFileSync("python", [reel, spec.replace("reel-spec", "coffee-commercial"), "--dry-run"], { encoding: "utf8", stdio: "pipe" }));
});

test("rejects a spec missing required fields", () => {
  const dir = mkdtempSync(join(tmpdir(), "cine-"));
  const file = join(dir, "bad.json");
  writeFileSync(file, JSON.stringify({ title: "t", shots: [{ beat: "x" }] }));
  assert.throws(() => run(file), /missing/);
});
