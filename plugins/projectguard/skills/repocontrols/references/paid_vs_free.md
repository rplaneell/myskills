# Which protections are paid on a private free plan, and what replaces them

Written from our understanding of GitHub's plans at the time. Plans change. Ask the owner to confirm on their own Settings pages
(Settings, Code security; Settings, Branches) before relying on this table.

| Protection | Paid for private repos? | Free replacement | What the replacement does NOT do |
|---|---|---|---|
| Secret scanning (GitHub finds keys in the repository) | yes (free on public repositories) | gitleaks in CI over the whole history | notices after the push; does not block |
| Push protection (GitHub refuses the push containing a key) | yes (free on public repositories) | gitleaks as a local pre commit hook | only on computers with the hook; `--no-verify` skips it |
| Branch protection / rulesets (refuse merge unless checks pass, require review) | yes for private repositories | CONTRIBUTING rules, the repo rules CI job, a local push blocker | cannot stop a push to main; no required review |
| CodeQL / code scanning alerts | yes for private repositories | Semgrep command line with your own rules in CI | narrower rule coverage; report only until reviewed |
| Required status checks before merge | yes (part of branch protection) | the rule "merge only when green" plus the checks | relies on the owner's discipline |
| Dependabot version updates and alerts | free | n/a | alerts must be switched on by the owner |
| GitHub Actions minutes | limited free allowance for private repos | keep slow jobs few; separate small fast workflows | a long test job costs minutes on every push |

## Principle

For every paid protection you cannot have, write down: what it would have done, what you use instead, and the gap that remains.
Put that table in the project's plan document so the owner never believes they have a protection they do not.

## When the situation changes

* Repository becomes public: switch on secret scanning, push protection, and code scanning; keep the CI and local layers.
* Paid plan: add branch protection or a ruleset requiring the CI checks and a pull request; keep the rules job (it checks things protection does not, like commit message shape).
* Several contributors: add CODEOWNERS and required reviews.
