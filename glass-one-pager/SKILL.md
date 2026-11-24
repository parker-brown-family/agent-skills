---
name: glass-one-pager
description: "Make a one-page PDF that shows what someone builds, drawn as a terminal window: a sidebar of projects beside a curved-glass CRT screen over a wallpaper, with every row a live link and the text sharp and selectable. Use for a portfolio one-pager, an open-source one-pager, a work sample, an 'upload anything' slot on an application, a conference or grant leave-behind, 'one-page PDF of my projects', 'make it look like a terminal', 'show off my contributions', or 'glass one-pager'. Everything on the page comes from one content file and everything about the look from one theme file."
license: MIT
---

# Glass One-Pager

One page, for a screen and never for print, that makes a reader want to click. The sidebar says what was done. The glass says why each
project exists and what its author loves about it. An example is in `examples/open-source/`.

A PDF can't restyle itself or answer a hover. It can hold live links and vector text, so this page leans on both: each line on the glass is
set along its own curve, which keeps the bulge of a tube and still lets the reader select, search and zoom.

## Make One

From this skill's directory:

```bash
python3 scripts/onepager.py new my-page
python3 scripts/onepager.py build my-page/content.json
python3 scripts/onepager.py check my-page/content.json
```

`new` writes a content file to fill in. `build` writes the HTML and PDF beside it, and a PNG where `pdftoppm` is installed. `check` compares
every GitHub pull request on the page with its real state. Python's standard library, plus Chrome or Chromium; `check` needs `gh`.

1. **Gather before writing.** List the person's real work: merged and open pull requests, releases, reported issues, their own
   repositories. Read each one. Never take a claim from a résumé or an older page without opening what it points to.
2. **Choose five or six projects.** Each gets three to five items. Anything more goes in `closed`: a name and a link, like a folded
   folder. Four closed items is plenty.
3. **Write `why` as a fact** about the project, in one line. Someone who has never heard of it should know what it is.
4. **`love` is the person's own sentence.** Ask for it, one project at a time. If you draft one, say which are drafts, and say so again
   when you hand the page over. Nothing else on the page is worth as much.
5. **Keep items to about five plain words**: what changed for somebody, not the pull request's title.
6. **Build, then open the PDF and look.** Show the person the page itself, not a description of it.

## Say Only What Is True

- **A mark is a claim.** `done` means merged, fixed or shipped. Work in someone else's project is `open` until they take it. A change a
  maintainer carried in under their own pull request is "carried into", never "merged". `check` exits 1 when a mark no longer matches,
  and also when a pull request can't be read: unknown is never a pass. Run it every time before the page goes out.
- **A report is not a patch.** "Six issues reported, all fixed" is honest when the maintainer wrote the fixes.
- **Public work only**, unless the person says otherwise. A link a reader can't open is worse than none.

## Keep Private Things Out

`build` refuses placeholders left unfilled, links to a local or private address, home-directory paths, and email addresses or phone numbers.
A page that should carry contact details says `"contact_is_public": true`, and only the person it belongs to decides that. The HTML beside
the PDF holds paths from your machine: send the PDF, never the HTML.

## Change the Look

The default is Deep Quiet: a CRT, forest green and ivory, over a mining robot on an asteroid. All of it is yours to change.

```bash
python3 scripts/onepager.py themes
python3 scripts/onepager.py theme my-look --wallpaper picture.jpg --dir my-page
python3 scripts/onepager.py build my-page/content.json --theme my-page/my-look.json
```

A theme is one JSON file: a wallpaper and its blurred copy, the colours by role, and the glass. [reference/themes.md](./reference/themes.md)
says what each knob does, and how to make the glass clearer or flatter. Change the theme file, not the script. Use a picture the person made
or may redistribute, and record whose it is.

## When It Refuses

| It says | Do this |
|---|---|
| the screen holds more words than fit | Shorten `why` and `love`, or fold a project into `closed` |
| sidebar line too long | Rewrite that item shorter; it names it |
| no room for the note | Shorten the longest line on the glass, or drop `note` |
| placeholder left in | Fill that field, or delete it |

The type grows and shrinks to fill the glass, so cutting words makes the page easier to read. If the screen type falls under 16 px, cut.
