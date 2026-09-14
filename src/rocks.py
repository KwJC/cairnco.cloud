"""Regenerate the cairn rock silhouettes for The Issue section.

Rocks are generated, not drawn: a polar radius with four high-frequency
harmonics gives faceted irregularity, then a Catmull-Rom pass smooths it into
cubic beziers. Base and top are flattened so the stones read as resting and
load-bearing. One cairn, eight rocks, one per problem card.

Writes rocks-markup.html; paste it inside the .fall__in div in the template.
Requires numpy.
"""
import numpy as np, json, math

def cr_bezier(pts):
    n = len(pts)
    d = [f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"]
    for i in range(n):
        p0, p1, p2, p3 = pts[(i-1) % n], pts[i], pts[(i+1) % n], pts[(i+2) % n]
        c1 = (p1[0] + (p2[0]-p0[0])/7.5, p1[1] + (p2[1]-p0[1])/7.5)
        c2 = (p2[0] - (p3[0]-p1[0])/7.5, p2[1] - (p3[1]-p1[1])/7.5)
        d.append(f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}")
    d.append("Z")
    return "".join(d)

def rock(seed, w, h, N=34):
    r = np.random.default_rng(seed)
    harm = [(r.uniform(.020, .050), int(r.integers(3, 9)), r.uniform(0, 2*math.pi))
            for _ in range(4)]
    pts = []
    for i in range(N):
        th = 2*math.pi*i/N
        rad = 1.0
        for a, k, ph in harm:
            rad += a*math.sin(k*th + ph)
        x, y = math.cos(th)*rad, math.sin(th)*rad
        if y > 0.62:   y = 0.62 + (y-0.62)*0.34     # flat base, it rests
        if y < -0.74:  y = -0.74 + (y+0.74)*0.55    # flat top, it carries the next
        pts.append((w/2 + x*w/2*0.95, h/2 + y*h/2*0.95))
    return cr_bezier(pts)

# width, height, tilt. Widest at the base. Eight rocks, one per problem card.
SPEC = [(460,184,-4), (400,160,7), (350,140,-9), (300,120,5),
        (252,101,-6), (206,82,9), (160,64,-5), (116,46,8)]
OVERLAP = 0.70   # lower = stones sit deeper into each other

if __name__ == "__main__":
    rocks, y, seed = [], 820, 900
    for (w, h, rot) in SPEC:
        seed += 1
        rocks.append({"w": w, "h": h, "rot": rot, "top": round(y-h),
                      "d": rock(seed, w, h)})
        y -= h*OVERLAP
    rocks.sort(key=lambda o: o["top"])     # topmost first: it crumbles from the top

    json.dump(rocks, open("rocks.json", "w"))
    out = []
    for i, o in enumerate(rocks):
        out.append(
            f'    <svg class="rock" viewBox="0 0 {o["w"]} {o["h"]}" '
            f'style="--x:70%;--y:{o["top"]}px;--w:{o["w"]}px;--h:{o["h"]}px;--r:{o["rot"]}deg">'
            f'<path d="{o["d"]}" fill="url(#stone{i%4})" stroke="#6E7A6E" '
            f'stroke-opacity=".5" stroke-width="1.6"/></svg>')
    open("rocks-markup.html", "w").write("\n".join(out))
    print(f"wrote {len(rocks)} rocks. Paste rocks-markup.html inside .fall__in")
