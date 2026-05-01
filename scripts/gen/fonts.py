"""Download Google Fonts woff2 (latin) for focal + hal placeholders."""
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TMP = ROOT / ".tmp"
OUT = ROOT / "assets" / "fonts"
OUT.mkdir(parents=True, exist_ok=True)


def latin_urls(css_path):
    css = css_path.read_text()
    blocks = re.split(r"/\*\s*([a-z\-]+)\s*\*/", css)
    out = {}
    for i in range(1, len(blocks), 2):
        label = blocks[i].strip()
        content = blocks[i + 1]
        m_w = re.search(r"font-weight:\s*(\d+)", content)
        m_u = re.search(r"url\((https://[^)]+\.woff2)\)", content)
        if not (m_w and m_u) or label != "latin":
            continue
        out[int(m_w.group(1))] = m_u.group(1)
    return out


def fetch(url, dst):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        dst.write_bytes(r.read())


def main():
    inter = latin_urls(TMP / "inter.css")
    jbm = latin_urls(TMP / "jbm.css")
    if not inter or not jbm:
        sys.exit("missing CSS — re-fetch with curl")

    name_map = {
        "focal-300.woff2": inter[300],
        "focal-400.woff2": inter[400],
        "focal-500.woff2": inter[500],
        "focal-600.woff2": inter[600],
        "hal-400.woff2": jbm[400],
    }
    for name, url in name_map.items():
        dst = OUT / name
        fetch(url, dst)
        print(f"{name}: {dst.stat().st_size} bytes")


if __name__ == "__main__":
    main()
