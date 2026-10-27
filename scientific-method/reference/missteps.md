# The weak moves

Every example is set at the same fictional event: the 2023 shooting at the Marston County
Fair, discussed on a podcast by a host and a guest who investigates it independently. A
fictional case keeps the examples about reasoning, and it is also where the grader's traps
live, so that an answer can only come from reading the words.

Each move comes as a pair: the weak version, then the nearest version that is not weak.
The difference between the two is what a grader has to read. A move flags a claim without
refuting it: a claim carried by a weak move can still be true, and this support cannot carry
its weight.

## Resting on an absence

> "Where's the footage from the gate camera? Nobody has released it. Nobody from the security
> firm has come forward. That's the dog that didn't bark."

> "The released gate log shows the camera went offline at 5:12 and came back at 5:58."

The first offers a missing thing as the reason; the second offers an observed one, even
if the conclusion drawn from it is still weak. An absence is strong evidence only when the
thing would surely have surfaced had it existed. Unreleased footage in a pre-trial case
would usually stay unreleased whatever it showed.

## Resting on a private source

> "I know from talking to people in the sheriff's office that they're worried about this."

> "The deputy testified at the hearing that he later learned a drone had been up."

The first cannot be checked by anyone listening. Mark it as what the page cannot check, and
expect a claim like this that comes back "confirmed" to have had only its public half
confirmed.

## Resting on the speaker's standing

> "I can say that with authority. I've hunted for thirty years. I know what that rifle sounds
> like."

> "The report crosses the frame in five frames at thirty frames a second; that is the
> crack of a supersonic round, not the muzzle."

The first asks the listener to accept experience in place of the evidence. Expertise is a
reason to listen closely, and the measurement is the thing to grade.

## Immunising

> "They found his fingerprints on the rifle. Well of course they did. That's exactly what a
> frame-up would look like."

> "They found his fingerprints on the rifle. That's a problem for my theory, and I don't have
> an answer to it yet."

When contrary evidence is recast as proof of the concealment, the claim cannot lose on any
evidence as argued. Combined with a record that contradicts it, the claim *explains away the
record*, and the page says so in those words.

## No named refutation

> "Somebody needs to look into this. There are too many questions."

> "If the plane's track puts it more than a mile from the stage at 5:41, I'm wrong about the
> plane."

The second is good practice and the page credits it, especially when the speaker set this
as their own standard. A named deciding test is the cheapest thing a reader can check, so
check it.

## The hidden-hand leap

> "The plane circled the fairground at 500 feet." (an observation, restated)

> "The plane circled the fairground at 500 feet because it was directing the shooter."

Leap is scored from 0 to 3: how far the proposition goes beyond the observation offered for
it. A proposition at 2.5 or above adds a hidden actor the observation does not contain. A
modest leap that the record does not contradict is *solid conjecture*, the tier that is
worth someone's time to pursue.

## Motive offered as the act

> "The agency wanted him gone; they had every reason."

> "The agency filed a request to restrict the airspace over the fair two days before."

A motive is a reason someone might act. The second is a record of something done, which can
be checked and graded.

## Part of it confirmed, read as all of it

> "The plane circled the fairground at 500 feet, less than a mile from the stage."

The radar confirms the 500 feet and puts the nearest point of the orbit 3.1 miles from the
stage. The confirmed half is the unremarkable half, and the distance was the half the claim
needed. Split compound claims before grading, or grade the part that carries the weight.

## Self-sourced record

> "As I showed in my thread last month, the casing was found two days later."

The speaker's earlier claim is not independent support for the same claim, and neither are
five outlets repeating it. Count independent sources in code and show the count beside the
tier.

## Anomaly hunting

> "A drone was photographed over the fairground forty minutes before the shot. Why was it
> there?"

Every account on the list is comfortable with a drone forty minutes earlier at a county fair.
A row like this is non-diagnostic: striking, consistent with every hypothesis, and so it
carries no weight in deciding between them. A case built mostly of such rows has not yet
offered evidence for itself. See `hypotheses.md`.

## The timed coincidence

> "The plane began descending at the moment of the shooting. That shows coordination."

The radar does show the descent beginning in the minute the first shots were reported. The
record also shows the plane returning to an airport 90 miles away, where a descent for that
approach normally begins about 25 minutes before landing, and it landed at 6:06. Before
crediting any alignment, count the comparable events in the window and measure how often
chance lines up as well (`tools/coincidence.py`). Then check the axes the alignment does not
mention: a descent on time says nothing about where the plane was.

## The moving target

The second firing position is named as the beer tent in the first week, the water tower in
the second, and a parked van in the third, each time after the previous one was checked.
Record every version with its date. A claim whose specifics move each time they are tested
has stopped being one claim, and no single version of it has survived a test.

## Reported speech graded as fact

> "The investigator has said the case was planted."

That sentence is true as a record of what someone said, and it is no evidence that the case
was planted. In a hypothesis matrix such a row has the standing of the claim it
relays and is dropped from the record-only tally.

## The alternative raised and dropped

> "Could it just be a training flight? Maybe. But look at the timing."

The ordinary explanation was named, then set aside without a measurement. This is the most
common move in careful people's
reasoning, ours included, and the page should say where it happened and what measurement
would have settled it.
