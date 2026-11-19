# Cine Craft

A Claude Code plugin that directs AI video generation like a human filmmaker.

AI-generated video has tells: waxy smooth skin, robotic camera drift,
oversaturated teal-and-orange, uniform 3-second clips, lighting from nowhere,
characters that morph between shots, and no story. Cine Craft replaces those
defaults with real filmmaking craft — it turns a video idea into a **video
direction spec** (story beats → shot list → continuity block → edit plan) and
then into per-shot generation prompts with explicit realism direction and
exclusions.

## What it knows

- **Cinematography** — shot sizes (EWS→ECU, OTS, POV), motivated camera movement, lens feel
- **Lighting** — three-point, practical, motivated, high/low-key; light that follows the environment
- **Composition** — rule of thirds, leading lines, depth layering, headroom/look room
- **Human behaviour** — blinking, micro-expressions, grounded walking, natural pauses, real object interaction
- **Editing & storytelling** — cut vocabulary (J/L-cuts, match cuts, cut on action), pacing, story spines per video type
- **Colour & continuity** — grading from mood, and the hard consistency contract (character, lighting, physics, scene) across shots

Supports six video grammars: cinematic, documentary, commercial, travel/lifestyle, interview, music video.

## Install

```
/plugin marketplace add <this repo or path>
/plugin install cine-craft
```

Then ask Claude to direct any video: *"Create a 30s commercial for a coffee
shop"* — the skill produces the direction spec and generation prompts instead
of a generic clip description.

## Structure

```
skills/cine-craft/
  SKILL.md                      # director brain: rules, process, AI-tells
  references/
    cinematography.md           # shots, movements, lenses
    lighting-composition.md     # light setups, framing rules
    human-behavior.md           # behavioural realism
    editing-storytelling.md     # cuts, pacing, per-type story grammar
    color-continuity.md         # grading + consistency contract
```

## License

MIT
