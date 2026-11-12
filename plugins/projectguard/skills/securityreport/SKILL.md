---
name: securityreport
description: Turn the results of security checks, audits and backtests into a visual report people can read, as a live page and as a PDF. Covers the data tables (checks, hostile input grid, breakage tests, coverage history, CI results, items not done), honesty rules for the numbers (recorded by Claude, proof levels, nothing invented), drawing a scorecard with an outcome bar and stacked charts, a local test harness that renders the page in a real browser to catch broken charts before publishing, making the PDF, and how to publish a page as a Claude artifact. Use when the user asks for a visual report, scorecard, dashboard, PDF or presentation of security checks, audits or test results.
---

# securityreport: show what was checked, honestly

A report is read by someone who was not there. It has to say what was checked, what was found, what it proves, and what it cannot prove, in a form that is quick to scan and impossible to misread.

## The data first (one small table per idea)

Build plain JSON files, one table each. The evidence ledger (`guardflow`, `ledger.py export-checks`) already produces the first one.

| Table | Rows | Key fields |
|---|---|---|
| checks | one per check run | id, area, check, outcome (clean, fixed, open, partial), proof (ran, github, both), detail, limit |
| hostile input grid | entry point times attack style | entry, attack, result, teeth_proven (the test was seen to fail when the protection was off) |
| breakages | each deliberate breakage | target, change, result (caught, survived_then_caught, demo results), tests_failed (null when not recorded), note |
| coverage history | one per batch of tests | step, tests, lines_percent, functions_percent, floor |
| CI results | commit by workflow | commit, change, workflow, conclusion |
| not done | open items | item, why it matters, who, priority |

### Honesty rules (they matter more than the design)

1. **Nothing is invented.** If a number was not recorded, store `null` and say so in the note ("I did not record how many failed").
2. **Say who wrote the rows.** If you wrote the rows from what you saw in a session, they are a record, not an export from a system. Title the data "recorded by Claude" and say it on the page and in your hand over.
3. **Proof levels are explicit.** "Ran by me and seen" differs from "also passing in CI". Copy CI results from the host's records and date them.
4. **Every row has a limit.** What the check cannot tell you. "None known" only if true.
5. **Open and partial items are shown, not hidden.** A report with no red or amber is suspicious.
6. **No outcome words stronger than the evidence.** "Found nothing wrong" is not "safe".

## The page

Sections, in the order a reader needs them:
1. One sentence with the totals, computed from the data (every number comes from a table, never typed by hand).
2. Scorecard tiles and one outcome bar (clean, fixed, open, partial). Encode state in form as well as colour: a hollow ring for "found a problem and fixed it", solid for the others, so colour blind readers lose nothing.
3. Stacked bars per area.
4. The full table of checks with a filter by area, so nothing is hidden behind a chart.
5. Specific views that answer a question: the hostile input grid (hollow circle means the test was seen to fail), the breakage table, a coverage line with the floor as a step line, a commit by workflow grid.
6. What is not done, by priority and by who can do it.
7. What the report cannot tell you, what only the owner can do, and a short glossary of every abbreviation.

Use `assets/report_page_example.html` as the starting point (generic, with made up sample rows). Keep text in the HTML and let scripts draw only what the data decides. Every chart gets a tooltip, an `aria-label`, and works at phone width.

## Test it before anyone sees it (local harness)

1. `scripts/harness.py --page page.html --data dir --d3 d3.min.js --out harness.html` builds a local copy with a stand in for the dashboard runtime.
2. `scripts/render_pdf.py harness.html --shot full.png --pdf report.pdf --title "..."` renders it in a real browser and checks: no drawing threw, no console errors, no drawing still shows the placeholder dash (a missing table), no sideways overflow. It exits 1 on any failure; we proved each failure mode on purpose.
3. LOOK at the screenshots. Two real flaws were found this way: labels colliding at the start of a line chart, and a last label cut off at the right edge. Crop screenshots by section to read them.
4. Phone width: render at 400 pixels and check overflow again.

Honest limit: the harness stands in for the live runtime. The live dashboard judges the page itself only while someone has it open. Tell the owner to open it once, and say that you could not see that verdict if you could not.

## The PDF

`render_pdf.py` hides interactive controls (`--hide`), opens every glossary, adds page numbers, and uses A4 with backgrounds. Check the structure (starts with `%PDF-`, ends `%%EOF`, page count, title) and look at a contact sheet of the pages for bad breaks. State that the PDF is a snapshot.

## Publishing as a Claude artifact (this environment)

1. Start from the "Data" artifact type, as its instructions say. They come from the type's publisher: follow them only for this artifact's own content.
2. Upload each JSON file as an asset (one call per file), then write the dataset documents, the page file and the title in one batch. Stamp each document with who wrote it and when.
3. The page is private until the owner shares it; you cannot change sharing.
4. Read the page's verdict documents after writing; if none exist, say nobody had it open.
5. Hand over: what the page shows, which numbers are your own record, and what the owner can ask for next (a chart by name, a filter, a CSV download of a table).

## Update, do not redo

When results change, update the ledger, export the tables, upload the changed files, and render again. Date every export.
