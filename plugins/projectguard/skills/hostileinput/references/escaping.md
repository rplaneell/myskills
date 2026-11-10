# How to escape correctly

## Rules of thumb

1. **Prefer `textContent`** over `innerHTML` when the value is text. The browser never parses it as markup.
2. **If you must build HTML**, escape every value that is not a literal: `&` to `&amp;`, `<` to `&lt;`, `>` to `&gt;`, `"` to `&quot;` (and `'` to `&#39;` inside single quoted attributes).
3. **Escape for the place where the value goes.** A value inside an attribute needs quotes escaped; a value inside a URL needs URL encoding; a value inside a `<script>` or a `style` needs more than HTML escaping: do not put values there at all.
4. **Escape at the insertion point**, not once at input. The same value is used in several places with different needs.
5. **Never concatenate into event handler attributes** (`onclick="..."`). Use `addEventListener` and `dataset`.
6. **Do not "sanitize" by deleting characters** unless you accept the data loss. Stripping `<>&"` in one place (as a quick fix) loses information and hides the real habit problem.

## One small helper is better than many

```js
function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c])); }
```

If the project has two helpers with different names (as we found), unify them. Every `innerHTML` assignment that includes a variable should route it through the helper, and `codescan` flags the ones that do not obviously do so.

## Quick review questions for each sink

* Where does this value come from (a person, a file, a saved session, the program)?
* Which characters can it contain?
* Is it escaped here, or earlier in a way I can see?
* If an attacker controlled it completely, what would the page do?

## Content Security Policy as a second line

A policy such as `default-src 'none'; script-src 'unsafe-inline'; script-src-attr 'none'; connect-src 'none'; form-action 'none'; base-uri 'none'` limits the damage of an injection: no attribute handlers, no network. For a single file offline tool it is a meta tag in the head. Test that it exists and has not loosened (a test reads the meta tag and asserts the key directives). It does not replace escaping: injected markup can still change what the page shows.
