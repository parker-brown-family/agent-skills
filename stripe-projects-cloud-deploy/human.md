# stripe-projects-cloud-deploy — Human Guide

## What This Is

This skill teaches an LLM agent to take a user from zero cloud infrastructure to a live production app — without the user ever touching a dashboard, copying an API token, or entering credit card details into a CLI.

It uses **Stripe Projects** (currently in open beta) as the orchestration layer: Stripe holds the user's identity and payment method, and passes both to Cloudflare via a standardized protocol so the agent can provision and deploy autonomously.

Source: https://blog.cloudflare.com/agents-stripe-projects/

## Prerequisites

1. **Stripe account** (free) at stripe.com — the user must be signed in
2. **Stripe CLI** installed: `npm install -g @stripe/stripe-cli` or `brew install stripe/stripe-cli/stripe`
3. **Stripe Projects plugin**: `stripe plugins install projects`
4. **Node.js** (for Wrangler): `npm install -g wrangler`

No Cloudflare account required. One gets created automatically.

## How to Use the Skill

**Option A** — paste the raw URL into your agent's system prompt:

```
https://raw.githubusercontent.com/parker-brown-family/agent-skills/main/stripe-projects-cloud-deploy/SKILL.md
```

**Option B** — copy the SKILL.md body into your agent framework (Augment, Claude Code, Cursor, Codex, etc.).

## What the Agent Will Do

When triggered (keywords: `stripe projects`, `deploy to cloudflare`, `zero-setup deploy`, etc.):

1. Verify Stripe CLI and plugin are installed
2. Confirm the user is logged in to Stripe (`stripe login` if not)
3. Initialize a Stripe Project (`stripe projects init`)
4. Query the service catalog (`stripe projects catalog`)
5. Provision Cloudflare account + API token
6. Register a domain (with user confirmation on domain name)
7. Deploy the app (`wrangler deploy`)
8. Verify the live URL is responding

## What the User Actually Touches

Only four things:
1. `stripe login` — one browser OAuth popup, done once
2. Add payment method if missing (stripe.com/settings/billing)
3. Confirm the domain name before purchase
4. OAuth consent if an existing Cloudflare account is being linked (one click)

## Cost and Budget

- Stripe enforces a **$100/month cap per provider** by default
- The agent cannot spend beyond this without user action
- To raise the cap: Cloudflare dashboard > Budget Alerts
- Domain registration is a one-time charge (typically $10-15/year)
- Workers/Pages deployment is usage-based; free tier covers most test apps

## Testing Without Spending Money

1. Run `stripe projects catalog` to see available services — no charge
2. Provision a Workers account without a domain — free
3. Deploy to a `*.workers.dev` subdomain — free, no domain purchase needed

## Startup Credits

Incorporating via **Stripe Atlas**? You get $100,000 in Cloudflare credits automatically as part of the Cloudflare/Stripe partnership (April 2026 launch).

## Files in This Skill

| File | Audience | Purpose |
|---|---|---|
| SKILL.md | Agent | Injected skill prompt with full procedure |
| README.md | Agent + Human | Navigation and quick reference |
| REFERENCE.md | Agent + Human | Protocol internals, CLI commands, cost control |
| SUMMARY.md | Human | One-paragraph orientation |
| human.md | Human | This file |

## Extending to Other Providers

The Stripe Projects protocol is provider-agnostic. If another provider (e.g., PlanetScale, Vercel) adds catalog support, the same flow works:

```bash
stripe projects add planetscale/postgres:database
stripe projects add vercel/hosting:deploy
```

Check `stripe projects catalog` for the current full list.
