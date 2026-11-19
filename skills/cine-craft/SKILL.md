---
name: cine-craft
description: Use when creating, directing, or prompting AI-generated video — text-to-video prompts, shot lists, storyboards, video direction specs, or reviewing generated clips. Produces videos that look directed by a human filmmaker (motivated camera movement, lighting that follows the environment, natural human behaviour, story-driven editing, continuity across shots) instead of AI-looking output (waxy smooth skin, robotic camera drift, oversaturated colors, repetitive transitions, disconnected clips with no story). Works for cinematic, documentary, commercial, travel, interview, and music-video formats.
---

# Cine Craft — Human Video Direction

Direct AI video generation the way a working filmmaker would. The output of this
skill is a **video direction spec**: a shot list where every shot has a reason,
a camera, a light source, human behaviour notes, and an edit plan — then
generation prompts derived from it. Never generate "a cool clip"; always
generate shot N of a story.

Before directing, skim the reference matching the task:

| Reference | Covers |
|---|---|
| `references/cinematography.md` | Shot sizes, camera movements, lenses |
| `references/lighting-composition.md` | Lighting setups, composition rules |
| `references/human-behavior.md` | Natural gestures, faces, movement realism |
| `references/editing-storytelling.md` | Cuts, pacing, story structures per video type |
| `references/color-continuity.md` | Grading, temporal/spatial/character consistency |

## Why AI video looks like AI (never repeat these)

1. Perfectly smooth, waxy skin and flawless faces.
2. Unrealistic or floaty body movements.
3. Robotic camera moves — constant slow push-in on everything, drift with no motivation.
4. Oversaturated colors; teal-and-orange grade regardless of story.
5. Perfectly clean, sterile environments — no props, no wear, no life.
6. The same transition repeated (cross dissolve everywhere, whip pans everywhere).
7. Unnatural facial expressions — frozen smiles, no blinking, constant emoting.
8. No storytelling — disconnected pretty clips in a row.
9. Objects that change or vanish between frames.
10. Lighting that ignores the environment (shadows contradicting the window/sun).

The fix is **cinematic realism and storytelling — not adding noise or film
grain on top of slop**. Grain over a waxy face is still a waxy face.

## The rules (non-negotiable)

1. **Every camera move has a motivation.** Pan to follow a subject, dolly to
   reveal, static to let a performance breathe. If you can't say why the camera
   moves, it doesn't move. Static shots are a feature, not a failure.
2. **Vary shot sizes with intent.** Emotional beat → close-up. Geography →
   wide. Conversation → medium + over-the-shoulder coverage. Never the same
   framing twice in a row unless it's a deliberate pattern.
3. **Light must make physical sense.** Name the light source in every shot
   (window camera-left, golden-hour sun behind subject, practical lamp in
   frame). Shadows and reflections follow it. Motivated lighting only.
4. **Humans behave like humans.** Blinking, micro-expressions, breathing,
   natural pauses, imperfect gestures, realistic walking speed, eyes that look
   at things. Prompt for these explicitly; exclude "perfect skin, symmetrical
   face, constant smile".
5. **Edit follows story, not a template.** Cut on action, J/L-cuts for
   conversation, varied clip lengths (a 0.5s insert next to a 6s hold), pacing
   that matches the emotional beat. Pick cuts per moment — never one
   transition applied globally.
6. **Grade follows mood, not fashion.** Choose color from story, environment,
   time of day. White balance consistent within a scene. Not every video gets
   teal-and-orange.
7. **Continuity is a hard requirement.** Same character appearance, wardrobe,
   light direction, environment and physics across every shot of a scene.
   Carry a continuity block (character sheet + environment sheet) into every
   prompt of the sequence.
8. **Environments show life.** Wear, clutter where real life has clutter,
   weather, props that belong to the character. Sterile = AI.

## Process

1. **Intent first.** Establish: video type (cinematic / documentary /
   commercial / travel / interview / music video), subject, emotional goal,
   platform + length. Each type has its own grammar — see
   `references/editing-storytelling.md`.
2. **Story structure.** Even 15 seconds has one: establish → introduce →
   action → emotional beat → resolution (or the type-specific variant). Write
   the beats before any shots.
3. **Shot list.** For each beat: shot size, camera movement (+ its reason),
   lens feel, lighting source, composition, human behaviour notes, duration.
4. **Continuity block.** One character sheet (face, hair, wardrobe, build) and
   one environment sheet (location, time of day, light direction, key props)
   repeated verbatim in every shot prompt of the scene.
5. **Edit plan.** Cut types between shots, pacing curve, where audio leads or
   trails the cut (J/L-cuts), music/ambience notes.
6. **Write the generation prompts.** Save the direction spec as JSON (see
   `examples/coffee-commercial.json` for the shape) and run
   `node scripts/direct.mjs spec.json --out prompts/` — it validates the spec,
   lints it for the AI-tells (uniform pacing, unmotivated camera moves,
   repeated transitions, light with no physical source), and writes one
   generation prompt per shot with the continuity block and exclusions baked
   in. Fix every warning before generating.
7. **Review generated clips against the ten tells above.** A clip failing
   continuity or lighting logic gets regenerated, not graded over.

### Rendering an explainer reel directly (no gen-AI needed)

For narrated explainer reels (tech topics, listicles, tutorials), the plugin
renders the video itself: write a scene spec JSON (see
`examples/reel-spec.json`) and run
`python scripts/build_reel.py spec.json` (`--dry-run` first to check the
plan). Pipeline: edge-tts narration per scene → scene duration from the
voice-over → PIL-drawn frames piped to ffmpeg → concat → music + narration
mixed and loudness-normalized to -14 LUFS. Layouts: `title`, `rows` (items
light up in sync with narration), `photo` (Ken Burns card + code pill + pop
stat), `outro` (word stack + CTA). Needs: `pip install edge-tts numpy pillow`
and ffmpeg on PATH; photos and a display font go in the spec's assets folder.

## Knowledge architecture (what this skill thinks with)

Video Director (intent) → Storytelling → Cinematography → Camera Direction →
Lighting → Composition → Human Behaviour → Colour Grading → Editing → Audio
Design → Continuity → **final video direction spec**.

## Study sources

StudioBinder (shots, directing), American Society of Cinematographers, No Film
School (editing, lighting), ARRI (camera and lighting). Terminology in the
references follows these.
