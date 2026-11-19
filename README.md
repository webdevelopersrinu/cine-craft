<div align="center">

# 🎬 Cine Craft

**Direct AI video generation like a human filmmaker.**

A Claude Code plugin that replaces AI-video defaults — waxy skin, robotic camera drift, teal-and-orange everything — with real filmmaking craft: motivated cameras, physical lighting, natural human behaviour, story-driven editing, and hard continuity.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-blueviolet)](https://docs.claude.com/en/docs/claude-code)
[![Node](https://img.shields.io/badge/Node-%E2%89%A518-brightgreen)](https://nodejs.org)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![Tests](https://img.shields.io/badge/tests-passing-success)](test/)

[Why](#-why-cine-craft) · [Install](#-installation) · [Quick Start](#-quick-start) · [How It Works](#-how-it-works) · [Tooling](#-tooling) · [Knowledge Base](#-knowledge-base) · [Contributing](#-contributing)

</div>

---

## 🎯 Why Cine Craft

Every AI-generated video fails the same ten ways:

| # | AI tell | Cine Craft rule |
|---|---------|-----------------|
| 1 | Waxy, perfectly smooth skin | Natural skin texture, slight asymmetry — prompted explicitly |
| 2 | Floaty, unrealistic body movement | Grounded, weight-bearing motion |
| 3 | Robotic camera drift on every shot | **Every camera move needs a motivation** — or it's static |
| 4 | Oversaturated colors | Grade from story, mood, and time of day |
| 5 | Sterile, perfectly clean environments | Wear, props, and life in every frame |
| 6 | The same transition repeated forever | Cuts chosen per moment, never by template |
| 7 | Frozen or exaggerated expressions | Blinking, micro-expressions, natural pauses |
| 8 | Disconnected pretty clips, no story | Every shot is shot *N* of a story spine |
| 9 | Objects morphing between frames | A continuity block repeated verbatim in every prompt |
| 10 | Lighting from nowhere | Light must have a physical source in the world |

> **The fix is cinematic realism and storytelling — not film grain on top of slop.** Grain over a waxy face is still a waxy face.

## 📦 Installation

```bash
# In Claude Code
/plugin marketplace add webdevelopersrinu/cine-craft
/plugin install cine-craft
```

Or clone and add locally:

```bash
git clone https://github.com/webdevelopersrinu/cine-craft.git
/plugin marketplace add ./cine-craft
```

**Optional** — only for the built-in reel renderer:

```bash
pip install edge-tts numpy pillow   # + ffmpeg on PATH
```

## 🚀 Quick Start

Ask Claude for any video and the skill takes over:

```
Create a 30-second commercial for a neighbourhood coffee shop
```

Cine Craft produces a **video direction spec** — story beats → shot list →
continuity block → edit plan — then per-shot generation prompts with realism
direction and exclusions baked in. Never "a cool clip"; always shot N of a story.

### Generate prompts from a spec

```bash
node skills/cine-craft/scripts/direct.mjs examples/coffee-commercial.json --out prompts/
```

```
wrote 5 shot prompts to prompts/ (18s total)
```

Every prompt carries the character sheet, environment sheet, behaviour
direction, and the exclusion list. The linter warns on uniform pacing,
unmotivated camera moves, repeated transitions, and light with no source —
**fix every warning before generating.**

### Render a narrated explainer reel (no gen-AI needed)

```bash
python skills/cine-craft/scripts/build_reel.py examples/reel-spec.json --dry-run
python skills/cine-craft/scripts/build_reel.py examples/reel-spec.json
```

TTS narration → synced visuals → music → loudness-normalized vertical MP4,
rendered entirely locally with PIL + ffmpeg.

## ⚙️ How It Works

```
 Idea ──▶ Video Director (intent, type, platform)
              │
              ▼
        Story beats  (establish → introduce → action → emotion → resolve)
              │
              ▼
        Shot list    (size · camera + motivation · lens · light source ·
              │       composition · behaviour · duration)
              ▼
        Continuity block  (character sheet + environment sheet,
              │            repeated verbatim in every prompt)
              ▼
        Edit plan    (cut types · pacing curve · J/L-cuts · audio)
              │
              ▼
        Per-shot generation prompts  ──▶  your video model
              │
              ▼
        Review vs. the 10 tells  →  regenerate failures, never grade over
```

Six video grammars supported, each with its own rules: **cinematic ·
documentary · commercial · travel/lifestyle · interview · music video**.

## 🛠 Tooling

| Tool | What it does |
|------|--------------|
| [`direct.mjs`](skills/cine-craft/scripts/direct.mjs) | Validates a direction spec, lints it for AI tells, emits one generation prompt per shot. Zero dependencies — pure Node. |
| [`build_reel.py`](skills/cine-craft/scripts/build_reel.py) | Renders narrated explainer reels end-to-end: edge-tts voice-over, PIL-drawn frames piped to ffmpeg, scene timing driven by narration length, -14 LUFS master. Layouts: `title` · `rows` · `photo` · `outro`. |

```bash
npm test   # validates both tools against the example specs
```

## 📚 Knowledge Base

The skill reasons with five reference modules:

| Module | Covers |
|--------|--------|
| [cinematography.md](skills/cine-craft/references/cinematography.md) | 9 shot sizes (EWS→ECU, OTS, POV), 9 camera movements with valid motivations, lens feel, conversation coverage |
| [lighting-composition.md](skills/cine-craft/references/lighting-composition.md) | Three-point, practical, motivated, high/low-key, golden hour · rule of thirds, leading lines, depth layering, headroom |
| [human-behavior.md](skills/cine-craft/references/human-behavior.md) | Blinking, micro-expressions, breathing, grounded walking, lip sync — written as direction to an actor |
| [editing-storytelling.md](skills/cine-craft/references/editing-storytelling.md) | Cut vocabulary (J/L-cuts, match cut, cut on action), pacing, audio design, per-type story grammar |
| [color-continuity.md](skills/cine-craft/references/color-continuity.md) | Grading order of operations, the 10-point consistency contract, the continuity block pattern |

## 📁 Project Structure

```
cine-craft/
├── .claude-plugin/
│   └── plugin.json                 # plugin manifest
├── skills/cine-craft/
│   ├── SKILL.md                    # director brain: rules + process
│   ├── references/                 # the five knowledge modules
│   └── scripts/
│       ├── direct.mjs              # spec validator + prompt generator
│       └── build_reel.py           # local explainer-reel renderer
├── examples/
│   ├── coffee-commercial.json      # 5-shot direction spec
│   └── reel-spec.json              # explainer-reel scene spec
└── test/
    └── direct.test.mjs             # node --test suite
```

## 🧪 Spec Reference

<details>
<summary><b>Direction spec</b> (for <code>direct.mjs</code>)</summary>

```jsonc
{
  "title": "Morning at Marigold Coffee",
  "type": "commercial",            // cinematic | documentary | commercial | travel | interview | music-video
  "character": "…",                // character sheet — repeated in every prompt
  "environment": "…",              // environment sheet — repeated in every prompt
  "shots": [{
    "beat": "establishing",        // story beat this shot serves
    "size": "wide",                // EWS → ECU
    "camera": "static locked-off", // movement…
    "reason": "…",                 // …and its motivation (required unless static)
    "lens": "35mm",
    "lighting": "window light camera-left",   // must name a physical source
    "composition": "rule of thirds, …",
    "action": "…",                 // directed like notes to an actor
    "duration": 4,
    "transition": "cut on action"
  }]
}
```
</details>

<details>
<summary><b>Reel spec</b> (for <code>build_reel.py</code>)</summary>

```jsonc
{
  "output": "my_reel.mp4",
  "assets": "video_assets",        // fonts + photos live here
  "voice": "en-US-AndrewNeural",
  "bgm": true,
  "scenes": [{
    "id": "intro", "label": "MY TOPIC",
    "layout": "title",             // title | rows | photo | outro
    "narration": "…"               // scene length follows the voice-over
  }]
}
```
</details>

## 🤝 Contributing

Issues and PRs welcome — especially new reference knowledge, additional reel
layouts, and per-model prompt dialects. Run `npm test` before submitting.

## 📄 License

[MIT](LICENSE) © [Srinu Desetti](https://github.com/webdevelopersrinu)

---

<div align="center">
<sub>Built for creators who want AI video that doesn't look like AI video.</sub>
</div>
