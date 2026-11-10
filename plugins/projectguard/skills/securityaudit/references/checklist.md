# Security checklist (static page versus server)

Columns: **Static** is a page that runs only in the browser with no server. **Server** is once there is a backend, login or database.
Status words: applies, not applicable, later.

| # | Item | What it means | Static page | Server | How to check or cover it |
|---|---|---|---|---|---|
| 1 | Hide API keys | secrets never in code or chat | applies (guard against future keys) | applies | `secretguard`: .env rules, history scan, commit blocker, CI scan |
| 2 | Check environment variables | configuration read from the environment, not the code | applies | applies | `.env.example` lists names only; no real values in the repository |
| 3 | Check the Git history for keys | an old commit may hold a key | applies | applies | gitleaks over all history; revoke any key found |
| 4 | Protect admin routes | admin pages not reachable by everyone | not applicable | applies | tests: unauthenticated request refused |
| 5 | Add authentication | prove who the user is | not applicable | applies | use a proven library or service, never invent your own |
| 6 | Check user permissions | what each user may do | not applicable | applies | check on the server for every action; deny by default |
| 7 | Sanitize user input | treat all input as hostile | applies (names, files) | applies | validate type, size and format; `hostileinput` tests |
| 8 | Protect against XSS | hostile text running as code | applies | applies | escape at insertion, `textContent`, CSP; `hostileinput`, `codescan` |
| 9 | Protect against SQL injection | hostile text changing a database query | not applicable | applies | parameterized queries only; test with hostile strings |
| 10 | Check database rules | who can read and write which data | not applicable | applies | deny by default; row level rules; test with a second user |
| 11 | Add rate limiting | stop floods and guessing | not applicable | applies | per user and per address limits on login and expensive routes |
| 12 | Set a spend cap | limit paid service costs | not applicable (no paid services) | applies | budget alerts and hard caps at the provider |
| 13 | Secure file uploads | uploaded files can be hostile | applies for files read locally | applies | size limit, type check by content, never execute, store outside web root |
| 14 | Add CSRF protection | another site tricking a logged in browser | not applicable (CSP `form-action 'none'` helps) | applies | tokens or `SameSite` cookies |
| 15 | Check CORS settings | which other sites may call the API | not applicable (`connect-src 'none'`) | applies | allow named origins only, never `*` with credentials |
| 16 | Enable HTTPS | encrypted traffic | host default if hosted; file offline | applies | redirect to HTTPS, HSTS header |
| 17 | Add security headers | browser hardening rules | the CSP lives in a meta tag | applies | CSP, HSTS, `X-Content-Type-Options`, frame rules; test the meta tag has not loosened |
| 18 | Secure cookies | cookie flags | not applicable (no cookies; `codescan` confirms) | applies | `HttpOnly`, `Secure`, `SameSite` |
| 19 | Disable debug mode | no debug pages or verbose errors in production | applies in spirit (no debug output, no test code shipped) | applies | grep the built file for debug flags and console logging of data |
| 20 | Check production settings | the deployed configuration is the safe one | applies (what is shipped, with which CSP) | applies | `releaseintegrity`: the shipped file is the tested file |

## Questions that settle most items

* Does any code in the shipped file contact a server? (scanner rule plus CSP)
* Does it store anything in the browser (cookies, storage)?
* Where does each displayed text come from, and is it escaped?
* Who can read or change data, and where is that enforced?
* What happens if a stranger sends the strangest possible input?

## Record

Keep the filled table in the project's plan document with the date and a one line reason per row. Review it whenever the architecture changes.
