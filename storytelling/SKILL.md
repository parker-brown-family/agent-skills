---
name: storytelling
description: Shape anything that has to land on an audience into a story — coaching content, a talk, a launch post, a case study, a demo, or the narration over a video clip. Runs the five-stage HOOK/SHAPE/FLESH/JUDGE/LAND loop as an active coach: reads the draft first, interviews when the writer is stuck, forces a rewrite rather than scoring and moving on. Includes NARRATION MODE for karaoke caption overlays on short-form video, and the LOOP SHORT structure whose ending feeds its beginning. Use when asked to write or fix a story, a talk, a script, a launch narrative, a case study, a video voiceover or on-screen captions; when a draft is accurate but nobody cares; or when Parker says "/storytelling", "tell this as a story", "make this land", "write the narration", "caption this clip".
---

# storytelling — make it land

Most BFS work fails on delivery, not on substance. The training plan is right and
the athlete does not follow it; the architecture is sound and the client does not
fund it; the clip shows a real bug and nobody watches past two seconds. This is
the pass that fixes that, and it is a **coaching loop, not a rewrite service** —
run the stages *with* the person, do not hand back a polished draft they cannot
reproduce next time.

The craft body is vendored under `upstream/` (Ringo Fai, CC BY 4.0 — see
`NOTICE.md`). Read the stage file when you need the depth; this page is the map,
the house layer, and the two BFS-specific modes.

## The loop

| Stage | The question | Depth |
|---|---|---|
| **1 HOOK** | Why should anyone care? Write the ENDING first, then where the audience is now. The gap between them is the hook. | `upstream/framework/01-hook.md` |
| **2 SHAPE** | What is the spine? What does the hero want more than anything? Then three acts: What Is → The Gap → New Bliss. | `upstream/framework/02-shape.md` |
| **3 FLESH** | Show, don't tell. One non-visual sensory detail per act, one moment of imperfection, and one thing REMOVED so the audience infers it. | `upstream/framework/03-flesh.md` |
| **4 JUDGE** | Does it work? Score it, then **force the rewrite before moving on**. | `upstream/framework/04-judge.md` |
| **5 LAND** | Delivery. Simulate the audience: reply with the skeptical questions they are silently asking. | `upstream/framework/05-land.md` |

Three checkpoints do most of the work, and they are pass/fail:

- After HOOK — *"What does the audience now NEED to know?"* If they cannot finish that sentence, the hook is loose.
- After SHAPE — *"Tell the whole story in exactly three sentences, one per act."* If they cannot, the structure is not there yet.
- After FLESH — *"Which sentence would be hardest to defend as necessary?"* That one goes.

**Data stories skip stage 3's sensory work.** For a metrics review or a financial
summary: find the single number they must remember, make it the title, strip the
rest (Knaflic). Sensory detail on a data slide is decoration.

## The house layer — this wins over upstream

- **`~/.claude/writing/house-style.md` is final.** Em dashes and contractions are
  welcome here; where upstream advice and house style disagree, house style wins.
- **Run `avoid-ai-writing` as the last pass** on any prose that ships. Do not show
  the audit — return the finished text.
- **Never invent the concrete detail.** Stage 3 asks for specifics, and the
  temptation is to supply a plausible one. In BFS work the specifics are load
  bearing: a real split, a real error message, a real date. If the detail is not
  known, go and get it or write around it. A fabricated detail is the one thing
  that turns a story into a liability.
- **The story does not soften the finding.** An audit that reads as a narrative is
  still an audit; if the answer is "this does not work", the arc lands there.

## Mode: narration over video

For short-form clips — the sideways reel, a coaching demo, a product walkthrough.
The trend this rides is **karaoke captions**: a short phrase on screen at once,
with a coloured word walking along it in step with the voice, slightly larger as
it passes. It is addictive because it removes the choice to skim.

Do not reveal the phrase word by word. That is the common mistake and it inverts
the effect: a sentence still being assembled cannot be taken in at a glance, so
the eye is stuck at the growing edge and never gets the phrase as a phrase. The
line goes up whole; the highlight only says where the voice is.

Craft constraints, all of which are hard:

- **One idea per card.** If a card needs a comma, it is two cards.
- **Cadence comes from word length, not a flat rate.** "The" and "something" are
  not the same length out loud, and a metronome sounds like one. A good rule is
  `170 ms + 42 ms per character`, clamped to 200–620 ms, plus a beat of about
  180 ms on any word ending in punctuation. Over a card that lands near 170 wpm,
  the pace of a person talking rather than a voiceover performing.
- **Layman's terms, always.** Not *"it issues SIGKILL to a stale PID"* — *"it kills
  a program that already stopped."* The test is whether a person who has never
  written code follows it. If a term must appear, the card before it defines it.
- **The first two seconds are the hook**, and they are a gap, not a summary. Not
  *"an agent restarting a server"* — *"watch it kill its own server."*
- **Present tense, third person, no hedging.** It does the thing; it does not
  "appear to attempt" the thing.
- **The last card is the turn**, not a recap. The audience should finish the clip
  holding a thought they did not arrive with.

Map the five stages onto a clip and the arc is:

1. **HOOK** — the gap, in the first two seconds.
2. **SHAPE** — What it is trying to do → what it cannot see → what it does instead.
3. **FLESH** — one real artifact on screen: the actual error, the actual count.
4. **JUDGE** — read it back at speed. Any card that needs a rewind fails.
5. **LAND** — the turn.

Write narration as a **cue list**, never a paragraph: each cue is `{ at, text }`
against the clip's own clock, so it can be rendered as an overlay rather than
read aloud by a human. Sixty to ninety cues fills a thirty-second short.

### The loop flag — set it on every short unless there is a reason not to

A short that ends is a short that gets scrolled. A short whose ending feeds its
beginning gets watched twice before the viewer notices, and the target is that
they **do not notice for two to four seconds**.

```
SHORT TYPE: NARRATIVE LOOP          TARGET: 25–35 seconds

HOOK          sounds complete, and can grammatically follow the last line
SETUP         the human problem, ≤5 seconds
ESCALATION    why the obvious solution failed
TURN          the unexpected insight
PAYOFF        the actual result, with a real number
LOOP BRIDGE   the last 3–8 words, written to lead into the hook
VISUAL LOOP   final shot matches or motivates the first
```

**The test, and it is the whole gate:** read the final card, then immediately
read the first card. If it sounds intentional, the loop works. Say it out loud —
a loop that only closes on paper falls apart at speed.

Three rules that decide whether it closes:

- **Write the payoff first, then the hook, then the bridge between them.** A loop
  written front-to-back almost never closes: the bridge is a constraint on the
  hook, not a decoration on the ending.
- **Keep the hook grammatically open at the front.** *"The fastest way to break
  something is…"* accepts a preceding clause; *"Here's why my agent failed"*
  cannot — nothing can precede "Here's".
- **Never name the subject again in the bridge.** Repetition is what makes a loop
  visible. *"…and that's when I realised"* closes; *"…and that's why agents fail"*
  announces the seam.

Five shapes, worked examples, and the bridges that do and do not work:
`reference/loop-short.md`. For agent-development shorts the default is the
**sentence loop plus a technical reveal** — the visual loop usually comes free,
because the session returns to the state it started in, which is the failure
being shown.

## Mode: coaching content

Training plans, race-day briefs, athlete check-ins. Same loop, one change: the
hero is the athlete and the "New Bliss" act must be something they DO this week.
A coaching story that ends in a feeling has failed. End on the session.

## Where this lives

Canonical: `~/BROWN-FAMILY-SPORTS/Software/agent-skills/storytelling/`, published
in the public `agent-skills` repo. `~/.claude/skills/storytelling` is a symlink to
it — one file, every agent. Never edit a copy.
