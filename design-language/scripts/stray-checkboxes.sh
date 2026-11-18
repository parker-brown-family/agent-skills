#!/usr/bin/env bash
# Toggles, never checkboxes: finds checkboxes in source before they render. Part of the design-language skill (MIT).
#   scripts/stray-checkboxes.sh [DIR ...]      exit 1 if any are found, 0 if none
# Matches HTML and JSX checkbox inputs, role="checkbox", and the checkbox components of the common
# libraries (Radix, shadcn, MUI, Headless UI, expo-checkbox, React Native's old CheckBox).
set -u
dirs=("${@:-.}")
pattern='type=["{'"'"' ]*["'"'"']?checkbox|role=["'"'"']checkbox|menuitemcheckbox|<Checkbox[ />]|<CheckBox[ />]|@radix-ui/react-checkbox|components/ui/checkbox|@mui/material/Checkbox|expo-checkbox|@react-native-community/checkbox'
if command -v rg >/dev/null 2>&1; then
  rg -n --no-heading -e "$pattern" -g '!**/node_modules/**' -g '!**/.next/**' -g '!**/dist/**' -g '!**/build/**' \
     -g '*.{tsx,jsx,ts,js,html,vue,svelte}' "${dirs[@]}"
else
  grep -rnE --include='*.tsx' --include='*.jsx' --include='*.ts' --include='*.js' --include='*.html' \
     --exclude-dir=node_modules --exclude-dir=.next --exclude-dir=dist --exclude-dir=build "$pattern" "${dirs[@]}"
fi
found=$?
if [ "$found" -eq 0 ]; then echo "stray checkboxes above: draw each as a toggle (.hw-toggle, role=switch) or a selectable row" >&2; exit 1; fi
echo "no checkboxes"; exit 0
