#!/usr/bin/env python3
"""Gera assets/img_1mb.jpg (~1MB), assets/img_300kb.jpg (~300KB) e assets/text_400kb.html (~400KB).
Requer: pip install pillow"""
import io, os, random
from PIL import Image

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
os.makedirs(OUT, exist_ok=True)

def noise_jpeg(target):
    lo, hi, best = 50, 2400, None
    while lo <= hi:
        mid = (lo + hi) // 2
        img = Image.frombytes("RGB", (mid, mid), os.urandom(mid * mid * 3))
        buf = io.BytesIO(); img.save(buf, "JPEG", quality=85)
        data = buf.getvalue()
        if best is None or abs(len(data) - target) < best[0]:
            best = (abs(len(data) - target), data)
        if len(data) < target: lo = mid + 1
        else: hi = mid - 1
    return best[1]

for name, size in (("img_1mb.jpg", 1_000_000), ("img_300kb.jpg", 300_000)):
    data = noise_jpeg(size)
    open(os.path.join(OUT, name), "wb").write(data)
    print(f"{name}: {len(data)/1024:.0f} KB")

words = "sistemas distribuidos carga desempenho escalabilidade wordpress locust docker container instancia requisicao servidor balanceamento latencia vazao usuario cliente rede tempo resposta teste cenario".split()
random.seed(42)
parts, size = [], 0
while size < 400 * 1024:
    p = "<p>" + " ".join(random.choice(words) for _ in range(80)) + ".</p>\n"
    parts.append(p); size += len(p.encode())
open(os.path.join(OUT, "text_400kb.html"), "w").write("".join(parts))
print(f"text_400kb.html: {size/1024:.0f} KB")
