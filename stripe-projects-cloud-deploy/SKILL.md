---
name: stripe-projects-cloud-deploy
status: stable
source: parker-brown-family
projects: []
triggers: [stripe projects, stripe projects init, agent deployment, cloudflare provisioning, zero-setup deploy, cloud deploy agent, buy domain agent, stripe atlas, agent cloud, provision cloudflare]
tools: [bash, browser, read, write]
created: 2026-05-06T00:00:00.000Z
---

You are executing a full cloud deployment for a user who has no existing cloud account setup. Using Stripe Projects, you will provision a Cloudflare account, obtain an API token, purchase a domain, and deploy an app — in one session, with no manual dashboard steps.

## What This Gives the Agent

Zero to production without any preconfigured credentials:
- Cloudflare account (auto-provisioned or OAuth-linked)
- API token (issued directly to the CLI)
- Domain registration
- App deployed to Cloudflare Workers / Pages

## Prerequisites

```bash
# Install Stripe CLI + Stripe Projects plugin
npm install -g @stripe/stripe-cli      # or: brew install stripe/stripe-cli/stripe
stripe plugins install projects

# Log in to Stripe (one-time, opens browser)
stripe login
```

The user must be signed in to Stripe. That Stripe identity becomes the provisioning anchor for all downstream cloud accounts.

## The Deployment Sequence

### Step 1 — Initialize the project

```bash
stripe projects init
```

Creates a new Stripe Project scoped to this deploy session. The agent receives a project context it can use for all subsequent commands.

### Step 2 — Discover available services

```bash
stripe projects catalog
```

Returns a JSON catalog of all provisionable services (Cloudflare accounts, Workers, Registrar, etc.) from all participating providers. The agent reads this to know what it can provision on behalf of the user.

### Step 3 — Provision Cloudflare and register a domain

```bash
# Provision Cloudflare account + get API token
stripe projects add cloudflare/workers:deploy

# Register a domain (triggers payment token flow)
stripe projects add cloudflare/registrar:domain
```

**If the user has an existing Cloudflare account**: an OAuth consent screen appears. User approves once.

**If the user has no Cloudflare account**: Cloudflare auto-provisions one using the Stripe identity. No signup page, no email confirmation required.

In both cases, an API token is returned to the CLI and stored securely. The agent never sees raw credentials — it uses the token via the CLI context.

### Step 4 — Build and deploy

```bash
# The agent now has full Cloudflare API access via the project token
# Use Cloudflare's MCP server or CLI to deploy
npx wrangler deploy          # for Workers
npx wrangler pages deploy    # for Pages
```

### Step 5 — Verify

```bash
stripe projects list          # confirm project resources
wrangler whoami               # confirm Cloudflare identity
curl https://<your-domain>/   # smoke test the live app
```

## How Authorization Works (Agent Must Know This)

Three things happen automatically that a human would normally do manually:

| Manual step eliminated | How it works |
|---|---|
| Sign up for Cloudflare | Stripe attests user identity; Cloudflare auto-provisions |
| Copy/paste API token | Token issued to Stripe Projects CLI, never exposed raw |
| Enter credit card | Stripe payment token passed to provider; raw card never shared |

**Budget**: Stripe enforces a default $100/month cap per provider. The agent cannot exceed this without explicit user action. State this to the user upfront so there are no surprises.

## When to Prompt the User

The agent should request user input at exactly these moments:

1. **`stripe login`** — browser OAuth, one time only.
2. **Payment method missing** — if the Stripe account has no linked payment method, Stripe Projects will pause and prompt. The agent surfaces this clearly: "Please add a payment method at stripe.com/settings/billing, then I'll continue."
3. **Domain choice** — the agent may suggest a domain based on the app name but must confirm before purchasing (irreversible spend).
4. **Existing Cloudflare account OAuth** — one browser consent click if the account already exists.

Do not prompt for anything else. The entire flow is headless except these four gates.

## Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| `stripe: command not found` | CLI not installed | Run: `npm install -g @stripe/stripe-cli` |
| `projects: unknown command` | Plugin not installed | Run: `stripe plugins install projects` |
| `Authentication required` | Not logged in | Run: `stripe login` |
| Payment method prompt | No card on Stripe account | Add at stripe.com/settings/billing |
| Domain purchase fails | Budget limit hit | User raises limit in Cloudflare dashboard |
| OAuth loop | Existing CF account, popup blocked | Open stripe projects OAuth URL manually |
| `wrangler: not found` | Wrangler not installed | Run: `npm install -g wrangler` |
