# C10

Cave survey data for **C10**, Bric 4 Group. Surveyed with SexyTopo,
drawn and rendered with [Therion](https://therion.speleo.sk/).

**📄 [Latest drawn survey](https://paperclipmonkey.github.io/caves-wye-c10/)** —
rebuilt automatically from this repository on every push to `main`.

---

## Status

The centreline is complete: 20 stations, 56 m of passage, entrance fixed
by GPS. **The passage walls are not drawn yet.** The sheets currently
show the centreline and the survey furniture, and will fill in as the
drawing progresses — nothing else needs changing for that to happen.

Still to do:

- Draw walls into `survey/C10.plan.th2` (plan) and `survey/C10.ee.th2`
  (extended elevation), tracing over the SexyTopo backdrops in `sketch/`.
- Fill in the eight empty cross-section scraps (`C10PX2`, `C10PX3`, …
  `C10PX15`), which are already anchored on the plan by
  `point section -scrap …`.
- Then turn on depth tinting and add the sections sheet — both are
  written out and commented in `thconfig`, ready to uncomment.

## Building it yourself

Everything is driven by one file, `thconfig`. With Therion installed:

```bash
therion
```

Or with no local install, using the same container CI uses:

```bash
docker run --rm -v "$PWD:/project" ghcr.io/paperclipmonkey/therion:6.4.0 thconfig
python3 web/make_index.py
```

Output lands in `output/` (git-ignored). Open `output/index.html`.

## What is where

| Path | What it is |
|---|---|
| `thconfig` | The build: layouts, page composition, and every export. Heavily commented. |
| `therion.ini` | Project-local Therion settings — currently the map fonts. |
| `survey/C10.th` | Survey metadata, centreline data, and the map definitions. |
| `survey/C10.plan.th2` | Plan drawing + the cross-section scraps. |
| `survey/C10.ee.th2` | Extended elevation drawing. |
| `sketch/` | SexyTopo backdrops (`.xvi`) to trace over in XTherion. |
| `fonts/` | DejaVu Sans, used for all map text. |
| `web/make_index.py` | Builds the GitHub Pages landing page from `output/`. |
| `.github/workflows/build.yml` | Build, publish, and PR previews. |

SexyTopo's own filenames are kept so a fresh export from the phone drops
straight in without renaming anything.

## How the automation works

`.github/workflows/build.yml` does the same build in all cases and then
branches on the event:

- **Push to `main`** → build → generate `index.html` → publish to GitHub
  Pages.
- **Pull request** → build → upload `output/` as a downloadable artifact
  and post (or update) a comment on the PR with the survey statistics and
  a link. Nothing is published until it merges.
- **Manual** → `workflow_dispatch`, same as a push.

The build fails if Therion logs an error; warnings are collected into a
collapsed group in the run log rather than failing the build. Each run
also writes a summary — station count, length, vertical range, and the
size of every artefact — to the Actions run page.

### First-time setup

GitHub Pages must be set to **Source: GitHub Actions** in
*Settings → Pages*. Nothing else is needed.

## Notes for whoever edits this next

- **Lines marked `<<< EDIT`** in `survey/C10.th` are placeholders: the
  team names and the dates. The coordinates are real.
- **Declination is pinned to 0** to match the raw SexyTopo export. There
  is a `cs` and `fix` in the file, so *deleting* that line makes Therion
  compute declination from its geomagnetic model and silently rotate the
  whole survey. Change it deliberately.
- **Splay shots cannot be drawn on a Therion map sheet.** They are
  filtered out before reaching any line symbol, and no symbol set draws
  them. Trace them from the `.xvi` backdrop in `sketch/`, or look at
  `output/C10-walls.lox`, which is a 3D model built from the splays.
- **The build is pinned to `ghcr.io/paperclipmonkey/therion:6.4.0`**, not
  `:latest`, so a survey rebuilt in a year renders identically. Bump it
  in `.github/workflows/build.yml` deliberately. That image is multi-arch,
  so it runs natively on Apple Silicon as well as on the CI runners.
  The `code tex-map` block still opens with two `\ifx` shims for helpers
  that only exist in 6.4 (`\setsize`, `\rgbcolor`); they are no-ops on
  6.4 and are kept so the file also builds under an older local Therion.
  If a sheet dies with *Undefined control sequence* and an
  `<inserted text>` naming a macro, add it to that list.
- **`\legendbox` is `\def`, not `\long\def`** — a `\par` token anywhere in
  its argument gives *Paragraph ended before \legendbox was complete* and
  a cascade of *Too many }'s*. Use `\endgraf`, and keep blank lines out of
  those boxes.
- **The output coordinate system is a config-level `cs`**, not a layout
  option. Set inside a layout it is ignored and Therion quietly picks a
  UTM zone from the fix instead — watch for `output coordinate system:` in
  `therion.log`.

A sister project for the C7 survey has the same structure with much
fuller commentary on the Therion features themselves.
