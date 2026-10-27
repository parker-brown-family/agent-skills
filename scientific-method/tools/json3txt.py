#!/usr/bin/env python3
"""YouTube json3 captions -> timestamped transcript, one line per ~30 s, every word once.

Fetch the captions and the metadata without the video:

    yt-dlp --skip-download --write-auto-subs --write-subs --sub-format json3 --sub-langs 'en.*' \
           --write-info-json -o '%(id)s' <url>

Use json3 rather than VTT. YouTube's VTT auto-captions roll: each cue repeats the previous line, and
de-duplicating the rolls drops words. json3 carries every word once, with its own start time, so the
transcript keeps the speaker's exact words and every line keeps a timestamp a reader can jump to.

Usage: json3txt.py <in.json3> <out.txt> [info.json]
"""
import json
import sys

src, out = sys.argv[1], sys.argv[2]
info = sys.argv[3] if len(sys.argv) > 3 else None

d = json.load(open(src, encoding="utf-8"))
words = []  # (ms, text)
for ev in d.get("events", []):
    t0 = ev.get("tStartMs", 0)
    for seg in ev.get("segs") or []:
        txt = seg.get("utf8", "")
        if txt.strip() == "":
            txt = " "
        words.append((t0 + seg.get("tOffsetMs", 0), txt))


def hms(s):
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


blocks, start, buf = [], None, []
for ms, txt in words:
    s = ms // 1000
    if start is None:
        start = s
    buf.append(txt)
    if s - start >= 30 and txt.rstrip().endswith((".", "?", "!")):
        blocks.append((start, "".join(buf).replace("\n", " ")))
        start, buf = None, []
    elif s - start >= 45:
        blocks.append((start, "".join(buf).replace("\n", " ")))
        start, buf = None, []
if buf:
    blocks.append((start, "".join(buf).replace("\n", " ")))

with open(out, "w", encoding="utf-8") as f:
    if info:
        m = json.load(open(info, encoding="utf-8"))
        f.write(f"# {m.get('title')}\nchannel: {m.get('channel')}\nupload_date: {m.get('upload_date')}\n")
        f.write(f"duration: {m.get('duration_string')}\nurl: {m.get('webpage_url')}\nviews: {m.get('view_count')}\n\n")
        f.write(f"## Description\n{m.get('description')}\n\n")
        chs = m.get("chapters") or []
        if chs:
            f.write("## Chapters\n")
            for c in chs:
                f.write(f"{hms(int(c['start_time']))} {c['title']}\n")
            f.write("\n")
        f.write("## Transcript (YouTube auto-captions, json3, speaker labels absent)\n\n")
    for s, text in blocks:
        f.write(f"[{hms(s)}] {' '.join(text.split())}\n")
print(f"{len(blocks)} blocks, {sum(len(b[1].split()) for b in blocks)} words -> {out}")
