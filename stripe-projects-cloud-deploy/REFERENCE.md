# stripe-projects-cloud-deploy — Reference

## Source

Cloudflare blog: https://blog.cloudflare.com/agents-stripe-projects/

## The Three-Component Protocol

Stripe Projects implements a standard that composes three existing mechanisms:

### 1. Discovery

```bash
stripe projects catalog
```

Returns a JSON array of available services from all participating providers. Each entry describes a provisionable resource, its provider, capabilities, and pricing tier. The agent reads this to understand what it can spin up without asking the user.

Cloudflare exposes its catalog via a simple REST endpoint returning JSON — no proprietary SDK required. Any platform can query it.

### 2. Authorization (identity + account provisioning)

**Flow for new users (no Cloudflare account):**
1. User signs into Stripe → Stripe holds the verified identity
2. Agent calls `stripe projects add cloudflare/...`
3. Stripe sends an OIDC identity attestation to Cloudflare
4. Cloudflare auto-provisions an account for that identity
5. Cloudflare issues an API token → returned to Stripe Projects CLI → stored securely
6. Agent uses token for all subsequent Cloudflare API calls

**Flow for existing users:**
1. Standard OAuth consent screen (one click)
2. Access granted to the Stripe Projects CLI
3. API token issued as above

Raw credentials are never exposed to the agent. The token is held by the CLI context.

### 3. Payment

- Stripe passes a **payment token** (not raw card data) with each provision request
- The provider (Cloudflare) bills against this token
- Default cap: **$100 USD/month per provider**
- Cap is enforced by Stripe, not by the agent
- User raises the cap via Budget Alerts in the Cloudflare dashboard

### Standards Used

| Component | Standard |
|---|---|
| Identity attestation | OIDC |
| Access delegation | OAuth 2.0 |
| Payment | Stripe payment tokenization |
| Service catalog | REST/JSON (provider-defined schema) |

## Stripe CLI Commands

| Command | What it does |
|---|---|
| `stripe login` | Authenticate to Stripe (browser OAuth, one-time) |
| `stripe projects init` | Create a new Stripe Project session |
| `stripe projects catalog` | List all provisionable services |
| `stripe projects add <service>` | Provision a specific service |
| `stripe projects list` | Show all resources in the current project |

## Cloudflare Service Identifiers

| Identifier | Resource provisioned |
|---|---|
| `cloudflare/workers:deploy` | Workers deployment + API token |
| `cloudflare/registrar:domain` | Domain registration |
| `cloudflare/pages:deploy` | Pages deployment |

Check `stripe projects catalog` for the current full list — it grows as Cloudflare adds products.

## Wrangler (Cloudflare CLI)

Once the API token is issued, the agent uses Wrangler for all deployment operations:

```bash
npm install -g wrangler

wrangler whoami           # confirm identity
wrangler deploy           # deploy Workers app
wrangler pages deploy     # deploy Pages site
wrangler domains list     # list registered domains
```

The Stripe Projects CLI sets the token in the environment or config automatically. No manual `wrangler login` needed if coming through the Stripe Projects flow.

## Platform Integration (Building Your Own Orchestrator)

Any platform with signed-in users can play the Stripe role:

1. Your platform holds the user identity
2. When the user needs a cloud resource, call Cloudflare's provision API with an OIDC attestation
3. Cloudflare returns an API token scoped to the new or linked account
4. Pass a payment token from your billing provider for charge authorization

Contact: agent-partnerships@cloudflare.com (per blog)

## Cost Control

| Control point | Where |
|---|---|
| Default spend cap ($100/mo per provider) | Stripe Projects (automatic) |
| Raise cap | Cloudflare dashboard > Budget Alerts |
| View charges | Stripe dashboard > Projects |
| Cancel subscriptions | Cloudflare dashboard > Subscriptions |

## $100K Cloudflare Credits for Startups

New startups incorporating via **Stripe Atlas** receive $100,000 in Cloudflare credits automatically as part of this partnership launch (as of April 2026).

## Related Tools

- Cloudflare Code Mode MCP server — provides the agent with richer Cloudflare context during development
- Cloudflare Agent Skills (official) — additional skills provided by Cloudflare for common deployment patterns
- PlanetScale Postgres integration — Cloudflare as Orchestrator for database provisioning (same protocol)
