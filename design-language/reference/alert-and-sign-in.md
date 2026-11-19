# Notices, status in rows, and the sign-in page

Two patterns every app in a family repeats, and the two that drift first when each app's builder
draws its own: how an error looks, and how a person gets in.

## Notices: one pattern, four levels

A notice tells a person something about the page they are on. One anatomy, four levels, and the
level decides the colour roles, the icon, how it is announced and where it sits.

| Level | For | Roles | Icon | Announced | Where |
|---|---|---|---|---|---|
| failed | something went wrong | danger | a disc with "!" | `role="alert"` | under the button that was pressed, or the top of its panel; until the next attempt |
| attention | something needs the person | warning | a triangle | `role="status"` | the top of the section it concerns; until resolved |
| mode | you are in an unusual mode | the mode band | a person | a labelled region | a strip above the header, on every page, never dismissable |
| worked | it worked, and nothing else on screen shows it | success | a check | `role="status"` | where the action was; the person may close it |

```html
<div class="hw-notice attention" role="status"><span class="hw-notice-icon" aria-hidden="true"></span>
  <div><p class="hw-notice-title">The card on file expires this month</p>
       <p class="hw-notice-text">Ask the client for a new card at their next visit.</p></div></div>
```

- The in-page levels are one block: the level's tint, a 1 px edge and a 4 px left edge in the
  level's ink (3:1 on any ground, light or dark), the icon, a display-face heading naming what
  happened, one text-face sentence saying what to do or what it means. The heading holds no
  figures; a time or a count goes in the sentence.
- `.hw-alert` is the failed level, the one error pattern. The example took it from the dictation
  app, whose builder had made every error one block after a sign-in failure on a tablet showed the
  same sentence for three different causes, in plain helper text.
- **The mode strip** says you are acting for someone else (support staff working in a customer's
  account, every action recorded) or using a test instance. It belongs with the header: above
  it, full width, sticky with it, so the folio tab still opens into the page. Its band is inverse
  to the page in the product's deep tone (dark under a light page, light under a dark one), seen
  at a glance without a status colour; names are content, so its words are the text face; its one
  button leaves the mode. Prefix the page title too. The example's first try was the alert's shape
  in the selection colour, inside the page: it scrolled away and read like a selected card.
- **Never a notice:** a field's own error (its hint, under the field), a routine save (the state
  shows itself), a row's state (below), a question before a destructive act (a dialog), tips, news
  or promotion, loading, an empty page. A toast is never used for an error.
- Checks: R19 (each in-page level's heading and sentence 4.5:1 on its tint, the icon's mark 4.5:1,
  the edge 3:1 on the tint, surface, ground, raised and float) and R21 (the strip's words 7:1 on
  the band, the band 3:1 against the page ground and the header's bare ground).

## Status in a row

A row's state is not a notice. One vocabulary across every table: a word and an icon, never colour
alone, with any reason beside it.

| State | Roles | Icon | In the example |
|---|---|---|---|
| waiting | neutral | a clock | going out, not yet due, booked |
| done | done | a check | delivered, paid, attended |
| held | warning | a pause | held by a test instance (with why), no consent, card needed |
| refused | danger | a cross | bounced, declined, no-show |
| unknown | neutral, dashed | ? | no answer, and nothing will be guessed |

`<span class="hw-status" data-status="held">Held</span> <span class="hw-status-why">a test server sends only to the people who sign in to it</span>`.
Unknown is its own state: a message with no answer is counted as neither delivered nor failed.
Check R22 holds each word at 4.5:1 and each icon at 3:1 on its tint.

## The sign-in page

The same page in every app, and only what works on that instance.

- A one-row glass header (`.hw-header.single`): the wordmark and the theme switch. The wordmark
  stays on a phone; it is where the product is named before anything else.
- One card (`.hw-signin-card`, 400 px wide at most, about a seventh of the window from the top; full
  width on a phone), with the product's signature as a bar on top: the title "Sign in to
  <Product>" in the display face, one line saying which account, then the sign-in button, full
  width, the one filled button on the page.
- **When only an identity provider works** (the example: Google), that is all. No email or password
  field, no "or", no "Forgot password?", no "Create account" unless the instance can create one.
  The example found four apps drawing four layouts, each with a password form on an instance
  where only Google worked.
- **When password sign-in is on**, it comes under the provider's button: "or", the two fields with
  their labels above, an outlined "Sign in", and "Forgot password?" only where reset works.
- **A refusal** is the alert, under the button that was pressed, with one heading per cause: nothing
  came back from the provider, the server refused (the time in the sentence, to match the log), the
  account is not on the list (naming it), no connection, too many attempts. A sheet the person
  closed says nothing.

A provider's own branding rules ask for its mark on any custom button. The example draws the
sign-in button as its primary button, with Google's "G" unaltered on a white square at its left
(`.hw-signin-g`), the words in the display face.
