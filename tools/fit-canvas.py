#!/usr/bin/env python3
"""
Re-fit the XTherion editing canvas to the drawing in a .th2 file.

    python3 tools/fit-canvas.py survey/C10.plan.th2 [...]
    python3 tools/fit-canvas.py --check survey/*.th2

Why this exists
---------------
The first line of a .th2 file looks like

    ##XTHERION## xth_me_area_adjust <left> <top> <right> <bottom>

and defines the bounds of the editing canvas in XTherion / Therion
Studio. It is a working-area setting, not part of the survey -- Therion
itself ignores it when building maps.

If the drawing grows beyond those bounds, the part outside simply is not
reachable in the editor: it renders off-screen and no amount of
scrolling or zooming will bring it back, because there is no canvas
there to scroll to. That is what "I can't recentre the drawing" looks
like.

XTherion rewrites this line when it saves, so it drifts as you work.
Re-run this whenever the editor starts feeling cramped.
"""

import re
import sys

MARGIN_FRACTION = 0.08   # of the drawing's span
MARGIN_MIN = 100.0       # drawing units

AREA_RE = re.compile(r"^(##XTHERION##\s+xth_me_area_adjust\s+)(.*)$")


def extent(lines):
    """Bounding box of every coordinate pair in the file."""
    xs, ys = [], []
    for ln in lines:
        if ln.startswith("##XTHERION##"):
            continue
        m = re.match(r"\s*point\s+(-?[\d.]+)\s+(-?[\d.]+)", ln)
        if m:
            xs.append(float(m.group(1)))
            ys.append(float(m.group(2)))
            continue
        # Skip option continuation lines such as
        #     -author 2026.09.06 "Lizzie Waterworth" \
        # which otherwise parse as the coordinate (2026.09, 06). A "-"
        # followed by a letter is an option; followed by a digit it is a
        # negative coordinate, which we do want.
        if re.match(r"\s*-[A-Za-z]", ln):
            continue
        # Line data: "x y" for a straight point, or a six-number bezier
        # sextet whose last pair is the node.
        if not ln.strip() or ln.lstrip().startswith(("scrap", "endscrap",
                                                     "line", "endline",
                                                     "area", "endarea",
                                                     "encoding", "#")):
            continue
        nums = re.findall(r"-?\d+\.?\d*", ln)
        if len(nums) in (2, 6):
            xs.append(float(nums[-2]))
            ys.append(float(nums[-1]))
    return (min(xs), max(xs), min(ys), max(ys)) if xs else None


def fit(path, check_only=False):
    lines = open(path, errors="replace").read().splitlines(keepends=True)
    box = extent(lines)
    if box is None:
        print(f"{path}: no coordinates, skipped")
        return True
    x0, x1, y0, y1 = box

    idx = next((i for i, l in enumerate(lines) if AREA_RE.match(l)), None)
    if idx is None:
        print(f"{path}: no xth_me_area_adjust line, skipped")
        return True

    cur = [float(v) for v in re.findall(r"-?\d+\.?\d*", AREA_RE.match(lines[idx]).group(2))]
    fits = (len(cur) == 4 and cur[0] <= x0 and x1 <= cur[2]
            and cur[3] <= y0 and y1 <= cur[1])

    mx = max(MARGIN_MIN, (x1 - x0) * MARGIN_FRACTION)
    my = max(MARGIN_MIN, (y1 - y0) * MARGIN_FRACTION)
    new = (round(x0 - mx, 2), round(y1 + my, 2),
           round(x1 + mx, 2), round(y0 - my, 2))

    if check_only:
        status = "ok" if fits else "DRAWING OUTSIDE CANVAS"
        print(f"{path}: {status}")
        print(f"    canvas  x {cur[0]:9.1f} .. {cur[2]:9.1f}   "
              f"y {cur[3]:10.1f} .. {cur[1]:9.1f}")
        print(f"    drawing x {x0:9.1f} .. {x1:9.1f}   "
              f"y {y0:10.1f} .. {y1:9.1f}")
        if not fits:
            print(f"    suggest x {new[0]:9.1f} .. {new[2]:9.1f}   "
                  f"y {new[3]:10.1f} .. {new[1]:9.1f}")
        return fits

    if fits:
        print(f"{path}: already fits, unchanged")
        return True

    lines[idx] = (AREA_RE.match(lines[idx]).group(1)
                  + " ".join(f"{v:.2f}" for v in new) + "\n")
    open(path, "w").write("".join(lines))
    print(f"{path}: canvas refitted to "
          f"x {new[0]:.0f}..{new[2]:.0f}  y {new[3]:.0f}..{new[1]:.0f}")
    return True


if __name__ == "__main__":
    args = sys.argv[1:]
    check = "--check" in args
    files = [a for a in args if not a.startswith("-")]
    if not files:
        sys.exit(__doc__.strip())
    ok = all(fit(f, check) for f in files)
    sys.exit(0 if ok or not check else 1)
