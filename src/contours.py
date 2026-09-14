"""Regenerate the section background contours (not the hero: that is live canvas).

Contours come from a sum of gaussians run through matplotlib.contour, generated
at the section's aspect ratio so they are never stretched.
Requires numpy and matplotlib.
"""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def make(seed, peaks, levels, fname, W=1440, H=1000, step=3, minlen=14,
         spread=(0.13, 0.40, 0.10, 0.30)):
    gx, gy = np.meshgrid(np.linspace(0, 1.44, 300), np.linspace(0, 1, 210))
    r = np.random.default_rng(seed)
    z = np.zeros_like(gx)
    sxlo, sxhi, sylo, syhi = spread
    for _ in range(peaks):
        cx, cy = r.uniform(-0.15, 1.6), r.uniform(-0.15, 1.15)
        sx, sy = r.uniform(sxlo, sxhi), r.uniform(sylo, syhi)
        z += r.uniform(-1, 1)*np.exp(
            -(((gx-cx)**2)/(2*sx**2) + ((gy-cy)**2)/(2*sy**2)))
    fig, ax = plt.subplots()
    cs = ax.contour(gx, gy, z, levels=levels)
    paths = []
    for segs in cs.allsegs:
        for seg in segs:
            if len(seg) < minlen:
                continue
            s = seg[::step]
            if len(s) < 6:
                continue
            paths.append("M" + " ".join(f"{p[0]/1.44*W:.0f},{p[1]*H:.0f}" for p in s))
    plt.close(fig)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'preserveAspectRatio="none" fill="none">']
    for i, d in enumerate(paths):
        out.append(f'<path d="{d}" stroke="currentColor" '
                   f'stroke-width="{1.7 if i % 5 == 0 else 0.9}"/>')
    out.append("</svg>")
    open(fname, "w", encoding="utf-8").write("".join(out))
    return len(paths)

if __name__ == "__main__":
    print("dense:", make(23, 11, 42, "topo-dense.svg"))
    print("open:",  make(31, 7, 12, "topo-open.svg", step=4, minlen=22,
                         spread=(0.22, 0.55, 0.16, 0.38)))
