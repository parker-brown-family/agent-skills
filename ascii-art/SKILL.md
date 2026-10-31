---
name: ascii-art
description: Turn photographs or drawings into dot-lattice art and animated loops using 0xSero's ascii-art craft and engine. Use for ASCII art, dot art, dot portraits, pixel art, disintegration, smoking lamps or censers, and dot animations for Terminal Delight's curved glass. Supports HTML, MP4, and live terminal playback.
---

# ASCII Art

Read the upstream craft before creating a piece:

`/home/parker/Work/ascii-art/SKILL.md`

That checkout contains the original skill, engine, references and MIT licence. Keep it updateable; do not copy its instructions or engine into host discovery directories. This local adapter supplies the machine's runtime and Terminal Delight delivery.

## Runtime

The upstream Python dependencies and Playwright Chromium are installed in:

`/home/parker/Work/ascii-art/.venv/bin/python`

Use that interpreter with the upstream scripts. For example:

```bash
/home/parker/Work/ascii-art/.venv/bin/python /home/parker/Work/ascii-art/scripts/photo_dots.py source.png map.txt 80 58 86
/home/parker/Work/ascii-art/.venv/bin/python /home/parker/Work/ascii-art/scripts/render_map.py map.txt still 0.6
```

Use `references/engine.md` and `references/case-study.md` inside the upstream checkout for scene construction. Convert locally; this workflow needs no image upload or AI call.

For a new install, use an isolated venv with numpy, scipy, pillow, scikit-image and playwright, then install Playwright Chromium. Never install dependencies into the system Python.

## Terminal Delight

Render and inspect the film first. The local terminal player turns an MP4 into two-tone Unicode Braille at 15 fps, with muted gold and rare red retained. It adapts to the terminal's size on launch. TD supplies its existing curvature and phosphor effects.

```bash
python3 /home/parker/BROWN-FAMILY-SPORTS/Software/agent-skills/ascii-art/scripts/play.py /absolute/path/to/film.mp4
```

The installed demo launcher accepts `lamp` or `watchman`:

```bash
ascii-glass lamp
ascii-glass watchman
```

Ctrl+C restores the cursor and the original terminal screen. The player requires ffmpeg and Python's standard library. Restart it after resizing.

For smoke, keep the vessel and chains intact. Emit particles from the vent, give every particle an integer number of cycles per loop, and fade it before its phase wraps. Inspect the plume and the metal separately. The worked extension and original photo masks live at:

`/home/parker/Work/reports/ascii-glass/build.py`

Deliver the review page using fancy-pants-brief. Frame-source HTML follows the artwork's palette; the reading page follows the house glass look. Include playable films, terminal launch commands, and links to the source and validation. Declare and open the reading page in your own pane.

## Installation

The Codex and Claude discovery paths are symlinks to this directory through `agent-parity --sync-skills`. Update the craft with `git -C /home/parker/Work/ascii-art pull --ff-only`; inspect the diff before running changed code.

Upstream: https://github.com/0xSero/ascii-art

Installed revision: `0968699a97e1807b54e7b7db2603c351490adaed`

Licence: MIT, copyright 2026 Sherif (0xSero); see the upstream `LICENSE`.
