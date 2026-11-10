# The browser rules, what they find, and how to write more

| Rule id | Severity | Looks for | Why it matters |
|---|---|---|---|
| pg_html_injection_sink | WARNING | `innerHTML` or `outerHTML` assigned a non literal, `insertAdjacentHTML`, `document.write` | hostile text in a name could become page elements (XSS, cross site scripting) |
| pg_dynamic_code | ERROR | `eval`, `new Function`, `setTimeout` with a string | text turned into running code |
| pg_network_api | ERROR | `fetch`, `XMLHttpRequest`, `WebSocket`, `EventSource`, `sendBeacon`, `importScripts`, `Worker` | an offline tool must never contact a server |
| pg_storage_or_cookie | WARNING | `document.cookie`, `localStorage`, `sessionStorage`, `indexedDB` | data kept in the browser |
| pg_navigation_or_window | WARNING | `window.open`, assigning `location.href`, `location.assign`, `location.replace` | page controlled by a value |
| pg_cross_window_message | WARNING | `postMessage`, `addEventListener("message")` | origin checks needed |

## Writing a rule

```yaml
rules:
  - id: pg_my_rule
    languages: [javascript]        # or python, java, go ...
    severity: WARNING              # ERROR makes --block-errors fail
    message: Plain language: what is risky and what to do instead.
    pattern-either:
      - pattern: dangerousCall(...)
      - pattern: $X.dangerousProperty = $Y
    pattern-not: $X.dangerousProperty = "..."      # a plain literal is fine
```

Then ADD a line to the fixture that triggers it. The self test fails if the fixture does not trigger every rule, so a rule you forgot to test cannot sit there silently.

## Traps

* Semgrep matches syntax, not meaning. A rule for `x` attributes fires on legitimate SVG `x` attributes. Use unmistakable names in detectors.
* Keep the target folder out of `build/` and `tests/`, and outside `.gitignore`d paths (the script passes `--no-git-ignore`).
* Parse errors mean files were skipped. The script treats any parse error as a failure.
* Pin the Semgrep version in CI so a new release cannot change results unnoticed.
