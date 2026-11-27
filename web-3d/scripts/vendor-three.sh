#!/bin/sh
# Bundle three.js and its addons into one minified ES module the site serves itself, so the page loads nothing from the
# network (no CDN, no import map pointing elsewhere). The MIT licence is copied beside it.
#   vendor-three.sh OUT.js [VERSION] [ENTRY.js]
# VERSION defaults to 0.187.0; ENTRY defaults to three-entry.js beside this script. The package is fetched with npm pack
# into a temporary directory and unpacked by tar, so none of its install scripts run.
set -eu
OUT=${1:?usage: vendor-three.sh OUT.js [VERSION] [ENTRY.js]}; V=${2:-0.187.0}
HERE=$(cd "$(dirname "$0")" && pwd); ENTRY=${3:-$HERE/three-entry.js}
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
( cd "$T" && npm pack "three@$V" --silent >/dev/null && mkdir -p node_modules/three && tar -xzf "three-$V.tgz" -C node_modules/three --strip-components=1 )
cp "$ENTRY" "$T/entry.js"
( cd "$T" && npx -y esbuild@0.25 entry.js --bundle --format=esm --minify --legal-comments=eof --outfile=bundle.js --log-level=warning )
mkdir -p "$(dirname "$OUT")"; cp "$T/bundle.js" "$OUT"; cp "$T/node_modules/three/LICENSE" "$(dirname "$OUT")/LICENSE.three"
echo "three $V -> $OUT ($(wc -c < "$OUT") bytes, $(gzip -c "$OUT" | wc -c) gzipped); licence at $(dirname "$OUT")/LICENSE.three"
