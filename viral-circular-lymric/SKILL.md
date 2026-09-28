---
name: viral-circular-lymric
description: Write a short-form narration as a CIRCULAR LYRIC — a rhymed verse whose last card feeds its first so completely that the replay reads as the next line, closing on grammar, rhyme and meaning at once. Use when writing or fixing narration for a looping short (YouTube Shorts, TikTok, Reels), when a loop "closes on paper but you can still hear the seam", when asked to make captions rhyme or scan, or when Parker says "/viral-circular-lymric", "make it lymric", "make it loop like a poem", "circular lyric". Extends the LOOP SHORT structure in /storytelling with the three-way close.
---

# viral-circular-lymric — the loop you cannot hear

A looping short that ends is a short that gets scrolled. A short whose ending
feeds its beginning gets watched twice before the viewer notices, and the target
is that **they do not notice for two to four seconds**.

`/storytelling` already carries the LOOP SHORT: write the payoff first, then the
hook, then the bridge between them, and keep the hook grammatically open at the
front. This skill is the harder version of the same move. A prose loop closes on
grammar alone, and grammar alone leaves a seam you can hear — the sentence
continues but the *music* restarts, and the ear catches the join even when the
reader cannot say why.

A circular lyric closes on three things at once.

## The three-way close

Read the last card, then the first two, out loud. All three must hold:

| | The test | Fails like this |
|---|---|---|
| **Grammar** | The last card and the first form one continuous sentence. | *"nine blank screens"* → *"the hardest thing to read"* — two sentences touching, not one running on. |
| **Rhyme** | The last card's final word rhymes with the first card's final word. | *"…and never sees"* → *"the quietest kind of trying"* — sense carries, sound stops dead. |
| **Meaning** | The sentence the loop completes says something the clip earned. | The join scans and rhymes but states a fact already given. Pretty, and the viewer leaves. |

Two of three is the trap. Grammar plus meaning is where most loops land, and
Parker's word for it is **"really close"** — which is the sound of a rhyme that
did not arrive.

## How to build one

**Write the frame sentence first.** Not the hook, not the payoff — the single
sentence the whole loop is. It must be true of the clip, and it must be able to
start and end on the same idea:

> *The loneliest thing a robot does is ask a quiet screen… and never knows it
> was the loneliest thing a robot does.*

Everything else is that sentence, opened up and filled with the real beats.

**Split the frame across the two ends.** The opening half becomes card 1 (and
often card 2); the closing half becomes the last card. Now you have the seam
before you have the poem, which is the whole point — a bridge written last
almost never closes.

**Pick the seam rhyme before the body.** The last card's final word and the
first card's final word are a couplet, and couplets are found, not forced.
`does / was`, `again / then`, `knew / to`. If the pair does not exist, change
the frame sentence — do not bend the last line around a rhyme it cannot reach.

**Then fill the middle against the real beats.** Every card still has to be true
about what is on screen. The verse is the delivery; the failure is the content,
and a rhyme that requires inventing an event has cost more than it bought.

## The constraints that do not move

Inherited from `/storytelling` narration mode, and none of them are negotiable
just because it now rhymes:

- **One idea per card.** If it needs a comma, it is two cards.
- **Seven words maximum.** Meter tempts you past this; the card does not grow.
- **Layman's terms.** *"he shuts the door he opened"*, never *"it SIGKILLs the
  listener"*. If a term must appear, the card before it defines it.
- **Present tense, third person.** It does the thing.
- **The card is a phrase, not a line of a poem you are proud of.** It goes up
  whole and a highlight walks it; nobody sees your enjambment.
- **Anchors are fixed.** A rewrite changes words, never which beat a card lands
  on. The anchors were validated against the fold; the rhyme is not a reason to
  re-argue them.

## Meter, lightly

Loose ballad measure carries this better than a true limerick. Seven syllables
with sixes on the turns reads as verse without becoming sing-song, and sing-song
is fatal over real failure footage — the bounce starts to sound like mockery.

A **true limerick** (five lines, AABBA, anapestic gallop) is a different and
much stronger flavour. Use it only when the subject can take being laughed at.
It cannot when the clip shows somebody's production database being dropped.

## Warmth is aimed at the character, not the damage

These clips are recordings of real failures — a wiped database, five repos
force-pushed, twelve hours lost. Cute lands two ways, and the difference is
entirely whether the verse is warm toward **the robot** or amused by **the
wreckage**.

*politely*, *just to be sure*, *a kinder question*, *he doesn't know* — those
are sympathy for something trying its best in an empty room, and they are safe
over any footage. *"watch this idiot nuke prod"* is the same joke pointed at the
person whose day it was.

Decide per clip, never as a blanket style. A thrash loop where nothing breaks
can be adorable. A destructive cut should be warm and quiet, or plain.

## The gate

Say it out loud. A loop that closes on paper falls apart at speed, and every
failure of this form is audible before it is explainable.

```
last card  →  first card  →  second card
```

If you hesitate at the join, it has not closed. If you hear the rhyme arrive and
the sentence keep going, it has.

## Worked example

Rank 59, a service-thrash cut: an agent starts a dev server, asks how it went,
gets a blank screen, waits, asks twice more, kills the port, reports the port
was busy — which nothing on screen ever said — and repeats nine times in a
minute.

Frame sentence: *the loneliest thing a robot does is ask an empty screen, and
never know it was.*

```
 1  the loneliest thing a robot does     A
 2  is ask an empty screen
 3  he wakes the little server
 4  and asks it how it's going           B
 5  the screen has nothing on it
 6  and has no way of knowing             B
 7  he asks again, politely
 8  then twice more, to be sure           C
 9  he shuts the door he opened
10  and says the door is stuck
11  though nothing ever said so
12  he checks the screen once more        C
13  he tries a kinder question
14  nine empty screens. one minute.
15  and never knows it was                A
```

The seam:

> *…and never knows it was* / *the loneliest thing a robot does* / *is ask an
> empty screen.*

Grammar runs on. `was` rhymes with `does`. And the sentence it completes is the
one thing the clip is actually about — he never finds out. Three-way close.

Card 10 is the failure and survives the verse intact: he shuts the door himself,
then reports it stuck. Losing that to a rhyme would have made the poem
decoration.

## Where this lives

Canonical: `~/Work/writers-block/skills/viral-circular-lymric/`, in the private
`writers-block` repo since 2026-09-28. `~/.claude/skills/` symlinks it. One file,
every agent — never edit a copy.

Craft parent: `/storytelling`, whose LOOP SHORT section this extends. The
upstream body there is Storyteller by Ringo Fai, CC BY 4.0.
