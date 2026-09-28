"""Render original profile line art. Run with Python 3 and Pillow."""
import math
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
S = 2
BG, PANEL, BORDER = "#0d1421", "#111b2b", "#253248"
WHITE, MUTED, LAVENDER, MINT, DIM = "#edf0f7", "#9caabe", "#b5a8df", "#9bcaba", "#34455d"


def font(size, bold=False, mono=False):
    windows = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
    choices = [windows / "CascadiaMono.ttf", Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")] if mono else [windows / ("segoeuib.ttf" if bold else "segoeui.ttf"), Path("/usr/share/fonts/truetype/dejavu") / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")]
    for choice in choices:
        if choice.exists():
            return ImageFont.truetype(str(choice), size * S)
    raise RuntimeError("Install Segoe UI or DejaVu Sans to reproduce the artwork.")


def canvas(w, h):
    image = Image.new("RGB", (w * S, h * S), BG)
    return image, ImageDraw.Draw(image)


def box(d, xy, fill, outline, radius):
    d.rounded_rectangle(tuple(round(v * S) for v in xy), radius=radius * S, fill=fill, outline=outline, width=S)


def line(d, xy, fill, width=1):
    d.line(tuple(round(v * S) for v in xy), fill=fill, width=width * S)


def text(d, x, y, value, size, fill=WHITE, bold=False, mono=False):
    d.text((x * S, y * S), value, font=font(size, bold, mono), fill=fill, anchor="lt")


def circle(d, x, y, r, fill=None, outline=None):
    d.ellipse(((x-r)*S, (y-r)*S, (x+r)*S, (y+r)*S), fill=fill, outline=outline, width=S)


def reduce(image):
    return image.resize((image.width // S, image.height // S), Image.Resampling.LANCZOS)


def header():
    image, d = canvas(1280, 360)
    box(d, (1, 1, 1278, 358), PANEL, BORDER, 22)
    line(d, (54, 54, 80, 54), MINT, 2)
    text(d, 94, 45, "SOFTWARE DEVELOPER", 17, MINT, mono=True)
    text(d, 54, 96, "Atakan MERGEN", 70, bold=True)
    text(d, 58, 193, "Thoughtful interfaces. Reliable systems.", 25, MUTED)
    text(d, 58, 236, "DESKTOP  /  BACKEND  /  AUTOMATION", 17, LAVENDER, mono=True)
    text(d, 58, 308, "hzflora", 17, MUTED, mono=True)
    text(d, 702, 308, "TÜRKIYE", 14, MUTED, mono=True)
    cx, cy = 1035, 177
    for radius in (62, 97, 132):
        circle(d, cx, cy, radius, outline=BORDER)
    line(d, (cx-150, cy, cx+150, cy), BORDER)
    line(d, (cx, cy-149, cx, cy+149), BORDER)
    circle(d, cx, cy, 53, fill=BG, outline=DIM)
    text(d, cx-42, cy-23, "</>", 45, LAVENDER, mono=True)
    for x, y in ((cx, cy-132), (cx+132, cy), (cx, cy+132), (cx-132, cy)):
        circle(d, x, y, 3, fill=DIM)
    frames = []
    for index in range(80):
        frame = image.copy()
        ink = ImageDraw.Draw(frame)
        phase = 2 * math.pi * index / 80
        for radius, angle, color, r in ((97, phase-math.pi/2, MINT, 5), (132, -phase+math.pi/6, LAVENDER, 4)):
            x, y = cx+radius*math.cos(angle), cy+radius*math.sin(angle)
            circle(ink, x, y, r+5, fill=PANEL)
            circle(ink, x, y, r, fill=color)
        frames.append(reduce(frame))
    return frames, 250


def workflow():
    image, d = canvas(1280, 136)
    box(d, (1, 1, 1278, 134), PANEL, BORDER, 18)
    text(d, 48, 32, "A CONTINUOUS PRACTICE", 13, MUTED, mono=True)
    text(d, 48, 67, "Make it work. Make it clear. Make it better.", 20)
    centers = (690, 910, 1130)
    for start, end in zip(centers, centers[1:]):
        line(d, (start+12, 47, end-12, 47), BORDER, 2)
    for x, label in zip(centers, ("BUILD", "TEST", "REFINE")):
        circle(d, x, 47, 5, fill=LAVENDER)
        text(d, x-(len(label)*10)/2, 78, label, 17, MUTED, mono=True)
    frames = []
    for index in range(60):
        frame = image.copy()
        ink = ImageDraw.Draw(frame)
        phase = index / 60
        if phase < 0.8:
            progress = phase / 0.8
            eased = progress * progress * (3-2*progress)
            circle(ink, centers[0]+(centers[-1]-centers[0])*eased, 47, 3, fill=MINT)
        frames.append(reduce(frame))
    return frames, 200


def save(name, frames, duration):
    # One palette keeps all stationary text and edges stable between frames.
    palette = frames[0].quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    indexed = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
    path = ASSETS / f"{name}.gif"
    indexed[0].save(path, save_all=True, append_images=indexed[1:], duration=duration, loop=0, optimize=True, disposal=1)
    print(f"{path.name}: {path.stat().st_size:,} bytes; {len(frames)*duration/1000:.1f}s loop")


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    for name, generator in (("profile-header", header), ("workflow", workflow)):
        frames, duration = generator()
        save(name, frames, duration)
