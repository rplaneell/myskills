---
name: projectguard
description: Start here. A complete, proven method to make any software project traceable, backtested and secure, with the order to adopt it, the working agreements, and a map to the specialized skills (secretguard, cihardening, repocontrols, codescan, backtest, propertytests, hostileinput, uitests, coveragegate, mutationcheck, releaseintegrity, securityaudit). Use when the user asks to make a project robust, secure, professional, traceable or well tested, to set up CI (continuous integration) and tests, to harden a repository, or to audit what protection a project has.
---

# projectguard: make a project traceable, backtested and secure

This is the overview. It explains the method, the order to follow, and how to behave while doing it. The specialized skills hold the details and the ready to use scripts. Every script in these skills was used on a real project and tested, and each skill says honestly what it protects and what it does not.

## The idea in one paragraph

Professional engineering is not writing code fast, it is being able to release code reliably and recover from disasters. That needs automatic checks that run on every change (CI, continuous integration), tests at several levels, protection against leaked secrets and hostile input, and a record that lets you prove which code produced which result. The cheapest way to get there is a pipeline of small, independent safety layers, each of which has been shown to fail when it should.

## The golden rule: a check that has never failed is unproven

Almost every serious mistake we made came from trusting a check that was quietly doing nothing: a scanner that scanned zero files and said "all clear", a test that clicked a button that was off screen, a comparison that passed because both sides were empty. So for every check you add, do two things: make it pass on good code, then break the code on purpose (in a scratch copy) and watch it fail. If you cannot make it fail, it is not protecting anything. Read `references/lessons.md` for the full list of traps.

## Working agreements (how to behave)

1. **Ask first, then act** when the owner asks for it: say what you plan to do, wait for a yes before each change that touches the repository, a setting, or anything outside your own scratch area. Read only exploration needs no permission.
2. **Explain in plain language.** Say why each thing matters, explain every abbreviation the first time, avoid jargon, and give context. Use friendly, human wording. If the owner says never to use hyphens or dashes in prose, obey it everywhere in prose (commands, file names and tool names are not prose).
3. **Report honestly.** Separate what you ran and saw from what you only expect to work. Say what a check cannot protect. Never claim a result you did not see. If a tool was disconnected and you could not read the CI result, say so and tell the owner exactly what to look for.
4. **Small reversible steps.** One topic per commit, a clear message, push, then check the result. Keep a safety copy before any history rewrite.
5. **Statistics and results never change by accident.** If the project computes results, they are frozen by backtests (see `backtest`). A result may change only when the owner asked for it, and the commit message says which numbers moved and why.
6. **Secrets live only in a local `.env` file** that Git never sees (see `secretguard`). A key that reached GitHub, even briefly, is treated as stolen.
7. **Do not create pull requests, force push, or touch other repositories unless asked.**

## The order to adopt things

Do the phases in this order. Each ends with an exit rule, so you know it is really done.

| Phase | Skill | Exit rule |
|---|---|---|
| 0. Find out what is really shipped | `releaseintegrity` | one command rebuilds the shipped file and the fingerprint matches |
| 1. Safety net | `secretguard` | history scan clean, a made up fake key is refused by the commit blocker |
| 2. Backtests | `backtest`, `propertytests` | changing a formula by a tiny amount fails a test, even after the golden files are regenerated |
| 3. Hostile input and clicking tests | `hostileinput`, `uitests` | hostile text creates no page element anywhere a person or file can enter text |
| 4. Coverage floor | `coveragegate` | CI fails when coverage drops below the floor |
| 5. Hardening CI and the repository | `cihardening`, `repocontrols` | every action pinned, rules check green, local hooks installed |
| 6. Code scanning | `codescan` | the scanner finds a planted bad file and never scans zero files |
| 7. Mutation checks | `mutationcheck` | no survivors on the core calculations, or each survivor has a new test |
| 8. Honest security checklist | `securityaudit` | every item marked applies, not applicable now, or later, with a reason |

You can start anywhere, but never skip the self checks. If the project is small, do phases 1, 2 and 5 first.

## Start of a new project: the first questions

1. Is the repository public or private, and which GitHub plan? (This decides which protections are free; see `repocontrols`.)
2. Is there a server, a database, logins, payments? (If not, many web security items do not apply; see `securityaudit`.)
3. What does the project compute or produce that must never change by accident? (These become the backtests.)
4. Is there an old trusted version that can act as an independent answer key?
5. Which file do users actually run, and is it built from the repository sources? (See `releaseintegrity`.)

## What to hand back to the owner at the end

A plain language report with: what you ran yourself versus what you only expect to work, the proof each check can fail, the remaining gaps, and the list of things only the owner can do (for example switching a setting on GitHub). Offer the next step and wait.

Read next: `references/adoption_checklist.md` (a tickable list) and `references/lessons.md` (the traps).
