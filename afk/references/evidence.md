# Evidence

## Corpus and Count

A local audit on 2026-11-12 found **71 distinct AFK or equivalent continuation
requests**, dated **2026-09-25 through 2026-11-12** (UTC): **43 in Claude Code
transcripts and 28 in Codex transcripts**. This is a bounded search of available
local records, not an estimate of all requests the user has ever made.

The audit searched Claude project JSONL and Codex session JSONL for `afk`,
`build build build`, `unblock yourself`, `I'm away`, `I am away`,
`while I'm away/gone/out`, and `go ahead`, plus tool/verification terms.
It parsed user message bodies, excluding tool-result bodies and duplicate
Codex event copies. Mechanical cleanup removed injected instructions, compacted
summaries, helper boilerplate and repeated text. Of 107 remaining candidate
records, 71 were continuation requests; 36 were ordinary approvals, resource/tool
discussion or a peer's relay. A negated "go ahead" was excluded.

For 17 selected requests, the audit inspected the subsequent conversation,
including up to three later user-form records and relevant assistant/tool
records. Some later records were automated notifications; only actual user
reactions are attributed below. No response is not evidence of satisfaction.

Raw transcripts and the extraction working files were kept outside this public
repository. Dates and generic quotations remain; personal subjects, private
project details, account identifiers and source paths are omitted. The public
digest therefore supports the workflow without reproducing the private corpus.

## Expectations and Reactions

- **2026-10-03:** "DO NOT COME TO ME FOR ANY QUUWESTION.. that would be a failed
  run..." The surrounding request authorizes completion while away. This is
  evidence against asking routine questions; it does not revoke other limits.
- **2026-10-07:** "take your time and think harder if you get blocked". The
  following run reports deliberately breaking guards and catching the mutations.
  The user later says, "seems to be working great!" That reaction supports this
  particular result; it does not independently verify every reported check.
- **2026-11-05:** "Great - afk - feel free to compeltely build the thing!"
  On return: "did we cutover?" and "get us there to test it." A completed build
  still needed a usable test instance. Include cutover only when authorized and
  report whether it actually happened.
- **2026-11-09:** "assume I am AFK and solve / unblock all your own problems".
  The next user continuation was "try to keep going~!" An interrupted session
  needed to resume rather than ask whether to proceed.
- **2026-11-09:** "do not deploy during work day" accompanies an AFK build
  request. A later turn repeats the deployment hold. Broad autonomy preserved
  the explicit restriction.
- **2026-11-09 to 2026-11-10:** after an autonomous benchmark request, the user
  reports "our system froze and died" and asks to "proceed with less aggressive
  workload". Separately, a speech-test transcript reports an uncapped run
  overloading a machine. Use resource caps and serialize heavy jobs; these
  records alone do not prove the freezes' complete causal chains.
- **2026-11-11:** "pause on it. Not to say we run totally blind though."
  This accompanies concern about evaluation spend. AFK did not authorize ignoring
  a new spending limit; cheaper verification and product work remained useful.
- **2026-11-11:** `DON"T RUSH it just to get it done fast..` accompanies repeated
  instructions to build, test and iterate. Later feedback still asks for visual
  changes. Autonomous completion leaves human taste review open.

## Verification Lessons

The 2026-11-09 harness conversation records an evaluation defect: fixes were
available through task git history, and some tasks passed without changes.
The user asks, "Are evals any good actually?" The assistant reports removing
history, checking untouched baselines, and correcting concurrent builds that
shared output. This supports blind cases, baseline checks and isolated runs;
it is not a new independent evaluation of those historical scores.

On 2026-11-12, the user asks whether another worker's test results were actually
incorporated. The assistant acknowledges that it had borrowed the method but
had not yet used those results, then reports writing expected answers before
running a synthetic extraction test. It identifies a number-parsing defect and
adds a regression check. Credit the evidence actually integrated; distinguish
synthetic verification from real-user performance.

## Observed Tool Use

- **Chrome / ChatGPT:** direct user requests name browser research; browser tool
  records on 2026-11-09 show a bounded outside research question being submitted.
  A 2026-11-12 request proposes outside-generated fictional speech for testing.
- **NotebookLM / Garrison:** on 2026-11-05 and 2026-11-09 the user asks for notebook
  research alongside ChatGPT and local investigation. The November 9 tool trace
  searches an existing notebook index, creates a notebook, submits 15 public
  source URLs and starts an Audio Overview with a focused question about evidence
  and disagreement. Later reader notes concur with the public-source boundary.
  Final audio playback and today's live UI were not verified in this audit.
- **research-delight:** direct AFK requests name it for research and getting
  unblocked. Its local README confirms a manual, gap-driven research flow with
  source requirements and stop budgets. Using it does not imply permission to
  launch the optional automatic agent gatherer.
- **Second machine / voice:** requests and subsequent reports use a remote machine
  for speech generation and a separate capped recognition profile. No private
  SSH alias or machine identity is needed in the public instructions.
- **Jev / Terminal Delight:** requests explicitly authorize typed judgment tools
  and coordination with seated workers. The current work order's live
  `floor_position` check confirmed an incoming prompt line and no outgoing lines;
  the author worked alone. Optional tooling was not installed or exercised merely
  to complete this inventory.
