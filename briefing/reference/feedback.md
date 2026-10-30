# Feedback

The shared contract is about a reader's reaction to a slice of a particular brief. Each medium keeps its own way to select and store that slice.

| Field | Meaning |
|---|---|
| `format` | Version of this handoff envelope; currently 1. Distinct from HTML island format 1. |
| `document.id` | Stable brief identity; HTML and Markdown renditions get distinct identities. |
| `document.href` | A locator supplied with the map. Resolve identity and revision against the actual document rather than trusting a basename. |
| `document.medium` | `markdown` or `html` now. Video is reserved. |
| `document.revision` | Content fingerprint the comments refer to, or `null` when it cannot be established. This is distinct from an annotation save timestamp. |
| `comments[].target` | Stable element or block identifier within the document. |
| `title` | Readable target context, or `null` when the exporter has none. |
| `text` | The reader's words, preserved exactly. Empty is valid only with an explicit stance. |
| `stance` | `agree`, `disagree`, or `null` for no stated stance. No comment or unchecked control implies no opinion. |
| `at` | Comment timestamp if known; otherwise `null`. |

See the [editable Markdown example](../examples/engineering.feedback.json). Keep the map beside its document. Supply both to the agent, or copy the map while naming the original document. Map export is not document publication or approval by itself.

Markdown hashes the exact UTF-8 document bytes, so even a rewording flags the old map for review. HTML hashes the authored content region using canonical parser events; transient annotation attributes, the generated section rail and reader-controlled evidence/disclosure state are excluded. Equivalent browser serialization of void elements and implicit table bodies keeps the fingerprint. Renaming an HTML heading changes the revision while its explicit target remains stable. A manual content edit is detected when the helper recomputes that fingerprint.

HTML continues to store native notes in `report-notes`, explicit concurs in `report-concurs`, and the reader-notes mirror. Existing copy maps remain accepted in their original form; the agent may read them with the matching document rather than requiring a new envelope. Never invent a content revision for a legacy map. If it is unknown, verify the targets and context with the reader's document before acting.

To export embedded HTML feedback or a new blank Markdown map:

```bash
python3 scripts/brief.py feedback path/to/brief.html
python3 scripts/brief.py feedback path/to/brief.md
```

To resolve a saved envelope:

```bash
python3 scripts/brief.py resolve path/to/brief.md path/to/brief.feedback.json
```

The helper adds `current_revision`, and each comment gets `status` and `reasons`. A changed revision, unknown revision, different document or missing target produces `needs_review`; the text stays in the output. Exit 2 is a request to inspect those comments, not an empty map. Unsupported format or malformed data produces exit 1 and a visible error.

Resolve feedback before revising. For each comment, answer it, change the brief, or state why it remains open. A resolved target means the comment's location is established; it does not mean the concern is answered. Keep that distinction in the agent's response. A concur applies to the recommendation the reader saw, not automatically to a later recommendation.

HTML's existing native islands lack per-comment content revisions. After a content-changing rebuild carrying old notes, their revision becomes unknown in the exported envelope. The old file is retained as a content-addressed backup. Review old and current context rather than claiming a precise mixed-origin history. A host holding unsaved browser notes must export or save them before regeneration.
