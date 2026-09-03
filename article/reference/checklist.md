# Pre-publish gate

Pass/fail. Every item is verifiable by reading the rendered page or pressing one
control — none of them is a judgement call. An article failing any item is not
nearly ready; the failing items are the ones a reader hits first.

## The finding

- [ ] The finding exists as one written sentence, separate from the headline and
      the dek.
- [ ] Every register tells that same finding. None has drifted to a different
      conclusion.
- [ ] Nothing concrete in the article was invented. Every number, date, quote,
      split and error message traces to something real.

## Registers

- [ ] The default register exists and carries the finding.
- [ ] Each register opens with exactly one lead callout.
- [ ] Each register has its own headline — not the h1 repeated, not the h1 with
      a suffix.
- [ ] No register defers to another for the real explanation.
- [ ] Each register is inside its contract's length band.
- [ ] Nothing banned by a register's contract appears in it — no citations in
      the ELI5, no subheadings in the tl;dr, no unsourced numbers anywhere.
- [ ] The ELI5, where present, holds one metaphor start to finish.
- [ ] The technical register, where present, ends by saying what would falsify
      the finding.

## Structure

- [ ] The dek states the question and the stake and does **not** contain the
      finding.
- [ ] At most one category chip, drawn from the property's vocabulary — or none,
      where the property has fewer than two categories in use.
- [ ] No conversion CTA above the article. A utility CTA in the meta row is
      fine; an ask is not.
- [ ] Each register's closing CTA is pitched to that register's depth.
- [ ] Nothing the profile's funnel guard forbids appears anywhere in the
      article — a booking or meeting link most commonly.
- [ ] Sources are a single article-level list.
- [ ] Every citation in the technical register resolves to an entry in it.
- [ ] Where the profile declares a liability gate, the full warning appears in
      every register, unsoftened.
- [ ] On a multipart piece, this part stands alone for a reader arriving from a
      search result.

## Mechanism

- [ ] Tabs work with JavaScript disabled, and land on the default register.
- [ ] All registers are present in the page source, not fetched.
- [ ] Arrow keys move between tabs, and every tab has a visible focus state.
- [ ] A deep link to a register's hash opens that register.
- [ ] Copy, pressed in each register, returns **only** that register, with the
      metadata header.
- [ ] Where only the default register exists, no tab bar renders.

## Build

- [ ] No literal colours in any article component — property tokens only.
- [ ] The page renders correctly on every theme the property ships, light ones
      included.
- [ ] No horizontal scroll at 390px. Wide content — tables, code, diagrams —
      scrolls inside its own container.
- [ ] Images have alt text that says what the image shows, and captions that add
      something the image doesn't.
- [ ] Metadata is filled: title, description, canonical URL, published and
      modified dates, author, category, social card image with alt text.
- [ ] The meta description carries the **finding**, taken from the default
      register — not the dek. A search snippet that poses the question without
      answering it spends the impression and gets nothing back.
- [ ] Body text is readable on every theme the property ships. Where themes
      change the typeface, the article's reading face is fixed.

## Craft

- [ ] `avoid-ai-writing` has been run on each register separately.
- [ ] No stage of that audit is visible in the output.
- [ ] Read the first two sentences alone: they say something, rather than
      preparing to.
- [ ] The article settles something. If it only surveys, it is research and
      should not ship as an article.
