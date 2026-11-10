# Lessons: the traps we actually fell into

Each item cost real time. Each has a defence that is now part of a skill.

1. **A scanner can be blind without telling you.** A code scanner reported zero findings; planting obviously bad code showed it found nothing either. Defence: a fixture of deliberately bad code that every rule must fire on, plus a rule that the number of files scanned equals the number of files present. (`codescan`)
2. **Tools skip folders silently.** Semgrep skips folders named `build` and `tests` and files ignored by Git, so scanning "build/scripts" scanned zero files and still exited cleanly. Defence: the scanned count guard above.
3. **Registry rule sets can load and still miss simple bad code.** Write a few rules of your own for the risks of your kind of project, and test them on the fixture.
4. **Fragments that start with `<script>` do not parse as JavaScript.** Extract the real scripts from the built file instead of scanning the source fragments.
5. **A passing golden test proves less than it seems.** Someone can regenerate the golden files from a broken build and the exact comparison goes green. Defence: an independent oracle, property tests, and a rule that golden files change only when the owner asked. (`backtest`, `propertytests`)
6. **Compare lists, not positions, when one side has an extra line.** One extra line in the oracle shifted every later line and caused false alarms. Strip the explained differences from both sides first.
7. **Two roundings can disagree at the edge.** A report shows 3 digits of the true value (39.05x becomes 39.1) while a file keeps 5 digits (39.05); rounding the file value again gives 39.0. Compare with the rounding step as tolerance.
8. **A number shown in two places needs a test comparing the two.** A threshold changed in one place only survived the first report tests, because nothing compared the summary sentence with the table. (`mutationcheck`, `uitests`)
9. **Clicking can scroll the page and push the target off screen.** Mouse actions at off screen positions land on nothing, silently. Scroll the target into view right before every mouse action, and assert that each step really changed something. (`uitests`)
10. **Controls inside collapsed sections are not visible.** A click times out with "element is not visible". Open the section first, like a person would.
11. **A test of a hidden feature can pass by testing nothing.** Always assert that the hostile text actually reached the page ("rendered") before asserting nothing was injected. (`hostileinput`)
12. **SVG charts use attributes called x and y.** A detector looking for a stray attribute named x flagged every chart label. Use an unmistakable made up name.
13. **Headless browsers have no printer and block the clipboard.** Replace the print command with a stand in, test both the "printing started" and "printing blocked" paths, and expect the clipboard fallback. (`uitests`)
14. **A PDF's text is compressed.** Test its structure (starts with %PDF, ends with %%EOF, page count, title, size, images) instead of grepping for words.
15. **A browser version mismatch is not a bug in your code.** "Executable doesn't exist at ..." means the Playwright package and the installed browser build differ. Use an environment variable that points to an existing browser. Do not reinstall.
16. **Stale remote tracking branches fool hook tests.** In a test clone, leftover references made `pre-commit` skip the push hook ("nothing new to push"). Use a clean remote and a new commit.
17. **Coverage measures running, not checking.** Raising it to 100 percent with weak tests proves little. Pair it with mutation checks.
18. **Enforce the coverage floor only on a full run.** A partial run always looks worse.
19. **Measure twice before choosing a floor.** The wobble between identical runs was a line or two; leave about one and a half points of room, then ratchet up.
20. **Pinning protects the future, not the past.** A tag already tampered with before you pinned it stays tampered. Say so.
21. **A checksum from the same release page is not independent.** It catches a damaged or swapped download, not a compromised release. Say so.
22. **A hook that can be skipped is a safety belt, not a lock.** `--no-verify` and computers without the setup bypass it; keep a CI layer behind every local layer.
23. **Free private repositories lack several protections** (secret scanning, push protection, branch protection, CodeQL are paid). Replace each with a free layer and write down the gap honestly. (`repocontrols`)
24. **Do not rewrite history without a safety copy and the owner's yes.** When it is wanted (for example to fix authorship), keep a local backup branch, check the tree is byte identical, and push with a lease.
25. **Believe the evidence over the plan.** The file the lab used was not built from the repository at all. Find out what is really shipped before testing anything. (`releaseintegrity`)
