# stripe-projects-cloud-deploy — Summary

**What**: Zero-to-production cloud deployment via Stripe Projects + Cloudflare. An agent provisions a Cloudflare account, gets an API token, buys a domain, and deploys an app — in one session, no dashboard, no manual credential copying.

**Why**: Agents need accounts, payment, and tokens to deploy. Stripe Projects eliminates all three manual gates by using Stripe as the identity/payment anchor and Cloudflare's provisioning API for automatic account creation.

**The sequence**:
```bash
stripe projects init
stripe projects catalog
stripe projects add cloudflare/workers:deploy
stripe projects add cloudflare/registrar:domain
wrangler deploy
```

**For agents**: Only four moments require user input — initial Stripe login, missing payment method, domain name confirmation, and (for existing CF accounts) one OAuth click. Everything else is headless.

**Budget safety**: Stripe caps agent spend at $100/month per provider by default. Raw card numbers are never passed to the agent or to Cloudflare.

**Reference**: REFERENCE.md for the three-component protocol (discovery/authorization/payment), CLI command table, and platform integration guide.
