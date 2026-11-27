#!/usr/bin/env bash
# Proves loop-render.mjs on a page with no network and no WebGL: a closed loop passes, and each of the two classic
# seam bugs is caught (a repeated first frame, a loop that does not close), and ambient motion on the virtual clock
# closes with its seam crossfaded. Headless; nothing opens on the desktop.
set -u
here=$(cd "$(dirname "$0")" && pwd); r="$here/../scripts/loop-render.mjs"; out=$(mktemp -d)
: "${PLAYWRIGHT:=$HOME/.local/share/mise/installs/playwright/latest/node_modules/playwright/index.mjs}"; export PLAYWRIGHT
fail=0; export FRAMES=24
run() { node "$r" "$here/$1" --out "$out/$1" --frames $FRAMES --width 320 --scale 1 --allow-software >"$out/$1.log" 2>&1; echo $?; }
check() { local got; got=$(run "$1"); if [ "$got" = "$2" ]; then echo "ok    $1 exits $got ($3)"; else echo "FAIL  $1 exits $got, wanted $2 ($3)"; sed 's/^/      /' "$out/$1.log"; fail=1; fi; }
check scene-good.mjs   0 "the loop closes"
check scene-repeat.mjs 1 "first frame shown twice"
check scene-jump.mjs   1 "the loop does not close"
check scene-ambient.mjs 0 "ambient motion on the virtual clock, seam crossfaded"
grep -q '"verdict": "ok"' "$out/scene-good.mjs/loop.json" && [ -s "$out/scene-good.mjs/loop.mp4" ] && [ -s "$out/scene-good.mjs/loop.webm" ] && [ -s "$out/scene-good.mjs/loop.webp" ] \
  && echo "ok    the good scene wrote mp4, webm, poster and manifest" || { echo "FAIL  outputs missing"; fail=1; }
rm -rf "$out"; exit $fail
