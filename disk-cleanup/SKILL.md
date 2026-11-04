---
name: disk-cleanup
description: Find out where this box's disk went and get it back without losing anything. Use whenever free space is the subject, in whatever words - "cleanup disk space protocol", "clean up behind ourselves", "disk is full", "we're out of space", "where did the space go", "what happened to my disk", "free up some room", "X is done, clean up after it", "how much can we reclaim". Rebuilds the free-space history from agent transcripts, finds what grew, sorts rebuildable from irreplaceable, and deletes only through guards that actually run. Machine facts live in dev-box-survival-kit/docs/disk-on-this-box.md. Not for diagnosing a full /tmp alone: that is RAM, and tmp-reaper's job.
---

# Disk cleanup

Parker, 2026-10-31: *"CLEANUP DISK SPACE PROTOCOL! terminmialist is done the Omarchy Doctrine is done, clean up behind ourselves <3"*. That run took the disk from 84 GB free to 319 GB and every step below comes from it. Facts about this machine (subvolumes, compression, who owns what) are in one place, and this skill does not repeat them:

```
/home/parker/BROWN-FAMILY-SPORTS/Software/dev-box-survival-kit/docs/disk-on-this-box.md
```

## 1. See who is still working

Run `list_panes`, then `pane_events` on the panes that own what you are about to touch. An agent in its tie-off may still be reading its scratch or tidying the same folder. Wait for it with a bounded loop on its transcript's modified time; never delete beside it.

## 2. Measure before believing anyone's number

- `df -h /` now.
- `scripts/free-space-history` rebuilds free space by day from the `df` output in agent transcripts. "We had 290 GB yesterday" turned out to be a peak four days old, and the real story was 50 GB a day. Say what the history shows, kindly.
- Sum **every** file written since the last peak, by folder, not just large files. Build folders and frame dumps are thousands of small files, and a `-size +20M` scan found a sixth of the truth:

```bash
find /home -xdev -type f -newermt '2026-11-01 00:00' -printf '%s\t%p\n' | awk -F'\t' '{n=split($2,a,"/"); k="/"a[2]"/"a[3]"/"a[4]"/"a[5]; s[k]+=$1} END {for (k in s) if (s[k]>2^30) printf "%7.1f GiB  %s\n", s[k]/2^30, k}' | sort -rn | head -20
```

`/home` is its own subvolume, so a `find / -xdev` stops at its edge and misses nearly everything. Scan `/home` and `/var` separately.

## 3. Sort everything into four piles

| Pile | Examples | What happens |
|---|---|---|
| Ours, finished, rebuildable | the named job's render frames and scratch; merged, clean worktrees | Delete after the guards |
| Rebuildable, someone else's | idle Rust `target` folders (find them by `CACHEDIR.TAG`), other films' scratch | List with sizes and dates; clear on Parker's yes, or when he has asked for the space back |
| Owned by a project's cleaner | Cinema Delight frames | Use the cleaner. If it refuses, read why; never `rm` around it |
| Costly or impossible to remake | music stems, Ardour mixes, models, sealed finals, draft movies, anything a page embeds | Stays. Check what pages embed before deleting from an `out/` folder |

Scope is what was asked. Anything bigger you noticed goes in the reply as a measured offer.

## 4. Guards, and each one must really run

Before a delete, all of these, in the same command as the delete:

- **Open files:** `scripts/held-open <path>...`. Never `lsof`: it is not installed here, and `lsof ... 2>/dev/null` prints nothing, which reads as "nothing open". A whole session's guards passed that way.
- **Running builds:** for each `cargo`/`rustc`, read `CARGO_TARGET_DIR` from `/proc/<pid>/environ` and its `cwd/target`, and skip those folders. A build can start between your survey and your delete, so check in the delete command.
- **Anything launched from it:** `readlink /proc/*/exe`, and symlinks in `~/.local/bin` and `~/bin`. `soundcraft`, `effectcraft`, `photocraft` and `cdx` run straight out of their own `target/release/`.
- **The launcher's target:** `readlink -f ~/.local/bin/terminal-delight` can change between turns. Re-read it at delete time, along with every binary a window is running.
- **Sockets:** never delete a folder holding one (`find -type s`).
- **Git:** a worktree goes only if it is clean and level with its upstream, through `git worktree remove`.

A guard whose tool is missing must fail loudly: run `command -v` first, and never silence stderr on the check that protects a delete.

## 5. Delete, then prove it

- Report what `df` says, not what `du` promised. btrfs compression means deletions free less than file sizes suggest, and space shared by reflink or hardlink frees nothing until the last copy goes. `uv cache prune` removed 27.8 GiB of files and freed nothing.
- `/tmp` is RAM. Clearing it frees no disk.
- Verify what must have survived: run `sha256sum -c` on seals you worked near, and confirm embedded media still resolves.
- When a delete is outside a project's cleaner, write a ledger first: what goes, why, whose word, and what stays with its hash.

## 6. Leave the fix, not only the space

Disk refills: 319 GB on 2026-10-31 was 249 GB two days later. For each big pile ask what would have stopped it, and file a falsifiable issue if nothing does. Keep a window on recent work: Parker wants sealed frames kept for a fast-follow fix, so a reaper takes old things, never the thing just finished.
