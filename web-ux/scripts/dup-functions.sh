#!/bin/sh
# Names any function declared more than once in each file given (rule H3): in one shared scope the later declaration
# silently replaces the earlier. Exit 1 if any, 0 if none, 2 on usage.
[ $# -gt 0 ] || { echo "usage: dup-functions.sh FILE.js..." >&2; exit 2; }
bad=0
for f in "$@"; do
  d=$(grep -oE '\bfunction[[:space:]]+[A-Za-z_$][A-Za-z0-9_$]*[[:space:]]*\(' "$f" | sed -E 's/function[[:space:]]+//; s/[[:space:]]*\($//' | sort | uniq -d)
  [ -n "$d" ] && { echo "$f: declared twice: $(echo $d)"; bad=1; }
done
exit $bad
