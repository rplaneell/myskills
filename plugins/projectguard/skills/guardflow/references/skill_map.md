# Skill map

| Skill | Use it to | Needs | Produces | Records in the ledger |
|---|---|---|---|---|
| projectguard | learn the method, the order, the traps | nothing | the plan shape | n/a |
| guardflow | run a multi step request | the request | protocol, ledger, hand over | the whole thread |
| secretguard | keep keys out of Git | repository | ignore rules, scanner, blocker, CI scan | history scan, blocker, CI scan |
| cihardening | harden automation | workflows | pinned actions, permissions, Dependabot | pins, permissions, rebuild check |
| repocontrols | protect a free private repository | repository, plan | rules, rules job, push blocker | rules job, push blocker |
| depaudit | find known flaws in dependencies | lock files | audits, weekly workflow, vendored list and test | each audit, vendored check |
| codescan | scan code for risky patterns | code or built page | rules, fixtures, guards | scan, blindness guards |
| backtest | freeze results | scenarios, an oracle if any | golden files, oracle comparison | backtests |
| propertytests | rules true for every result | saved results | property tests, cross view tests | property tests |
| hostileinput | prove text stays text | list of entry points | hostile tests, detector | hostile grid, break tests |
| uitests | click everything | built page | clicking tests, helpers | areas covered |
| coveragegate | know what tests run | tests | floor in CI | coverage and floor |
| mutationcheck | would tests notice a bug | tests | survivors, new tests | breakages |
| releaseintegrity | prove what was shipped | releases | manifest, rebuild check | fingerprints, findings |
| porting | bring an old build into sources | shipped file, sources | inventory, plan, steps | each step |
| securityaudit | sort the standard checklist | architecture | applies, not applicable, later | checklist rows |
| securityreport | show it visually | ledger, tables | page, PDF | n/a (reads the ledger) |
| ownersteps | what only the owner can do | project | checker, steps | owner reported items |

## Dependencies in one picture

```
guardflow ─ recon ─ releaseintegrity, secretguard, depaudit, codescan, securityaudit
          ─ setup ─ secretguard → cihardening → repocontrols → depaudit → ownersteps
          ─ tests ─ backtest → propertytests → hostileinput → uitests → coveragegate → mutationcheck
          ─ old file ─ releaseintegrity → porting (with backtest as oracle)
          ─ end ─ ledger → securityreport → ownersteps
```

## Naming and evidence rules shared by every skill

* Outcome: clean, fixed, open, partial. Proof: ran, github, both. Gaps are separate.
* A check is proven only after it was seen to fail on purpose.
* Every skill ends with honest limits; copy them into the ledger.
