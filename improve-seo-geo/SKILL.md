---
name: improve-seo-geo
description: Improve SEO and generative-engine/AI-agent discoverability for public websites by inspecting existing metadata, sitemap, robots, structured data, content, internal links, and agent-readable files; use when the user invokes /improve-seo-geo, asks for SEO/GEO/AI search optimization, llms.txt, structured data, or discoverability improvements, and hard-stop if the repository is not a public website or web-rendered content surface.
status: stable
source: parker-brown-family
projects: []
triggers: [improve-seo-geo, /improve-seo-geo, seo geo, generative engine optimization, ai search optimization, llms.txt, search metadata, structured data]
tools: [bash, read, write, browser]
created: 2026-06-07T00:00:00.000Z
---

You are running an SEO/GEO improvement pass for a public website. Your job is to make the codebase more discoverable to search engines and AI agents, while giving the non-technical owner clear off-site business steps to take after deploy.

GEO here means agent and generative-search discoverability. Do not invent ranking guarantees. Make the human page better first, then add accurate machine-readable signals that mirror visible content.

## Hard Stop: Confirm This Is A Website

Before editing, determine whether the repository contains a public website, web app, docs site, marketing site, ecommerce storefront, local-business site, or static site.

Look for clear evidence:
- Web framework files: `app/`, `pages/`, `src/routes/`, `astro.config.*`, `next.config.*`, `nuxt.config.*`, `svelte.config.*`, `gatsby-config.*`, `vite.config.*`
- Public web assets: `public/`, `static/`, `assets/`, `index.html`, templates, route files
- SEO surfaces: `robots.*`, `sitemap.*`, metadata exports, head components, JSON-LD, OpenGraph/Twitter tags
- Content models: articles, posts, docs, product pages, services, locations, CMS data
- Build scripts for web output: `next build`, `astro build`, `vite build`, `nuxt build`, static-site generators

If this evidence is absent, stop immediately. Do not create SEO files in a non-website repo. Report:

```text
Blocked: /improve-seo-geo only applies to repositories with a public website or web-rendered content surface. I do not see routes, HTML/templates, public assets, metadata, sitemap/robots, or a web build pipeline here.

Next step: point me at the website repo, docs repo, CMS export, or deployed site source.
```

If there is a website but the target page/business goal is unclear, inspect the site structure and pick the most relevant public page. Ask only if multiple targets are equally plausible and the wrong choice would create bad public metadata.

## Working Rules

- Preserve existing patterns. Use the site's framework APIs, components, content model, sitemap generator, and schema helpers before adding new abstractions.
- Keep changes scoped. Check `git status` first and do not revert unrelated work.
- Treat visible content as the source of truth. Structured data, `llms.txt`, JSON manifests, and metadata must not claim facts that are not visible or supported on the site.
- Do not keyword-stuff, hide text, fabricate reviews, invent credentials, or add fake locations/services.
- Do not add a public MCP server for SEO/GEO. Normal crawlers and agents use pages, links, sitemaps, structured data, and public static/route files. MCP is only appropriate if the product already exposes a tool/API surface and the user explicitly asks for it.
- For medical, legal, financial, health, or high-stakes content, preserve disclaimers and avoid making individualized advice claims.
- If current official platform guidance matters, check primary sources such as Google Search Central, Schema.org, platform docs, or the framework docs.

## One-Click Workflow

Run the full pass without waiting for user decisions unless a hard stop or genuinely ambiguous target appears.

### 1. Baseline The Site

Inspect:
- routes/pages and the target page
- layout/head metadata
- article/product/service/location content models
- sitemap and robots generation
- OpenGraph/Twitter images
- existing JSON-LD/schema components
- internal navigation and relevant service/category pages
- public static files such as `llms.txt`, `.well-known`, or `ai/`
- analytics/Search Console/verification placeholders, if present

Write down the current pattern in your own working notes before editing. The implementation should look native to the repo.

### 2. Choose The SEO/GEO Target

Classify the primary target:

| Target | Likely schema | Priority signals |
|---|---|---|
| Article/guide/blog | `Article`, `BlogPosting`, sometimes `FAQPage` | canonical URL, author, date, headline, sources, internal links |
| Recipe/how-to | `Recipe`, `HowTo`, `Article` | ingredients/steps only if visible, yield, images, safety notes |
| Local service business | `LocalBusiness`, `MedicalBusiness`, `Service` | name/address/phone, service area, booking URL, Business Profile consistency |
| Ecommerce/product | `Product`, `Offer`, `AggregateRating` only when real | product facts, price/availability if visible, canonical variants |
| SaaS/product docs | `SoftwareApplication`, `TechArticle`, docs metadata | docs index, changelog/date, canonical concepts |
| Venue/person/portfolio | `Organization`, `Person`, `Event`, `CreativeWork` | entity clarity, social profiles, canonical bio/location |

If no work has been done yet, start with crawlability, canonical metadata, sitemap/robots, and one useful structured-data graph for the most important page.

### 3. Improve The Human Page First

Make small, visible improvements when needed:
- sharpen title/H1 alignment without making every title identical
- add one or two natural phrases people would actually search for
- make the target audience explicit in body copy or teaser text
- add internal links from relevant service/category pages
- ensure author/date/source information is visible for editorial content
- add alt text or a better social image only when the repo already supports it
- preserve copy-friendly controls if the site uses them for AI or sharing

Avoid large rewrites unless the user asked for content strategy or the page is too thin to support the metadata.

### 4. Add Or Update Page Metadata

Use the framework's existing metadata path:
- `title`
- `description`
- canonical URL
- OpenGraph URL/title/description/type/image
- Twitter/X card metadata
- author/publisher/date for articles
- category/tags/keywords only if the framework already uses or accepts them

Descriptions should be accurate, specific, and written for humans. Do not dump keyword lists into visible copy.

### 5. Add Accurate Structured Data

Add JSON-LD using the site's existing schema helper or head/script pattern.

Good structured data:
- matches visible text on the page
- uses stable canonical `@id` URLs
- connects `Person`, `Organization`, `Article`, `Recipe`, `Service`, or `Product` nodes where appropriate
- includes dates, author, publisher, images, and `mainEntityOfPage` for articles
- includes ingredients, instructions, yield, and nutrition only for recipes where those facts are visible

Bad structured data:
- review/rating markup without visible real reviews
- FAQ markup for questions not visible on the page
- service areas, prices, credentials, or medical claims that the page does not state
- schema added only to game rich results

If a strict CSP nonce is present, follow the site's existing nonce/script pattern so JSON-LD does not break the page.

### 6. Improve Crawl Paths

Check and update where native:
- sitemap entries for new or important URLs
- `lastModified`, `changeFrequency`, and reasonable priorities
- `robots.txt` sitemap declaration, usually `Sitemap: <canonical-site-origin>/sitemap.xml`
- canonical URL consistency
- internal links from relevant pages
- no accidental `noindex`, blocked static assets, or broken route conventions

Do not make every page high priority. Give the primary target a modest bump relative to ordinary evergreen pages.

When possible, fetch the live or local `/robots.txt` and confirm it exposes the canonical sitemap URL. Add the directive through the site's existing robots generator or static file if it is missing.

### 7. Add Agent-Readable Metadata When Helpful

If the site can serve public static files or simple public routes, consider adding:
- `/llms.txt`: concise Markdown index of priority pages and canonical URLs
- `/ai/<topic>.json`: structured facts for agents when one topic/page is strategically important
- `rel="alternate"` links to the public JSON/text metadata if the framework supports them

Use these files as navigation aids, not hidden content. They should:
- identify the site/entity
- list canonical URLs
- summarize the target page
- include target audience and supported facts
- point agents back to visible page content as source of truth
- mention copy-friendly page controls when they exist
- include safety/disclaimer context for high-stakes topics

Do not add `llms.txt` if the site cannot serve it publicly, if it would duplicate private/internal data, or if the user explicitly does not want AI crawler affordances.

### 8. Prepare The Owner Launch Plan

After code changes, give the owner an exact sequence they can execute without engineering help:
- deploy the current branch or PR
- verify the live priority page, `/sitemap.xml`, and `/robots.txt`
- submit the sitemap in Google Search Console
- use URL Inspection and request indexing for the priority page plus important linked pages
- run Google's Rich Results Test on the priority page
- publish a Google Business Profile update when local-business relevant
- share the canonical URL through social, newsletter, and relevant partner/profile links
- start the next supporting article or page in the content cluster

For local businesses, include a NAP consistency reminder using only facts visible in the repo or provided by the user: business name, address, phone, service area, booking URL, and profile links. If any value is missing or uncertain, mark it as owner-confirm-needed instead of inventing it.

For Google Business Profile posts, draft copy only when the site has local-business context. Keep it short, professional, and action-oriented. Include:
- post type suggestion, usually Update
- post copy
- CTA label, usually Learn more or Book
- canonical URL to attach
- reminder that Google reviews posts and may reject policy-sensitive wording

For the content cluster, suggest 4-6 supporting page/article ideas based on the target page and existing site navigation. Each supporting idea should link back to the pillar page and one relevant service/category/contact page.

## Verification

Run the fastest reasonable checks for the stack:
- build or typecheck (`npm run build`, `pnpm build`, `yarn build`, `astro check`, etc.)
- JSON parse for any added public JSON files
- render/curl the target page locally when a dev server is available
- confirm `application/ld+json` appears and parses
- confirm `/llms.txt` and `/ai/*.json` resolve when added
- confirm `/robots.txt` includes the canonical `Sitemap:` directive
- confirm the priority URL is indexable: no `noindex`, no robots block, no login requirement
- confirm internal links are visible in rendered HTML
- confirm visible author/date/source or business/location facts match metadata and schema
- inspect the focused git diff

If browser screenshots are useful, use them for visual regressions but do not block a metadata-only pass on screenshots.

## Final Owner Handoff

End with three compact sections:

1. **Code changes made**
   - files touched
   - metadata/schema/crawl/agent-readable additions
   - whether `robots.txt` already had, or was updated with, the sitemap directive
   - verification run and result

2. **Business steps after deploy**
   - verify or update Google Search Console
   - submit `sitemap.xml`
   - use URL Inspection and request indexing for priority URLs
   - run Google's Rich Results Test on the priority page
   - update Google Business Profile when local-business relevant: services, description, photos, and a post linking the new page
   - share the canonical URL from relevant social profiles, newsletters, directories, or partner pages
   - next 4-6 supporting content ideas, each with the pillar page it should link to

3. **Caveats**
   - no ranking guarantees
   - `llms.txt`/AI JSON are agent affordances, not official Google ranking requirements
   - any placeholders still requiring owner action, such as Search Console verification tokens or Business Profile edits

## Output Tone

Be direct and owner-friendly. A lay person should understand what changed, what to do next, and what not to worry about. Do not bury the business instructions under implementation detail.
