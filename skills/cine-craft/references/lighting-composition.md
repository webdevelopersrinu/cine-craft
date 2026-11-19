# Lighting & Composition

## Lighting — the light must exist in the world

Every shot prompt names its light source and direction. If a person stands
near a window, the bright side of their face points at the window, the shadow
side away, and the room's bounce fills softly. Shadows, highlights and
reflections must make physical sense — this single rule kills most AI tells.

### Setups to know

- **Natural light:** sun/sky through windows or outdoors. State time of day; it defines everything.
- **Three-point:** key (main source, sets direction), fill (softens shadows, weaker), backlight (separates subject from background). The interview standard.
- **Practical lighting:** lamps, neon signs, screens, candles *visible in frame* motivate the light. Great for realism — the viewer sees why the light exists.
- **Motivated lighting:** every light in the scene is justified by a source the world contains, even if off-frame (door ajar, streetlight). The umbrella rule.
- **High-key:** bright, low contrast, minimal shadows — commercials, comedy, clean product.
- **Low-key:** dark, high contrast, deep shadows — drama, tension, noir.
- **Golden hour:** low warm sun, long soft shadows — travel and emotional exteriors. Don't put golden-hour glow on an indoor office scene.

### Prompting rules

- Name source + direction + quality: "soft window light from camera-left, warm practical lamp in background, dim ambient fill".
- One scene = one light logic. The sun doesn't move between shots of the same moment (see color-continuity.md).
- Exclude: "glowing skin, rim light on everything, lens flare with no source, evenly lit from nowhere".

## Composition — where the viewer looks

1. **Rule of thirds:** subject on a third line, eyes near a top intersection. The default.
2. **Symmetry:** centered, balanced — use *deliberately* for formality, power, unease. Not the default (centered-everything is an AI tell).
3. **Leading lines:** roads, rails, corridors, shadows pull the eye to the subject.
4. **Negative space:** empty space says isolation, scale, calm. Let shots breathe.
5. **Frame within a frame:** doorways, windows, mirrors — depth and voyeurism.
6. **Depth and layering — foreground / midground / background:** every shot wants all three. A flat subject-on-backdrop frame reads synthetic; put something soft in the foreground edge.
7. **Headroom:** small gap above the head — too much reads amateur, cropped scalp reads accidental (unless ECU).
8. **Look room / lead room:** space in front of a gaze or movement direction. A subject walking right sits in the left third.

**Per-shot prompt line:** composition rule + layers, e.g. "rule of thirds,
subject left third looking right, out-of-focus market stall foreground right,
street depth behind."
