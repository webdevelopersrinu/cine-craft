import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";

const usage = "usage: node direct.mjs <spec.json> [--out prompts/]";
const args = process.argv.slice(2);
const positionals = [];
let outDir;
for (let i = 0; i < args.length; i++) {
  if (args[i] === "--out") {
    outDir = args[++i];
    if (!outDir || outDir.startsWith("--")) {
      console.error("--out needs a directory, like --out prompts/");
      process.exit(1);
    }
  } else if (!args[i].startsWith("--")) {
    positionals.push(args[i]);
  }
}
const [specPath] = positionals;
if (!specPath) {
  console.error(usage);
  process.exit(1);
}

let spec;
try {
  spec = JSON.parse(readFileSync(resolve(specPath), "utf8"));
} catch (error) {
  console.error(`cannot read spec: ${error.message}`);
  process.exit(1);
}

// --- validate: a spec missing these cannot produce a coherent video ---
const errors = [];
for (const field of ["title", "type", "character", "environment", "shots"]) {
  if (!spec[field]) errors.push(`spec is missing "${field}"`);
}
const types = ["cinematic", "documentary", "commercial", "travel", "interview", "music-video"];
if (spec.type && !types.includes(spec.type)) {
  errors.push(`"type" must be one of ${types.join(", ")}, got "${spec.type}"`);
}
const shots = Array.isArray(spec.shots) ? spec.shots : [];
if (spec.shots && shots.length === 0) errors.push('"shots" must be a non-empty array');
shots.forEach((shot, i) => {
  for (const field of ["beat", "size", "camera", "lighting", "action", "duration"]) {
    if (!shot[field]) errors.push(`shot ${i + 1} is missing "${field}"`);
  }
  if (typeof shot.duration === "number" && shot.duration <= 0) {
    errors.push(`shot ${i + 1} duration must be > 0 seconds`);
  }
});
if (errors.length) {
  errors.forEach((error) => console.error(`error: ${error}`));
  process.exit(1);
}

// --- lint: the AI-tells a human director would catch in review ---
const warnings = [];
const durations = new Set(shots.map((shot) => shot.duration));
if (shots.length >= 3 && durations.size === 1) {
  warnings.push(`uniform pacing: every shot is ${shots[0].duration}s — vary clip length with the beat (a 0.5s insert next to a 6s hold)`);
}
shots.forEach((shot, i) => {
  if (!/static|locked/i.test(shot.camera) && !shot.reason) {
    warnings.push(`shot ${i + 1}: camera "${shot.camera}" has no "reason" — every move needs a motivation, or make it static`);
  }
  if (i >= 2 && shot.transition && shot.transition === shots[i - 1].transition && shot.transition === shots[i - 2].transition) {
    warnings.push(`shots ${i - 1}–${i + 1}: transition "${shot.transition}" repeated 3× in a row — vary cuts per moment, not by template`);
  }
  if (i >= 1 && shot.size === shots[i - 1].size && i >= 2 && shot.size === shots[i - 2].size) {
    warnings.push(`shots ${i - 1}–${i + 1}: three "${shot.size}" shots in a row — vary shot size with emotional intensity`);
  }
  if (!/(window|sun|lamp|neon|practical|golden|overcast|screen|candle|streetlight|sky|key light|three-point|moon|fire)/i.test(shot.lighting)) {
    warnings.push(`shot ${i + 1}: lighting "${shot.lighting}" names no physical source — light must exist in the world`);
  }
});
warnings.forEach((warning) => console.warn(`warning: ${warning}`));

// --- emit: one generation prompt per shot, continuity block verbatim in each ---
const EXCLUDE =
  "waxy or airbrushed skin, perfect facial symmetry, oversaturated colors, teal-and-orange grade, " +
  "aimless camera drift, constant slow push-in, lens flare without a source, sterile empty environment, " +
  "frozen expression, unblinking eyes, floating or gliding walk, morphing objects between frames";

const prompt = (shot, i) =>
  [
    `Shot ${i + 1} of ${shots.length} — ${spec.title} (${spec.type}). Beat: ${shot.beat}.`,
    `${shot.size} shot, ${shot.camera}${shot.reason ? ` (motivation: ${shot.reason})` : ""}.${shot.lens ? ` Lens: ${shot.lens}.` : ""}`,
    `Lighting: ${shot.lighting}.${shot.composition ? ` Composition: ${shot.composition}.` : ""}`,
    `Action: ${shot.action} Natural human behaviour: irregular blinking, micro-expressions, breathing, grounded weight-bearing movement.`,
    `CHARACTER (keep identical in every shot): ${spec.character}`,
    `ENVIRONMENT (keep identical in every shot): ${spec.environment}`,
    `Duration: ${shot.duration}s. Exclude: ${EXCLUDE}.`,
  ].join("\n");

const prompts = shots.map(prompt);
if (outDir) {
  const dir = resolve(outDir);
  mkdirSync(dir, { recursive: true });
  prompts.forEach((text, i) => writeFileSync(join(dir, `shot-${String(i + 1).padStart(2, "0")}.txt`), text + "\n"));
  const total = shots.reduce((sum, shot) => sum + shot.duration, 0);
  console.log(`wrote ${prompts.length} shot prompts to ${dir} (${total}s total${warnings.length ? `, ${warnings.length} warnings` : ""})`);
} else {
  console.log(prompts.join("\n\n---\n\n"));
}
