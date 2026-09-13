# Consent banner: deferred, geofenced rollout plan

Status: deferred. Revisit when the trigger condition below is met.

## Current state

`analytics_storage` defaults to `'granted'` site-wide (Consent Mode, see the
"Consent defaults" script on every page and `templates/article.html`).
`ad_storage`, `ad_user_data`, and `ad_personalization` stay `'denied'`. The
legal basis for analytics stated in `/privacy/` is legitimate interest, with
an opt-out via Google's browser add-on or blocking cookies.

This is a reversion of a 2026-09-10 change (PR #122) that flipped
`analytics_storage` to `'denied'` by default without ever shipping a
consent-collection UI to grant it — GA4 traffic went to ~zero as a result,
since nothing ever called `gtag('consent', 'update', ...)`. See the commit
that restored `'granted'` for the incident detail.

## Why this isn't fully compliant, and why we're deferring anyway

The EU ePrivacy Directive (and the UK's equivalent, PECR) require opt-in
consent before setting non-essential cookies, including GA-style analytics
cookies, regardless of GDPR legal basis. "Legitimate interest, granted by
default with an opt-out" is a valid GDPR legal basis but does not satisfy
that opt-in cookie requirement. Since `/privacy/` names the Estonian Data
Protection Inspectorate (Andmekaitse Inspektsioon) as our supervisory
authority, this exposure is concrete, not hypothetical.

GA4 country breakdown checked 2026-09-13 (5 Apr–11 Sept window, 2,655 active
users): Germany 88 + United Kingdom 82 = 170 users, ~6.4% of total, with a
long tail of other EU countries likely pushing the true EEA+UK share to
somewhere around 8–10%. The large majority of traffic (US, Singapore, China,
India, Colombia, Canada, Brazil, ...) isn't subject to this requirement.
Given that, full opt-in-by-default site-wide isn't worth reintroducing the
zero-collection risk again — but geofencing it to the affected ~1-in-10
visitors is cheap enough to be worth doing once traffic justifies the work.

## Trigger to pick this back up

Revisit when either:
- The Germany + UK + rest-of-EEA share of GA4 active users grows
  meaningfully past its current ~8–10%, or
- Any paid/organic marketing push specifically targets the EU, where
  regulatory attention on the site is more likely.

Check via GA4 → Reports → User attributes overview → Active users by
Country (EEA members + United Kingdom).

## Planned approach: edge geofencing, not a site-wide banner

The site sits behind Cloudflare (see `/privacy/`'s infrastructure table),
which stamps every request with a `CF-IPCountry` header at no extra cost —
no third-party geo-IP lookup needed, and it's based on the request's actual
IP rather than a spoofable client-side signal.

1. Add a Cloudflare Worker (or Transform Rule) that reads `CF-IPCountry` on
   each request.
2. For EEA member states + `GB`, rewrite the response so the "Consent
   defaults" script sets `analytics_storage: 'denied'` instead of
   `'granted'`, and inject the consent banner (see below). Every other
   country code passes through unchanged, still defaulting to `'granted'`.
3. Keep the EEA/UK country list in the Worker script, not scattered across
   the 298 static pages — this is exactly why it belongs at the edge rather
   than as two maintained versions of every page.

This avoids reintroducing the all-traffic collection outage: only the
geofenced ~10% ever sees `'denied'` by default, and only that slice needs the
banner to grant it.

## Existing draft to build on

`site/_snippets/consent-head.js` and `site/_snippets/consent-banner.html`
are an unwired first draft of the banner UI and the
`gtag('consent', 'update', ...)` wiring (accept/reject buttons, persisted
choice via `localStorage`, re-applied on return visits). Neither file is
referenced by `scripts/sync_shared.py` yet. When this is picked back up:

- Wire `consent-head.js` into `<head>` (after the consent-defaults script,
  before GTM loads) and `consent-banner.html` before `</body>`, but **only**
  for requests the Worker has marked as geofenced — not site-wide.
- Update `/privacy/`'s "Cookies and changing your choices" section and the
  legal-basis table back to describing consent-gated analytics for the
  geofenced visitors specifically.
