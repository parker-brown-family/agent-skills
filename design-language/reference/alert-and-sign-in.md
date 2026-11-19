# The alert and the sign-in page

Two patterns every app in a family repeats, and the two that drift first when each app's builder
draws its own: how an error looks, and how a person gets in.

## The alert: one error pattern

Every error in every app (a refused sign-in, a failed save, a lost connection) is one block: the
alert colour, an icon, a heading in the display face naming what happened, and one sentence in the
text face saying what to do.

```html
<div class="hw-alert" role="alert" aria-live="assertive">
  <span class="hw-alert-icon" aria-hidden="true">!</span>
  <div><p class="hw-alert-title">This Google account is not on Stone's list</p>
       <p class="hw-alert-text">Ask your practice's owner to add it, or choose another account.</p></div>
</div>
```

- It sits where the eye already is: under the button that was pressed, or at the top of the panel
  the error belongs to. It stays until the next attempt and is announced to screen readers.
- The heading names the cause, never "Something went wrong"; give each cause its own heading. It
  is display-face words, so it holds no figures; a time or a count goes in the sentence.
- Never red helper text, a toast or a modal for an error. Red helper text is easy to miss beside
  the helper text around it; a toast leaves before it is read; a modal hides what went wrong.
- Colours by role: the danger tint, a 1 px danger edge with a 4 px danger edge on the left, a 24 px
  disc in the danger colour with the mark on it. Check R19 holds the words at 4.5:1 on the tint,
  the mark at 4.5:1 on its disc, and the edge at 3:1 on the tint and on the card or page.

The example took the pattern from the dictation app, whose builder had made every error one
block after a sign-in failure on a tablet showed the same sentence for three different causes,
in plain helper text.

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

A provider's own branding rules may ask for its button in its colours and with its mark; read them
before shipping a custom button. The example's apps draw it as their primary button and name the
provider in words.
