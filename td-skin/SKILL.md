---
name: td-skin
description: Create or revise a personal Terminal Delight skin from a reference, validate its TOML, preview real native surfaces, and apply the selected local file. Use for TD chrome and material customization; TDSP workbench content and authored documents retain their own content.
metadata:
  status: approved
  source: terminal-delight surface-authoring
---

# A personal Terminal Delight skin

Make one skin file, show it on TD's real controls, and retain a way back to the previous look. The reference may be an image, an existing skin, or a description. Keep the user's requested scope: a preview does not authorize changing another window or desktop configuration.

## Read the running version's contract

Find the TD binary and resolve the target window, if the user asked to apply the look. Several TD windows may run at once. MCP can identify panes and the answering instance; the control CLI accepts an explicit window pid. Prefer that identity over a guessed process name.

Export the contract from the binary you will preview:

```sh
terminal-delight skin --catalogue > skin-surfaces.json
terminal-delight skin --catalogue-md > skin-surfaces.md
terminal-delight skin --template chalk > personal-skin.toml
terminal-delight skin --atlas-script > skin-atlas.py
```

Read the catalogue's policies and the template. The JSON is the inventory; do not maintain a copied list in this skill. Its facets describe source routing. A missing fixture or capture is unverified, and a stale receipt does not certify the current file. If these options are unavailable, use a compatible TD build before promising this workflow.

The four inputs are separate:

- **Palette:** colour roles and semantic state colours.
- **Design:** terminal font and CRT effects.
- **Skin:** native furniture, material, UI type and note policy.
- **Grade:** the window or pane's current warp, brightness and size settings.

Let the substrate follow the selected palette. Do not manufacture light and dark skin variants unless the user requests distinct designs. Preserve terminal cells, authored HTML/Markdown/PDF typography, media pixels, and the meaning of status colours. Their native surrounding controls still belong to the skin.

## Author within the vocabulary

Choose the nearest bundled template using `skin --list` and `--template`. Write one TOML file. Supported strategies compose without rebuilding TD. A new rendering effect needs a shared engine extension; it cannot be smuggled into an unknown TOML field.

Use role recipes for colours that should follow the palette. A pinned hex value is appropriate when the reference or user actually requires a fixed colour. Keep selected, hover, warning, failure and success distinguishable.

The templates and resolver expose current keys. Useful settings include:

- `[font] family`, `heading`, `data`, `scale`, `min_px`, `line_height`: UI families and optical fitting. Material does not choose these. Confirm the requested font is available or bundled; a fallback is not proof that it rendered.
- `[shape] material`, `corner`, `boundary`, `emphasis`, `divider`, `caps`, `shine`, `gauge`, `title`, `focus`, `tube`: the existing finite strategies. `tube = "stock"` and `"glass"` control terminal furniture independently of chrome material.
- `[metric] grain`, `roughness`, `lift`, `marker_alpha`: existing stock rendering controls. Grain, roughness and marker opacity use 0–1; lift uses 0–2. The template documents the remaining metrics.
- `[note] decoration = "plain" | "flower"`, `stock = true | false`: note decoration and whether Contrast paper derives from the skin. Sticky text retains its own handwriting.

Distinguish a choice from an action. A selected choice needs one clear mark through its label; a raised action can carry a backing and depth. Judge type centring and label fit with the actual font, including a long label. Avoid fixing a material defect by flattening the user's CRT or changing terminal cell geometry.

Validate and read back the result:

```sh
terminal-delight skin --check --skin personal-skin.toml --theme hacker > resolved-skin.json
```

Use the relevant design or palette file for other pairings. `--check` refuses unknown tokens and invalid numeric settings. Read the resolved fonts, optical settings, shape, ink and material values. An absent override means inheritance; an explicit zero remains zero. Resolution proves the file, not its native appearance.

## Preview native controls

Use the exported runner with the same binary. It creates a new session with private config, cache and state, fictional data, and no credentials. Give each capture a new directory:

```sh
python3 skin-atlas.py --binary /path/to/terminal-delight --skin personal-skin.toml --out review/usage --scene usage
```

Read `--help` for scenes, geometry, language, grade and palette options. The default hidden capture backend uses Hyprland 0.56. On another desktop, `--visible --hold` opens only the private preview window. `--capture` accepts a JSON argv array for a native screenshot utility; it does not evaluate shell text. If no capture backend is available, retain that fact and have the user inspect the preview rather than inventing proof.

Preview the catalogue families affected by the request. For a new overall look, include workspace/frame/rails, palette choices, Subscriptions, gauges, workbench, document controls and sticky notes. Compare a pale and dark palette, a narrow window, the intended UI/text scale, the user's actual grade, and at least one warped scene. Exercise selected, inactive, hover and disabled controls where relevant. Include measured-zero and unavailable readings; they must remain distinguishable. A screenshot of one family does not certify another.

The receipt records build and skin hashes, palette request, geometry, grade and capture. Its visual verdict starts absent. Inspect the pictures, record what was actually judged, and keep missing cases explicit. Present the native pictures with the file and a short explanation of what changed. For iterative feedback, make a local commentable HTML review whose anchors correspond to the catalogue entries; use an available report skill or a self-contained page, with no external dependencies.

## Apply and restore

Apply only to the requested local target. Inspect `ctl skin status`, the active custom-file path, and the previous explicit/theme-following selection. `TD_SKIN` overrides the standard path and wins over a saved selection on startup; record it if present. Save the selection and back up an existing custom file before replacing it. Use the validated TOML, then select `custom` on that window through MCP or the explicit-pid control CLI. Do not restart normal sessions to change a skin.

Verify the active skin with `ctl skin snapshot` and a visible change. The snapshot reads the live registry. The runner's `--verify-reload` exercises a valid edit, invalid edit, exact file/selection restoration and a restart of only its private preview to check persistence. Explain the exact restore action for the user's recorded file and selection. If the custom file did not exist before, restoration includes removing it as well as restoring the selection.

Deliver the skin file, native review and scoped proof receipts. Report any remaining mixed or unverified catalogue facets plainly. Keep a new renderer contribution separate from the claim that this look was authored through a file.
