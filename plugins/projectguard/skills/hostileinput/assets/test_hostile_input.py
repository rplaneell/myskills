"""Hostile input: text that looks like HTML must be shown as plain text, never turned into page elements or attributes.

Three attack styles in every place a person or a file can put text into the page:
  tag           <b id=pwn_t>x</b>                 a whole element
  attr_id       " id=pwn_a zzpwn=1 "              breaking out of an attribute to add attributes
  attr_handler  " onfocus=1 id=pwn_h "            breaking out of an attribute to add an event handler
The test looks at the PAGE STRUCTURE, so it works even when a Content Security Policy would stop injected scripts from running.
Keep payloads short (some boxes cut text at 24 characters).
"""
import pytest

PAYLOADS = {"tag": "<b id=pwn_t>x</b>", "attr_id": '" id=pwn_a zzpwn=1 "', "attr_handler": '" onfocus=1 id=pwn_h "'}

PROBE = """() => {
    const all = [...document.querySelectorAll('*')];
    return {
      rendered: /pwn_[tah]/.test(document.body.textContent),
      injected: all.filter(e => /^pwn_/.test(e.id)).map(e => e.tagName + '#' + e.id),
      stray: all.filter(e => e.hasAttribute('zzpwn') || [...e.attributes].some(a => /^on/i.test(a.name)))
                .map(e => e.tagName + ':' + [...e.attributes].map(a => a.name).join(',')).slice(0, 5)
    };
}"""
# NOTE: do not look for a stray attribute named x: SVG charts use x and y attributes legitimately. zzpwn is unmistakable.


# FILL IN: one function per place where text can enter. Each receives (page, payload, tmp_path) and leaves the page in the
# state where that text would be shown. Typical places: a name typed in a table, a file name, a cell inside an uploaded CSV
# or JSON, a custom label box, a pasted table, a saved session being imported again, a URL parameter.
def via_name_in_table(pg, payload, tmp):
    pg.fill("#nameBox", payload)
    pg.keyboard.press("Tab")
    pg.wait_for_timeout(500)


ENTRY_POINTS = {"name_in_table": via_name_in_table}


@pytest.mark.parametrize("attack", PAYLOADS)
@pytest.mark.parametrize("entry", ENTRY_POINTS)
def test_hostile_text_is_shown_as_text_and_creates_nothing(page, tmp_path, entry, attack):
    ENTRY_POINTS[entry](page, PAYLOADS[attack], tmp_path)
    r = page.evaluate(PROBE)
    assert r["rendered"], f"{entry}: the text never reached the page, so this test proved nothing"     # guards against a no op test
    assert r["injected"] == [], f"{entry}/{attack}: hostile text became page elements {r['injected']}"
    assert r["stray"] == [], f"{entry}/{attack}: hostile text added attributes {r['stray']}"


def test_the_detector_would_notice_a_real_injection(page):
    """Self check: if the page DID turn text into elements, the probe above must report it."""
    page.evaluate("document.body.insertAdjacentHTML('beforeend', '<b id=pwn_t zzpwn=1 onfocus=1>x</b>')")
    r = page.evaluate(PROBE)
    assert r["injected"] == ["B#pwn_t"] and r["stray"], r
