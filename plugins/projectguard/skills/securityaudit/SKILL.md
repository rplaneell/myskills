---
name: securityaudit
description: A plain language website and application security checklist that sorts each item into applies now, not applicable now, or applies once a server exists. Items are hiding API keys, environment variables, Git history for keys, admin routes, authentication, user permissions, input sanitizing, XSS, SQL injection, database rules, rate limiting, spend caps, file uploads, CSRF, CORS, HTTPS, security headers, secure cookies, disabling debug mode and production settings. Use when the user asks for a security review, a pre launch checklist, or to know what security a static page or an app really needs.
---

# securityaudit: what actually applies to this project?

Security lists are often copied without asking whether they fit. A static offline page has no server, no database and no login, so many items cannot apply. Marking an item "not applicable" with a reason is a correct and useful answer, and it prevents fake work. The same list becomes real work the day a backend appears.

## How to use

1. **Describe the architecture in three lines:** where code runs (only in the browser, or on a server), where data lives (nowhere, files, a database), who can log in (nobody, users, admins).
2. **Go through `references/checklist.md` item by item.** For each: applies now, not applicable now, or later (when X exists), with the reason and what covers it today. Be specific, name files and tests.
3. **Verify claims instead of trusting them.** "No server" means: check the code for network calls (`codescan` rule for fetch, XMLHttpRequest and similar finds none), check the Content Security Policy forbids network access, check no cookies or storage are used.
4. **Produce a table** the owner can keep in the project's plan document, and a short list of gaps in order of importance.
5. **Say what only the owner can do** (GitHub settings, provider consoles, DNS).

## Typical outcome for a static, offline page

Applies now: secrets and the Git history, input sanitizing and XSS (names and files that are shown), file handling (size limits, malformed files), a restrictive Content Security Policy, dependency and supply chain safety, debug output and leftover test code. Not applicable now: authentication, admin routes, permissions, SQL injection, database rules, rate limiting, spend cap, CSRF, CORS, cookies, HTTPS configuration (unless hosted, then HTTPS is usually default on the host). Later: all of the second group the day a backend, login or database is added.

## The day a backend appears

Do not wait. As soon as the project grows a server: add authentication and authorization checks on every route (never trust the client), validate and parameterize every query (no string built SQL), set database access rules to deny by default, add rate limiting and a spend cap on paid services, restrict CORS to known origins, protect forms with CSRF tokens or same site cookies, mark cookies `HttpOnly`, `Secure` and `SameSite`, force HTTPS, add security headers, turn debug mode off, and review the production configuration. Write tests for each (an unauthenticated request to a protected route must be refused; a hostile string in a field must not change a query).

## Honest limits

A checklist is not a penetration test. It shows you considered each risk and what covers it; it does not prove nothing is missing. For anything handling other people's data or money, get an independent review.

See `references/checklist.md` for the table and the questions to ask.
