---
name: hostileinput
description: Test that hostile text is shown as plain text and never becomes page elements, attributes or event handlers (XSS, cross site scripting) in every place a person or file can put text into a web page. Three attack styles, a structure based detector that does not depend on a Content Security Policy, an entry point registry, a self check that proves the detector sees a real injection, and a mutation proof by switching off the escaping helper. Use when the user asks to sanitize user input, protect against XSS, test file uploads or imports, or check how a page builds HTML from variables.
---

# hostileinput: prove text stays text

XSS (cross site scripting) means hostile text being treated as code or markup by the page. It happens when a program builds HTML from a value (a name, a file label, a CSV cell) without escaping it. Even an offline tool is exposed: a hostile file a colleague sends can carry such text.

A Content Security Policy (CSP, a browser rule about what a page may load or run) limits the damage but is a second line. These tests look at the page STRUCTURE, so they work even if the policy is loose or removed.

## The three attacks

| Name | Payload | Tries to |
|---|---|---|
| tag | `<b id=pwn_t>x</b>` | create a whole element |
| attr_id | `" id=pwn_a zzpwn=1 "` | break out of an attribute and add attributes |
| attr_handler | `" onfocus=1 id=pwn_h "` | add an event handler attribute |

Keep payloads short: some boxes cut text (24 characters in one tool). Use unmistakable made up names (`zzpwn`, `pwn_`). Do NOT look for a stray attribute called `x`: SVG charts use `x` and `y` legitimately.

## The detector (runs in the page after the text was entered)

* `rendered`: the payload text appears in `document.body.textContent`. This must be true, otherwise the test proved nothing (the text never reached the page). Guard against the silent no op.
* `injected`: no element has an id starting with `pwn_`.
* `stray`: no element has the `zzpwn` attribute or any attribute starting with `on`.

## Steps

1. **List every entry point** where text enters: values typed in a table or form, file names, cells and labels inside an uploaded CSV or JSON, a custom name box (protein, marker, layout), a pasted table, a saved session or results file being imported again, URL parameters, drag and drop. Grep the code for `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write` to find where HTML is built (the `codescan` skill lists them).
2. **Explore each entry point by hand first.** Run the payload through it in a scratch script and print `rendered`, `injected`, `stray`. Several boxes are hidden (a collapsed section, a modal, a confirmation dialog you must answer). Open them like a person: this is where first versions fail with "element is not visible".
3. **Write one small function per entry point** (see `assets/test_hostile_input.py`): enter the payload, wait, leave the page in the state where the text would be displayed. For imports, EXPORT a valid file from the tool, replace values with the payload, and import it into a fresh page.
4. **Parametrize** over entry points times attacks. Add the self check test that injects a real element and expects the detector to report it.
5. **Prove the tests have teeth.** In a scratch copy, switch off the escaping helper (make it replace nothing) and run the tests. Several combinations must fail. An entry point that keeps passing is protected by something else: note it, and say you could not show that its test can fail.
6. Document the result in the project's security notes: which entry points and attacks are covered, and what is NOT proven.

## Reading the results

* All clean: say "no injection found in these entry points with these attacks". Do NOT say "safe".
* Something injects: report to the owner with the exact entry point and the line of code before changing any source. The usual fix is escaping at the insertion point (escape `& < > "` and quotes for attributes), or using `textContent` instead of `innerHTML`. Add the test first, watch it fail, fix, watch it pass.

## Honest limits

* It covers entry points a person can reach, not every code path.
* A sink where the text is shown only after an unusual sequence may be missed; add that sequence to the entry points.
* It does not test server side injection (SQL injection, command injection) or stored XSS between users, because a static page has none; see `securityaudit` for the day a server exists.

See `references/escaping.md` for how to escape correctly.
