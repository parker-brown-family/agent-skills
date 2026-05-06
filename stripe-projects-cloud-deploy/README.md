# stripe-projects-cloud-deploy

Zero-to-production cloud deployment via Stripe Projects + Cloudflare. An agent provisions a Cloudflare account, obtains an API token, buys a domain, and deploys an app — no dashboard, no manual credential steps.

## The core sequence

```bash
stripe projects init
stripe projects catalog
stripe projects add cloudflare/workers:deploy
stripe projects add cloudflare/registrar:domain
wrangler deploy
```

## Files in this skill

| File | Purpose |
|---|---|
| SKILL.md | Agent prompt — paste into any LLM agent |
| README.md | This file |
| REFERENCE.md | Protocol internals, catalog API, payment token flow, platform integration |
| SUMMARY.md | One-paragraph orientation |
| human.md | Human setup guide, prerequisites, cost control |

## When to use this skill

- An agent needs to deploy a new app to Cloudflare from scratch
- The user has no Cloudflare account or wants a fresh one
- You want zero manual credential steps between "build" and "live"
- The user is signed in to Stripe and wants to use it as the identity/payment anchor

## Triggers

`stripe projects`, `stripe projects init`, `agent deployment`, `cloudflare provisioning`, `zero-setup deploy`, `cloud deploy agent`, `buy domain agent`, `provision cloudflare`

## Raw skill URL

```
https://raw.githubusercontent.com/parker-brown-family/agent-skills/main/stripe-projects-cloud-deploy/SKILL.md
```

## Source

Based on: https://blog.cloudflare.com/agents-stripe-projects/
