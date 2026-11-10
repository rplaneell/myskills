---
name: uitests
description: Write reliable browser (Playwright) clicking tests that drive a web page like a person, for buttons, menus, dialogs, drag and zoom, file uploads, downloads, PDFs, printing, clipboard and keyboard. Includes a conftest with an optional browser path, helpers for the traps that make UI tests silently empty or flaky (scrolling targets into view, collapsed sections, off screen mouse actions, headless printing, PDF structure checks, rounding tolerant comparisons), and how to prove a UI test can fail. Use when the user wants end to end tests, to click every button, to raise coverage of user interface code, or to test reports, downloads and printing.
---

# uitests: click everything, trust nothing you did not see fail

End to end (E2E) tests drive the real page in a real browser. They are the only tests that exercise buttons, dialogs, drawing and output files together. They are also the easiest tests to get silently wrong, so this skill is mostly about traps.

## Setup

1. Install Playwright (`pip install playwright pytest`) and a browser. If the browser build on the machine differs from what the installed package expects ("Executable doesn't exist at ..."), do NOT reinstall: point the tests at an existing Chromium with an environment variable (`assets/conftest.py` supports `PQ_CHROMIUM=/path/to/chromium`, and does nothing when unset).
2. Copy `assets/conftest.py` (fixtures `browser`, `open_page`, `page`; the `page` fixture dismisses alert dialogs and asserts no uncaught page errors) and `assets/ui_helpers.py`.
3. Test the BUILT page the users run, not the sources.

## How to write a UI test

1. **Explore in a scratch script first.** Print what is on the page: `Object.keys(STATE)`, element ids, disabled states, what a click changes. Write assertions from facts, not guesses.
2. **One behaviour per test,** with a name that states the behaviour ("zoom out after zoom in returns to the full view and relocks the buttons").
3. **Assert that each step really changed something** before asserting the final result. Otherwise a click that missed makes the test pass vacuously.
4. **Cross check against trusted numbers.** Reports and downloads must agree with the golden results (see `backtest`), and two displays of one number must agree with each other (see `propertytests`).
5. **Prove it can fail** (see `mutationcheck`): break the code in a scratch copy and watch the right test fail.

## The traps (each one cost us time)

* **Clicking can scroll the page.** After a button click, the target (a chart) may be off screen and a mouse action at its position lands on nothing, silently. Scroll the target into view immediately before computing coordinates (`ui_helpers.screen_point` does this).
* **Collapsed sections hide their controls.** A click on a button inside a closed `details` times out with "element is not visible". Open it like a person would (`open_collapsed_section`).
* **Modals and confirmation dialogs.** Changing a setting may open a confirm box that must be answered before the next control exists.
* **Dialogs from the browser** (`alert`, `confirm`) hang a test unless handled: the fixture dismisses them.
* **Wheel with a held key.** Dispatch the event directly (`ctrl_wheel`); it is deterministic.
* **Drag.** Use several `mouse.move` steps; give the page time; assert the result changed.
* **Downloads.** Use `with page.expect_download() as dl:` and read `dl.value.path()`; check the suggested file name (it often contains today's date: compute it in the test).
* **PDF files.** Test structure, not words (page text is compressed): starts with `%PDF-`, ends with `%%EOF`, page count, title, creator, number of images, a size well above a failed or blank file, and that the temporary print sheet in the page was cleaned up. Allow time (60 seconds) for generation.
* **Printing.** A headless browser has no printer. Replace `window.print` with a stand in: one that announces "printing started" (to test the print sheet and its clean up on the next click) and one that does nothing (to test the page's fallback, for example offering a PDF).
* **Clipboard.** Headless blocks it. Test the fallback (the page puts the text in a box) and accept either outcome.
* **Rounding.** A report shows 3 significant digits of the true value; a file keeps 5. Two roundings can disagree exactly at a rounding edge (39.05 becomes 39.1 or 39.0). Compare with the rounding step as tolerance (`close_to_shown_digits`).
* **Tab characters.** A toast message that contained a tab shows it as a space in inner text. Normalize whitespace before comparing.
* **Escape and keyboard.** Test that Escape closes what it should and only that. We found a case where Escape in a rename box also closed the whole window; the fix was to stop the keypress propagating.
* **Focus traps.** Test that Tab at the last control wraps to the first inside a modal.
* **Timing.** Prefer waiting for a condition (`wait_for_function`, `expect_download`) over fixed sleeps; keep short sleeps only for animations you control.
* **Known issues.** Record a real but minor defect as `xfail(strict=True, reason=...)`; when it is fixed the test unexpectedly passes, strict mode fails the run, and you remove the marker and keep the test as a guard.

## What to report

How many tests, what areas they cover, coverage before and after (see `coveragegate`), any real issue found (with evidence: the exact steps), and the proof that the tests can fail.

## Honest limits

* Headless Chromium is not every browser or every operating system.
* Printing and the clipboard are tested by stand ins, not by the real thing.
* Visual correctness (layout, colours) is not checked unless you add screenshot comparisons, which are fragile.
