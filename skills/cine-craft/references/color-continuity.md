# Colour Grading & Continuity

## Colour grading — mood from story, not fashion

Work the grade in this order:

1. **White balance** — correct first; skin tones believable, whites neutral (unless a cast is motivated: candlelight, neon).
2. **Contrast** — set blacks and whites for the mood: low-key drama holds deep shadows; high-key commercial lifts them.
3. **Highlights / shadows / midtones** — protect highlight detail (blown windows are fine only if motivated); skin lives in midtones.
4. **Saturation** — restrained. Oversaturation is a core AI tell. Real colour is duller than you remember.
5. **Colour temperature** — warm for comfort/nostalgia/golden hour, cool for isolation/night/clinical. Must match the lighting in frame.
6. **Colour harmony** — pick a palette from the scene (wardrobe + location + light) and grade toward it; complementary or analogous, two to three hues.
7. **LUTs / film emulation** — a finishing flavor on a corrected image, never a fix for a broken one.

**Not every video gets teal-and-orange.** Choose from story, environment,
mood, time of day. One scene = one grade; the grade may evolve across the
story arc (warm open → desaturated low point → warm return), which is itself
storytelling.

## Continuity — the believability contract

These consistencies are hard requirements across every shot of a scene.
Violating any one breaks the video regardless of per-shot quality.

| Concept | What must hold |
|---|---|
| Temporal consistency | Appearance stable frame to frame — no flicker, no morphing |
| Spatial consistency | Objects keep positions and relationships between shots |
| Motion continuity | Movement flows across cuts; direction of travel preserved |
| Character consistency | Same face, hair, build, wardrobe in every shot |
| Physics consistency | Gravity, weight, collisions behave; cloth and hair follow motion |
| Lighting continuity | Light direction and quality constant within the scene |
| Scene continuity | Environment, weather, time of day, props persist |
| Depth of field | Focus logic consistent — same lens feel within coverage |
| Motion blur | Moving things blur naturally; no frozen-crisp fast motion |
| Lens characteristics | Perspective/distortion consistent within a scene |

### Worked example — person walks left to right across a sequence

Across every shot: clothes identical; face stable; travel stays left→right
(screen direction — don't cross the 180° line); shadow falls away from the
established sun; background objects persist; steps bear weight.

### The continuity block (paste into every shot prompt of a scene)

**Character sheet:** age range, face description, hair, build, exact wardrobe
items and colors, distinguishing detail (glasses, watch).
**Environment sheet:** location, time of day, weather, light source +
direction, 3–5 key props and where they sit.

Write both once per scene, then repeat them verbatim in each shot's prompt.
Any generated clip contradicting the block is regenerated — grading or grain
cannot repair a continuity break.
