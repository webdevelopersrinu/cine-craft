# Human Behaviour — the hardest realism layer

AI people fail on behaviour before they fail on pixels. Prompt behaviour
explicitly in every shot containing a person; never leave it to the model's
defaults.

## What real humans do on camera

- **Blink.** Every 3–5 seconds, irregularly. Unblinking eyes are the #1 uncanny tell. Prompt "natural blinking".
- **Micro-expressions.** Faces rest near-neutral and flicker — a brow twitch, a half-smile forming and fading. Not a held expression for the whole clip.
- **Small head movements.** Slight nods, tilts while listening, re-orienting toward sounds.
- **Breathing.** Visible chest/shoulder rise, especially after movement or in close-ups.
- **Eye movement.** Eyes look *at things* — the other person's eyes (then briefly away), the object being handled, where they're walking. Darting or dead-locked gaze both read fake.
- **Natural pauses.** Conversation has hesitations, "thinking" looks away, overlaps. Perfectly fluent delivery reads synthetic.
- **Imperfect gestures.** Hands adjust clothing, rest, fidget, half-complete a motion. Not constant illustrative gesturing.
- **Realistic walking.** Normal pace, slight asymmetry, arms swinging naturally, weight shifting. AI walks float or glide — prompt "grounded, weight-bearing steps".
- **Real object interaction.** Fingers wrap around the cup before it lifts; weight affects posture; eyes precede the reach.

## Skin and faces

- Real skin has pores, slight unevenness, small asymmetries, stray hairs.
- Prompt for: "natural skin texture, slight facial asymmetry, realistic
  complexion". Exclude: "flawless skin, airbrushed, perfect symmetry,
  porcelain, beauty filter".
- Expressions must match the beat: someone hearing bad news doesn't smile at
  camera. Direct the emotion per shot, in acting terms: "listens, jaw
  tightens, looks down briefly".

## Lip sync and talking heads

- Lip movement matches phonemes and pace of speech; jaw and cheeks move too, not just lips.
- Talking includes eyebrow raises on emphasis, head nods on agreement points, swallowing, breath before sentences.
- Eye contact with camera (interview) breaks occasionally — glances away to recall, returns on the key phrase.

## Direction, not description

Write behaviour as a director would to an actor — verbs and beats, not
adjectives: "she sets the phone down, exhales, glances at the door, then
back" — not "sad woman". Exaggerated acting is as fake as frozen acting;
calibrate down.
