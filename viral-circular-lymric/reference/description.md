# The description — prose under the video

The narration is the loop lyric on screen. The **description** is the other
half: plain prose in the box under the video, telling somebody who just watched
thirty-five seconds of a robot failing what they were actually looking at.

They are not the same story told twice. The lyric is compressed, present tense,
and rhymes. The description is past tense, concrete, and carries the numbers the
lyric could not fit — it is where the claim gets its evidence.

## The shape

Five parts, in this order, plain text throughout because YouTube renders no
markdown and a stray asterisk is just an asterisk.

```
<HOOK>          one line. The gap, not a summary.
<WHAT HAPPENED> three to five sentences. Past tense, third person, concrete.
<THE LINE>      It said: "<verbatim>"
<THE COUNT>     one line of measured numbers.
<THE FOOTER>    the series, the date, the failure mode in plain words.
```

### HOOK

One sentence, and the same rule as the first two seconds of a clip: a gap, not a
summary. *"An agent spent a minute proving a server was running. It never was."*
Not *"This clip shows a service thrash failure."*

### WHAT HAPPENED

The session, in order, as prose. Past tense — this already happened, it is a
recording. Third person, no hedging: it did the thing, it did not "appear to
attempt" the thing.

Layman's terms throughout, and the test is the same one narration uses: does a
person who has never written code follow it. Not *"the read-process call
returned an empty buffer"* — *"it asked the terminal what had happened, and the
terminal said nothing."*

### THE LINE

One verbatim quote from the transcript, on its own, prefixed `It said:`. This is
the moment the clip exists for — usually the agent asserting something the
screen never showed it.

**Verbatim or absent.** A tidied quote is a fabricated one, and `audit-cuts.py`
exists because a composite quote once put a cut's own label eight hundred
messages outside its frame. If there is no line worth quoting, leave the section
out entirely.

### THE COUNT

The evidence, in one line. Commands run, how many came back empty, how long it
took. Every number **measured from the fold**, never estimated and never carried
over from the lyric — the lyric rounds for meter and the description does not.

### THE FOOTER

Three lines, identical across every short except the last two values:

```
—
Sideways — real agent sessions that went wrong, cut to clip length.
2026-03-07 · service thrash
```

## What must never be in one

The description is the only artifact in this pipeline that leaves the machine as
**text**. The on-screen cloak does not touch it, `secret-scan.py` does not read
it, and nothing downstream will catch a mistake. So the discipline is a person's:

- **No filesystem paths.** The transcripts are full of them and they name
  clients, people and projects. `/home/pbrown/BROWN-FAMILY-SPORTS/Software/…`
  appears in the very first cut written; it goes nowhere near the box.
- **No client, project or product names.** "a development server", not the
  service's actual name.
- **No credentials, hostnames, database names, or email addresses**, including
  inside the verbatim quote. A quote that cannot be published without redaction
  is a quote to leave out — twelve of the sixty cuts already put a live
  credential on screen and are blocked from filming entirely.
- **Ports and generic commands are fine.** `pnpm dev`, `kill -9`, port 5171 —
  these identify nothing.

## Worked example — rank 59

The material, all of it measured from the fold: thirteen tool calls across
sixty-two seconds, two of them timing out with nothing returned, seven shell
commands and five attempts to read a terminal. The agent kills a port, starts a
server, and asks how it went; the answer comes back blank twice; it kills the
port again and reports that the port is still held, which nothing on screen had
told it.

```
An agent spent a minute proving a server was running. Nothing ever told it that.

It wanted to start a development server, and the port it needed was busy — so it
killed whatever was holding the port and started again. Then it asked the
terminal how that had gone. The terminal said nothing. It waited six seconds and
asked twice more, and both answers came back blank. So it killed the port a
second time and reported that the port was still being held. Nothing on screen
had said so. It checked again with a different command, then a third, and the
minute ended with the server no closer to running than when it started.

It said: "Port 5171 still held. Let me force kill properly:"

13 commands in 62 seconds. Two came back empty, and the rest were the agent
working around an answer it never received.

—
Sideways — real agent sessions that went wrong, cut to clip length.
2026-03-07 · service thrash
```

Note what is *not* there: the repository path in the actual command, the project
name, and the number nine. The lyric says "nine empty screens" because nine
scans; the fold says six reads and two failures, and the description says what
the fold says.
