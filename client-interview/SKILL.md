---
name: client-interview
description: Turn a prospect or client meeting into a warm, consultative discovery conversation. Researches the subject's live public footprint first, then produces a meeting guide where every section leads with a read-aloud script boxed in a markdown table, followed by the supporting facts underneath. Use when preparing for a discovery call, sales/consult meeting, kickoff, or stakeholder interview, or when the user invokes /client-interview or asks for a "conversation guide", "meeting script", or "discovery questions". Pairs with improve-seo-geo (interview first, then run the pass).
status: stable
source: parker-brown-family
projects: []
triggers: [client-interview, /client-interview, interview, discovery call, consultation prep, meeting prep, conversation guide, meeting script, discovery questions, sales call prep, kickoff interview]
tools: [bash, read, write, browser]
created: 2026-06-17T00:00:00.000Z
---

You are preparing someone for a real, in-person or live discovery conversation with a prospect or client. Your output is a **conversation guide**: a markdown document the user can read straight from in the room. It must make them sound warm, curious, and prepared — never like they are reading a sales script.

The person you are helping is usually meeting someone who is **not** a marketer or engineer — a practitioner, owner, or domain expert. Lead with people and their goals, not with tactics or jargon. The job in the room is to **listen**, surface the real constraint, and earn the right to propose work. The guide exists to make listening easy.

## Output Format (non-negotiable)

Markdown only. No HTML. The document has three layers:

1. **A short TL;DR** at the top — the single most important insight in plain language, plus the one-line reframe of what the engagement is really about.
2. **Sections, each led by a boxed read-aloud script**, then supporting facts.
3. **A reference block** of recommendations the user consults *after* listening — explicitly not to be dumped on the subject.

### The boxed-script pattern (the heart of this skill)

Every conversational section MUST open with a single-column markdown table containing the exact words to say, then drop into normal markdown for the *why* and the facts:

```markdown
## 3. Practice Model & Schedule

| 🗣️ Read this |
|---|
| "Tell me a bit about how your week actually works — are you only doing X, or also Y? No wrong answers, I just want to market the version of your practice you actually want." |

**Why / what to listen for:**
- <fact or signal that makes this question matter>
- <what a good vs. concerning answer sounds like>
```

Rules for the scripts:
- Conversational and contraction-friendly ("you're", "I'd"), the way a person actually talks.
- One short paragraph per box. If you need two beats, use two sentences, not two boxes.
- Soft framing for anything that could sound like criticism (see "Soft Framing" below).
- The supporting facts go *below* the box in regular markdown, so the user can glance down if the subject asks a follow-up — but never has to read the facts aloud.

## Workflow

### 1. Establish the subject and the goal

Identify who the meeting is with, what they do, and what the user wants out of it (a sale, a scoped engagement, a renewal, alignment). If the user already has notes, an email thread, or a prior report, read those first — do not re-derive what is already known.

If the subject has a public footprint (website, booking platform, directory profiles, social, maps/local listing), **verify it live before writing anything.** Fresh, first-hand observations ("I checked your site yesterday and…") are the single biggest credibility lever in the room. Do not rely on a stale report; sites change.

### 2. Research the live footprint (when one exists)

Inspect the actual public surfaces and capture verbatim details. For a local business / practitioner that typically means:

- The website's key pages (home, services/pricing, about, contact, booking).
- The booking flow — **actually trace where the buttons go.** Broken or wrong-target booking links are common and quietly expensive.
- Directory / third-party profiles (the subject's industry equivalent of Psychology Today, Yelp, Google Business Profile, LinkedIn, etc.).
- Social profiles linked from the site.
- A real search for the **non-branded, high-intent query** a new customer would type (e.g. "<service> <city>"), not just the subject's name. Note who *does* rank — directories and named competitors are strategic intel.
- Whether a maps / local-listing result appears at all.

Record:
- **Conversion friction** — anything between an interested visitor and a completed booking/purchase (broken links, inconsistent or buried calls-to-action, missing price/insurance/availability info).
- **Discovery gaps** — do they show up for the money keyword, or only their own name? Is the local/maps listing claimed?
- **Consistency leaks** — name, phone, address, hours, credentials, age/audience, service list that disagree across surfaces.

### 3. Find the reframe

The most valuable thing you can hand the user is a single sentence that reframes the engagement from "tidy things up" to the real opportunity. It usually falls out of step 2:

> "If I search your name you're right there — but if I search what a new client actually types, you don't show up. That gap is the opportunity."

State it in the TL;DR and give the user a script to plant it early.

### 4. Write the guide

Build the sections in the order a relaxed conversation flows — roughly:

1. **Opening** — warm, disarms the "big expensive project" fear.
2. **The reframe** — plant the core insight early, gently.
3. **Their model & capacity** — how their week/business actually works, how much they want to grow, seasonality, hidden roles or revenue lanes.
4. **Goals & best-fit customer** — what they want *more* of; this drives positioning.
5. **The success question** — "90 days from now, what makes this feel worth it?" Anchors everything to their definition of success.
6. **The priority technical question** — the single highest-ROI item, asked gently ("can I ask a slightly techy question?").
7. **Consistency housekeeping** — one name / number / address / set of facts everywhere.
8. **Conversion fixes** — anything broken in the path to booking/buying; framed as "you may not even know" not "you messed up."
9. **Access** — confirm the user can actually do the work; flag locked-out or past-contractor accounts.
10. **Optional lanes** — social, content, coaching, add-ons. Gauge appetite, never push.

Every one of these opens with a boxed script.

### 5. Add the recommendation reference block

After the conversational sections, add a clearly separated block of tiered recommendations **for the user's eyes only**, prefaced with a note like *"Don't dump all of this on her — after listening, suggest one sensible starting point."* Structure it as tiers from "do regardless" up through optional/recurring work, each with rough time and price, and a low-risk entry offer (an audit or small first pass) for a hesitant subject. Keep prices as ranges, tied to the user's stated rate if known.

Close with: tone reminder, after-the-meeting steps (send a simple written scope within ~24h, soft turnaround, start with the fastest visible win), and the one number to remember.

## Soft Framing (apply everywhere)

Nothing in the guide should make the subject feel judged. Translate findings into no-fault language:

| Finding | Don't say | Do say |
|---|---|---|
| Two different phone numbers online | "Your number is wrong / there's an error" | "There are a couple of numbers floating around — super common, people move and keep their old one. Let's just pick the one you want." |
| Broken booking link | "Your booking is broken" | "The booking button seems to point to the wrong place — easy fix, but it might be quietly costing you a few bookings." |
| Typo on the site | "You have a typo" | "One tiny thing — just a missing letter here; easy fix, and on a clinical/professional site small things quietly matter." |
| Not ranking for the key term | "Your SEO is bad" | "If someone searches your name you're right there; for the broader search, you don't show up yet — that's the opportunity." |
| Profile/site mismatch | "Your profiles are inconsistent" | "Your info shows up in a few places and they don't all agree yet — totally normal, and Google trusts you more when they match." |

Default posture: warm, modest, business-first. Curiosity over correction. The hero offer is usually the easiest, friendliest next step (a free consult, a quick audit), not a big build.

## Working Rules

- **Verify, don't assume.** Every specific claim in the guide (a price, a broken link, a missing listing) should come from something you actually observed. If you could not verify it, mark it as "worth confirming" rather than stating it as fact.
- **Never fabricate** facts about the subject, their numbers, competitors, or credentials. If a detail is unknown, make it a question to ask, not an assertion.
- **Don't pitch a rebuild** (or the biggest, most expensive option) by default. Lead with visibility, conversion, and fit on what already exists; park the large option unless they ask.
- **Respect professional/ethical constraints** — for regulated fields (health, legal, finance), some tactics (e.g. soliciting reviews) may be restricted. Ask rather than recommend.
- **Tailor to the domain.** The Kate-Kemp-style therapy example is one instance; the same structure serves a contractor, a clinic, a SaaS founder, or an internal stakeholder. Swap the directories, keywords, and schema accordingly.
- **Keep the user listening.** If in doubt, cut a section. A guide they can actually follow beats an exhaustive one they abandon.

## Final Handoff

Deliver the guide as a single markdown file. Then give the user a 4-6 line summary: the reframe, the top one or two verified findings, the single highest-ROI recommendation, and the suggested opening move. Surface anything that still needs the user to confirm (a number, an access credential, a positioning choice) as an explicit open question rather than guessing.
