"""Generate PBR floor textures (procedural cyberpunk marble).

Produces 1024x1024 tiling textures:
  basecolor.png  - dark marble with cyan veins
  normal.png     - subtle bumpiness from same noise
  roughness.png  - varying gloss
  metalness.png  - mostly non-metal with subtle inclusions
"""
import numpy as np
from PIL import Image
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[2] / "assets"
OUT = ASSETS / "floor"
OUT.mkdir(parents=True, exist_ok=True)
SIZE = 1024


def value_noise(size, scale, seed):
    rng = np.random.default_rng(seed)
    n = max(2, size // scale)
    grid = rng.random((n, n)).astype(np.float32)
    img = Image.fromarray((grid * 255).astype(np.uint8), "L")
    img = img.resize((size, size), Image.BICUBIC)
    return np.asarray(img, dtype=np.float32) / 255.0


def fbm(size, seed=1):
    out = np.zeros((size, size), dtype=np.float32)
    amp = 0.5
    for i, scale in enumerate([8, 16, 32, 64, 128]):
        out += value_noise(size, scale, seed + i) * amp
        amp *= 0.55
    out -= out.min()
    out /= out.max()
    return out


def basecolor(size, seed=42):
    base = fbm(size, seed)
    veins = np.abs(fbm(size, seed + 100) - 0.5) * 2.0
    veins = 1.0 - veins
    veins = np.clip((veins - 0.85) * 7.0, 0, 1)

    r = 0.04 + base * 0.06
    g = 0.05 + base * 0.07
    b = 0.08 + base * 0.10
    r = np.clip(r + veins * 0.05, 0, 1)
    g = np.clip(g + veins * 0.55, 0, 1)
    b = np.clip(b + veins * 0.85, 0, 1)
    rgb = np.stack([r, g, b], axis=-1)
    arr = (rgb * 255).astype(np.uint8)
    Image.fromarray(arr, "RGB").save(OUT / "basecolor.png", optimize=True)
    return base, veins


def normal_map(size, base, veins, strength=2.0):
    height = base * 0.4 + veins * 0.6
    gx = np.zeros_like(height)
    gy = np.zeros_like(height)
    gx[:, 1:-1] = (height[:, 2:] - height[:, :-2]) * strength
    gy[1:-1, :] = (height[2:, :] - height[:-2, :]) * strength
    nz = np.ones_like(height)
    norm = np.sqrt(gx * gx + gy * gy + nz * nz)
    nx = -gx / norm
    ny = -gy / norm
    nz = nz / norm
    rgb = np.stack([(nx + 1) * 0.5, (ny + 1) * 0.5, (nz + 1) * 0.5], axis=-1)
    arr = (rgb * 255).clip(0, 255).astype(np.uint8)
    Image.fromarray(arr, "RGB").save(OUT / "normal.png", optimize=True)


def roughness_map(size, base, veins):
    rough = 0.35 + base * 0.4 + (1.0 - veins) * 0.1
    rough = np.clip(rough, 0.2, 0.95)
    arr = (rough * 255).astype(np.uint8)
    Image.fromarray(arr, "L").save(OUT / "roughness.png", optimize=True)


def metalness_map(size, veins):
    metal = veins * 0.35
    metal = np.clip(metal, 0, 1)
    arr = (metal * 255).astype(np.uint8)
    Image.fromarray(arr, "L").save(OUT / "metalness.png", optimize=True)


def marble_disk(size=1024):
    """CSS-anchor marble used by index.html .floor-anchor::after.
    Square PNG with the marble pattern masked into a soft-edged ellipse."""
    base = fbm(size, seed=11)
    veins = np.abs(fbm(size, seed=23) - 0.5) * 2.0
    veins = np.clip((1.0 - veins - 0.85) * 7.0, 0, 1)
    val = np.clip(base * 0.85 + veins * 0.45, 0, 1)
    rgb = np.stack([val * 235 + 18, val * 232 + 20, val * 230 + 24], axis=-1).clip(0, 255).astype(np.uint8)
    tile = Image.fromarray(rgb, "RGB").convert("RGBA")
    # soft elliptical alpha mask
    yy, xx = np.mgrid[0:size, 0:size]
    cx = cy = (size - 1) / 2
    d = np.sqrt(((xx - cx) / cx) ** 2 + ((yy - cy) / cy) ** 2)
    alpha = np.clip(1.0 - (d - 0.78) / 0.22, 0, 1)
    rgba = np.dstack([np.asarray(tile)[..., :3], (alpha * 255).astype(np.uint8)])
    out = Image.fromarray(rgba, "RGBA")
    out = out.quantize(colors=128, method=Image.Quantize.FASTOCTREE).convert("RGBA")
    out.save(ASSETS / "floor-marble.png", optimize=True)


def main():
    base, veins = basecolor(SIZE)
    normal_map(SIZE, base, veins)
    roughness_map(SIZE, base, veins)
    metalness_map(SIZE, veins)
    marble_disk(1024)
    print(f"Wrote 4 floor textures to {OUT} + floor-marble.png to {ASSETS}")


if __name__ == "__main__":
    main()
