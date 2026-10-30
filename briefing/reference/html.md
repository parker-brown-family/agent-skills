# HTML

Read the sibling `decision-brief/reference/pictures.md` and `reference/glass.md` before drawing. Reuse `fancy-pants-brief` for the house look: dark glass over one random Omarchy wallpaper, themed ink, gel controls and a section rail. The new brief keeps its chosen purpose; using the assets does not turn every brief into a decision request.

Start from [the engineering source](../examples/engineering.src.html). A complete source has one `<!--BRIEF:head-->` slot in its head, one `<!--BRIEF:notes-->` slot at the end of its body, and one `<!--brief-content-->` / `<!--/brief-content-->` pair around the authored header and main. The assembler rejects unknown or repeated slots.

Give each significant comment target an explicit stable id and matching `data-brief-anchor`. Every section heading and figure needs one. Use the same id after renaming the heading; never reuse a removed id for a different claim.

```html
<h2 id="sec-return" data-brief-anchor="sec-return">Returning a comment</h2>
<figure id="fig-target" data-brief-anchor="fig-target">
  <span class="lbl">01 · A comment's target</span>
  <!-- Draw the mechanism here. -->
  <figcaption>A removed target keeps its comment unresolved.</figcaption>
</figure>
```

Build with `scripts/brief.py html SOURCE OUTPUT --id STABLE-ID --purpose PURPOSE`. It reads the existing canonical notes assets, with a checked one-line adaptation for explicit anchors. There is no forked asset or storage-format migration. Rebuild through the same command; do not paste empty notes islands over a reader's comments.

The output is self-contained for its rendering and annotation UI. Evidence links are deliberate navigation to adjacent files; share their directory when those sources must travel with it. Drawing assets and scripts are inline, with no CDN or network dependency. A linked evidence note is not a rendering dependency.

The new output's handoff bridge shows an unresolved-feedback notice when carried comments have an unknown revision or missing target. Copy Map includes those removed targets and their reader text. The older skill's map generator and storage stay unchanged.

On rebuilding an existing output, the tool preserves its wallpaper, both notes islands including revisions, and the last reader-notes mirror byte for byte. It validates the old islands before replacement and keeps the old bytes in a content-addressed `.bak` file. Detected concurrent writes cause refusal; editing and rebuilding simultaneously still needs host-level coordination. Never claim an atomic replace is a full multi-writer transaction.

If a canonical source hook changes, assembly stops for review. Do not silently remove the guard or mutate the older skill to make this one pass. Review and update the small adaptation alongside its tests.

Verify with the sibling glass gate, this skill's local-link checker and an isolated headless browser. Check at a narrow pane width and a phone width. A figure's text must fit its own viewBox, not merely avoid page overflow. Every important target needs an actual note control; a total count cannot establish coverage.

In Terminal Delight, the native reader can submit comments into the original HTML. A standalone browser stores live edits in localStorage and exports a map. Test the host's persistence path before reporting a disk save. The existing notes engine can restore a browser-held comment deleted by another writer; this skill does not claim to solve that conflict.
