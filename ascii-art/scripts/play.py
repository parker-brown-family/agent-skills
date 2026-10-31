#!/usr/bin/env python3
"""Play the dot-lattice films as terminal Braille; TD supplies the glass effects."""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path.home() / "Work/reports/ascii-glass"
BITS = ((0, 0, 1), (0, 1, 2), (0, 2, 4), (1, 0, 8),
        (1, 1, 16), (1, 2, 32), (0, 3, 64), (1, 3, 128))
COLORS = {
    1: "\033[38;2;145;148;143m",
    2: "\033[38;2;242;242;235m",
    3: "\033[38;2;231;182;100m",
    4: "\033[38;2;220;40;62m",
}

def frame(data, width, height):
    lines = []
    for y in range(0, height, 4):
        row, last = [], None
        for x in range(0, width, 2):
            bits, peak, color = 0, 0, 1
            for dx, dy, bit in BITS:
                i = ((y + dy) * width + x + dx) * 3
                r, g, b = data[i:i+3]
                value = max(r, g, b)
                if value > 38:
                    bits |= bit
                    if value > peak:
                        peak = value
                        color = 4 if r > g * 1.55 and r > 65 else (
                            3 if r > b * 1.22 else (2 if value > 95 else 1))
            if bits:
                if color != last:
                    row.append(COLORS[color])
                    last = color
                row.append(chr(0x2800 + bits))
            else:
                row.append(" ")
        lines.append("".join(row) + "\033[0m\033[K")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("piece", nargs="?", default="lamp", help="lamp, watchman, or an MP4 path")
    parser.add_argument("--snapshot", action="store_true", help="Print one frame without cursor control")
    parser.add_argument("--size", help="Character columns x rows; default fits the terminal")
    args = parser.parse_args()
    if not shutil.which("ffmpeg"):
        parser.error("ffmpeg is required")
    source = ROOT / (args.piece + ".mp4") if args.piece in {"lamp", "watchman"} else Path(args.piece).expanduser().resolve()
    if not source.is_file():
        parser.error(f"Film is missing: {source}")
    if args.size:
        try:
            cols, rows = map(int, args.size.lower().split("x"))
        except ValueError:
            parser.error("--size must be columns x rows, for example 160x50")
    else:
        size = shutil.get_terminal_size((120, 44))
        cols, rows = size.columns, size.lines - 2
    if cols < 20 or rows < 10:
        parser.error("Terminal must be at least 20 columns and 12 lines")
    # Braille has 2 x 4 square subpixels per character at a 1:2 font ratio.
    width = min(cols * 2, int(rows * 4 * 1.6))
    width -= width % 2
    height = min(rows * 4, int(width / 1.6))
    height -= height % 4
    loops = [] if args.snapshot else ["-stream_loop", "-1", "-re"]
    command = ["ffmpeg", "-v", "error", "-nostdin", *loops, "-i", str(source),
               "-vf", f"fps=15,dilation,dilation,scale={width}:{height}:flags=area",
               "-threads", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    chunk_size = width * height * 3
    try:
        if not args.snapshot:
            sys.stdout.write("\033[?1049h\033[?25l\033[2J")
        while True:
            # A pipe read can return fewer bytes than one frame.
            data = bytearray()
            while len(data) < chunk_size:
                part = proc.stdout.read(chunk_size - len(data))
                if not part:
                    break
                data.extend(part)
            if len(data) != chunk_size:
                if proc.poll() not in (None, 0):
                    raise RuntimeError(proc.stderr.read().decode(errors="replace"))
                break
            art = frame(data, width, height)
            if args.snapshot:
                print(art)
                break
            sys.stdout.write("\033[H" + art + "\033[0m\033[K\n"
                             + source.stem.upper() + "  ·  0xSero / ASCII ART  ·  Ctrl+C closes")
            sys.stdout.flush()
    except (KeyboardInterrupt, BrokenPipeError):
        pass
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        proc.stdout.close()
        proc.stderr.close()
        if not args.snapshot:
            sys.stdout.write("\033[0m\033[?25h\033[?1049l")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
