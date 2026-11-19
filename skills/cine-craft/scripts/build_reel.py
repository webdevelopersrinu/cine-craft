# -*- coding: utf-8 -*-
"""
Data-driven vertical reel builder, generalized from build_valkey_reel_pro.py.

Pipeline (same engine as the reference):
  scenes from a JSON spec -> edge-tts narration per scene (cached, retried)
  -> scene duration = voice-over length + pad -> PIL frames piped raw to
  ffmpeg per scene (parallel) -> concat -> narration + synthesized BGM mixed,
  loudness-normalized to -14 LUFS -> mp4.

usage: python build_reel.py <spec.json> [--dry-run]

Spec shape (see examples/reel-spec.json):
{
  "output": "my_reel.mp4", "assets": "video_assets",
  "width": 1080, "height": 1920, "fps": 30,
  "voice": "en-US-AndrewNeural", "font": "ConcertOne.ttf", "bgm": true,
  "scenes": [
    {"id": "intro", "label": "MY TOPIC", "narration": "...",
     "layout": "title", "headline": "NOT just a cache.",
     "lines": ["8 real-world uses", "all in memory"]},
    {"id": "x", "label": "PART 1", "narration": "...",
     "layout": "rows", "headline": "The pieces",
     "rows": [["Strings", "text & numbers", "cyan"], ...]},
    {"id": "y", "label": "PART 2", "narration": "...",
     "layout": "photo", "headline": "Caching", "photo": "img_cache.jpg",
     "code": "SET products EX 60", "pop": "0.2 ms"},
    {"id": "outro", "label": "THAT'S IT", "narration": "...",
     "layout": "outro", "words": ["cache", "broker"],
     "cta": "comment below · hit like"}
  ]
}
layouts: title | rows | photo | outro
"""
import json, math, os, sys, wave, asyncio, subprocess

COLORS = {
    "ink": (240, 242, 252), "blue": (110, 145, 255), "cyan": (90, 210, 250),
    "pink": (240, 80, 140), "green": (90, 210, 130), "yellow": (255, 200, 40),
    "red": (240, 90, 90), "grey": (160, 165, 185), "dim": (90, 95, 120),
}
LAYOUTS = {
    "title": ["headline"], "rows": ["headline", "rows"],
    "photo": ["headline", "photo"], "outro": ["words"],
}

def load_spec(path):
    with open(path, encoding="utf-8") as fh:
        spec = json.load(fh)
    errors = []
    for field in ["output", "scenes"]:
        if not spec.get(field):
            errors.append(f'spec is missing "{field}"')
    for i, sc in enumerate(spec.get("scenes") or []):
        for field in ["id", "label", "narration", "layout"]:
            if not sc.get(field):
                errors.append(f'scene {i + 1} is missing "{field}"')
        layout = sc.get("layout")
        if layout and layout not in LAYOUTS:
            errors.append(f'scene {i + 1}: unknown layout "{layout}" (use {"/".join(LAYOUTS)})')
        else:
            for field in LAYOUTS.get(layout, []):
                if not sc.get(field):
                    errors.append(f'scene {i + 1} ({layout}) is missing "{field}"')
        for row in sc.get("rows") or []:
            if len(row) != 3 or row[2] not in COLORS:
                errors.append(f'scene {i + 1}: each row is [title, sub, color], colors: {"/".join(COLORS)}')
    if errors:
        for error in errors:
            print("error:", error, file=sys.stderr)
        sys.exit(1)
    spec.setdefault("width", 1080); spec.setdefault("height", 1920)
    spec.setdefault("fps", 30); spec.setdefault("voice", "en-US-AndrewNeural")
    spec.setdefault("assets", "video_assets"); spec.setdefault("bgm", True)
    spec.setdefault("font", "ConcertOne.ttf")
    return spec

# ------------------------------------------------------------------ audio --
SR = 48000

async def make_tts(spec, assets):
    import edge_tts
    for sc in spec["scenes"]:
        mp3 = os.path.join(assets, f'vo_{sc["id"]}.mp3')
        if os.path.exists(mp3):
            continue
        for attempt in range(5):
            try:
                await edge_tts.Communicate(sc["narration"], spec["voice"]).save(mp3)
                print("tts", sc["id"]); break
            except Exception:
                if os.path.exists(mp3): os.remove(mp3)
                if attempt == 4: raise
                await asyncio.sleep(3 * (attempt + 1))
        await asyncio.sleep(1.0)
    for sc in spec["scenes"]:
        wv = os.path.join(assets, f'vo_{sc["id"]}.wav')
        if not os.path.exists(wv):
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error",
                            "-i", os.path.join(assets, f'vo_{sc["id"]}.mp3'),
                            "-ar", str(SR), "-ac", "1", wv], check=True)

def wav_data(path):
    import numpy as np
    with wave.open(path, "rb") as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0

def bgm(total):
    import numpy as np
    n = int(total * SR); out = np.zeros(n)
    chords = [(220, 261.6, 329.6), (174.6, 220, 261.6), (261.6, 329.6, 392), (196, 246.9, 293.7)]
    bar = 3.2; tb = np.arange(int(bar * SR)) / SR
    env = np.ones(len(tb))
    na, nr = int(1.0 * SR), int(1.2 * SR)
    env[:na] = np.linspace(0, 1, na); env[-nr:] *= np.linspace(1, 0, nr)
    i = 0
    while i < n:
        ch = chords[(i // int(bar * SR)) % 4]
        seg = sum(np.sin(2 * np.pi * f * tb) + 0.25 * np.sin(2 * np.pi * f / 2 * tb) for f in ch) / 6 * env
        m = min(len(seg), n - i); out[i:i + m] += seg[:m]; i += m
    out *= 0.04
    kt = np.arange(int(0.16 * SR)) / SR
    kick = np.sin(2 * np.pi * 55 * kt) * np.exp(-kt * 26) * 0.08
    for j in range(0, n - len(kick), int(0.6 * SR)):
        out[j:j + len(kick)] += kick
    return out

# ----------------------------------------------------------------- frames --
def renderer(spec):
    """Build the per-frame draw function set; imports PIL lazily so --dry-run needs nothing."""
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    W, H = spec["width"], spec["height"]
    assets = spec["assets"]

    def F(s): return ImageFont.truetype(os.path.join(assets, spec["font"]), s)
    def MONO(s): return ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", s)
    def UI(s): return ImageFont.truetype(r"C:\Windows\Fonts\segoeuisl.ttf", s)
    C = COLORS
    def ease(t): t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3
    def tc(d, xy, s, f, fill): d.text(xy, s, font=f, fill=fill, anchor="mm")
    def rr(d, box, r, **kw): d.rounded_rectangle(box, radius=r, **kw)

    small = Image.new("RGB", (108, 192))
    px = small.load()
    for y in range(192):
        for x in range(108):
            fy = y / 192; fx = x / 108
            r = 16 + 26 * fy + 10 * fx; g = 14 + 10 * fy; b = 38 + 48 * fy + 14 * (1 - fx)
            boost = max(0, 1 - math.hypot(fx - 0.5, fy - 0.16) * 2.1) * 36
            dark = max(0, math.hypot(fx - 0.5, fy - 0.5) - 0.42) * 90
            px[x, y] = (int(max(0, r + boost - dark)), int(max(0, g + boost * 0.9 - dark)),
                        int(max(0, b + boost - dark)))
    BG = small.resize((W, H), Image.BICUBIC)

    size = 360
    g = Image.new("L", (size, size), 0)
    gd = ImageDraw.Draw(g)
    for rad in range(size // 2, 0, -4):
        gd.ellipse([size/2 - rad]*2 + [size/2 + rad]*2, fill=int(110 * (1 - rad / (size / 2)) ** 2))
    GLOW = g.filter(ImageFilter.GaussianBlur(10))

    def glow(img, center, color, scale=1.0):
        s = max(24, int(360 * scale))
        gs = GLOW.resize((s, s))
        img.paste(Image.new("RGB", (s, s), color), (int(center[0] - s / 2), int(center[1] - s / 2)), gs)

    photos = {}
    def photo(name):
        if name not in photos:
            photos[name] = Image.open(os.path.join(assets, name)).convert("RGB")
        return photos[name]

    def chrome(img, d, label, frac):
        f = F(34)
        tw = d.textbbox((0, 0), label, font=f)[2]
        rr(d, [(W - tw) / 2 - 44, 96, (W + tw) / 2 + 44, 172], 38, fill=(20, 22, 44), outline=C["cyan"], width=3)
        tc(d, (W / 2, 134), label, f, C["cyan"])
        d.rectangle([0, H - 14, W, H], fill=(28, 30, 56))
        d.rectangle([0, H - 14, int(W * frac), H], fill=C["yellow"])

    def photo_card(img, d, name, box, t):
        x0, y0, x1, y1 = box; bw, bh = x1 - x0, y1 - y0
        rr(d, [x0 + 10, y0 + 14, x1 + 10, y1 + 14], 26, fill=(8, 8, 18))
        p = photo(name); pw, ph = p.size
        ar = bw / bh
        cw, ch = (int(ph * ar), ph) if pw / ph > ar else (pw, int(pw / ar))
        z = 1 + 0.10 * t
        cw2, ch2 = int(cw / z), int(ch / z)
        crop = p.crop(((pw - cw2) // 2, (ph - ch2) // 2, (pw + cw2) // 2, (ph + ch2) // 2)).resize((bw, bh))
        mask = Image.new("L", (bw, bh), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, bw, bh], radius=26, fill=255)
        img.paste(crop, (x0, y0), mask)
        rr(d, box, 26, outline=C["cyan"], width=5)

    def draw(sc, img, d, t):
        layout = sc["layout"]
        if layout == "title":
            glow(img, (W / 2, 560), (60, 80, 200), 2.6)
            tc(d, (W / 2, 560), sc.get("title", sc["label"]), F(110), C["ink"])
            if t > 0.3:
                tc(d, (W / 2, 860), sc["headline"], F(78), C["pink"])
            for i, line in enumerate(sc.get("lines", [])):
                if t > 0.5 + i * 0.12:
                    tc(d, (W / 2, 1010 + i * 100), line, UI(40), C["grey"] if i else C["ink"])
        elif layout == "rows":
            tc(d, (W / 2, 290), sc["headline"], F(72), C["ink"])
            for i, (title, sub, color) in enumerate(sc["rows"]):
                lit = t >= i / len(sc["rows"]) * 0.9 + 0.05
                y = 420 + i * 300; col = C[color]
                if lit:
                    glow(img, (150, y + 75), col, 0.9)
                    rr(d, [90, y, W - 90, y + 150], 26, fill=(24, 27, 52), outline=col, width=6)
                else:
                    rr(d, [90, y, W - 90, y + 150], 26, fill=(18, 20, 40), outline=(55, 60, 92), width=3)
                d.text((138, y + 24), title, font=F(48), fill=col if lit else C["dim"])
                d.text((138, y + 88), sub, font=UI(32), fill=C["grey"] if lit else (70, 75, 100))
        elif layout == "photo":
            tc(d, (W / 2, 280), sc["headline"], F(80), C["cyan"])
            photo_card(img, d, sc["photo"], (110, 380, W - 110, 1020), t)
            if sc.get("code") and t > 0.35:
                rr(d, [150, 1120, W - 150, 1210], 20, fill=(20, 22, 44), outline=C["green"], width=4)
                tc(d, (W / 2, 1165), sc["code"], MONO(42), C["green"])
            if sc.get("pop") and t > 0.6:
                glow(img, (W / 2, 1400), (120, 90, 20), 1.4)
                tc(d, (W / 2, 1400), sc["pop"], F(100), C["yellow"])
        elif layout == "outro":
            glow(img, (W / 2, 520), (70, 60, 160), 2.2)
            tc(d, (W / 2, 520), sc.get("title", sc["label"]), F(96), C["ink"])
            palette = ["cyan", "pink", "yellow", "green"]
            for i, word in enumerate(sc["words"]):
                if t > 0.3 + i * 0.09:
                    tc(d, (W / 2, 880 + i * 110), word, F(64), C[palette[i % 4]])
            if sc.get("cta") and t > 0.72:
                tc(d, (W / 2, 1500), sc["cta"], UI(38), C["yellow"])
        return img

    return BG, chrome, draw

# ------------------------------------------------------------------- main --
def render_scene(spec, BG, chrome, draw, idx, sc, dur, start, total):
    from PIL import Image, ImageDraw
    W, H, FPS = spec["width"], spec["height"], spec["fps"]
    seg = os.path.join(spec["assets"], f"seg_{idx:02d}.mp4")
    nf = int(dur * FPS)
    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p", seg],
        stdin=subprocess.PIPE)
    for f in range(nf):
        t = f / nf
        img = BG.copy()
        d = ImageDraw.Draw(img)
        draw(sc, img, d, t)
        chrome(img, d, sc["label"], (start + t * dur) / total)
        edge = min(f, nf - f) / (0.3 * FPS)
        if edge < 1:
            img = Image.eval(img, lambda px: int(px * (0.3 + 0.7 * edge)))
        proc.stdin.write(img.tobytes())
    proc.stdin.close(); proc.wait()
    return seg

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print("usage: python build_reel.py <spec.json> [--dry-run]", file=sys.stderr)
        sys.exit(1)
    spec = load_spec(args[0])
    os.chdir(os.path.dirname(os.path.abspath(args[0])) or ".")
    if "--dry-run" in sys.argv:
        for i, sc in enumerate(spec["scenes"]):
            words = len(sc["narration"].split())
            print(f'{i + 1:2d}. [{sc["layout"]:6s}] {sc["label"]:20s} ~{words / 2.5:4.1f}s  "{sc["narration"][:50]}..."')
        print(f'dry-run ok: {len(spec["scenes"])} scenes -> {spec["output"]}')
        return
    import numpy as np
    assets = spec["assets"]
    os.makedirs(assets, exist_ok=True)
    asyncio.run(make_tts(spec, assets))
    vo = {sc["id"]: wav_data(os.path.join(assets, f'vo_{sc["id"]}.wav')) for sc in spec["scenes"]}
    durs = [max(3.5, len(vo[sc["id"]]) / SR + 0.6) for sc in spec["scenes"]]
    total = sum(durs)
    print("reel length:", round(total, 1), "s")

    master = np.zeros(int((total + 1) * SR), dtype=np.float32)
    t0 = 0.0
    for sc, dur in zip(spec["scenes"], durs):
        i0 = int((t0 + 0.3) * SR)
        a = vo[sc["id"]]; master[i0:i0 + len(a)] += a * 0.95
        t0 += dur
    if spec["bgm"]:
        pad = bgm(total + 1)
        master[:len(pad)] += pad[:len(master)]
    fade = int(1.5 * SR)
    master[int(total * SR) - fade:int(total * SR)] *= np.linspace(1, 0, fade)
    master[int(total * SR):] = 0
    master = np.clip(master, -0.98, 0.98)
    awav = os.path.join(assets, "reel_audio.wav")
    with wave.open(awav, "wb") as wv:
        wv.setnchannels(1); wv.setsampwidth(2); wv.setframerate(SR)
        wv.writeframes((master * 32767).astype(np.int16).tobytes())

    BG, chrome, draw = renderer(spec)
    starts = [sum(durs[:i]) for i in range(len(durs))]
    segs = [render_scene(spec, BG, chrome, draw, i, sc, dur, st, total)
            for i, (sc, dur, st) in enumerate(zip(spec["scenes"], durs, starts))]
    concat = os.path.join(assets, "concat.txt")
    with open(concat, "w") as fh:
        for s in segs:
            fh.write(f"file '{os.path.abspath(s)}'\n")
    silent = os.path.join(assets, "silent.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", concat, "-c", "copy", silent], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", awav,
                    "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.0", "-ar", "48000",
                    "-c:a", "aac", "-profile:a", "aac_low", "-ac", "2", "-b:a", "192k",
                    "-movflags", "+faststart", "-shortest", spec["output"]], check=True)
    print("WROTE", spec["output"])

if __name__ == "__main__":
    main()
