"""Each repository rule must be able to FAIL. Put next to tools/check_repo_rules.py (adjust the path below)."""
import importlib.util, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("rules", ROOT / "tools" / "check_repo_rules.py")
rules = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rules)


def test_tracked_env_and_key_files_are_flagged_but_env_example_is_allowed():
    bad = [".env", ".env.local", "config/.env.production", "server.pem", "api.key", "id_rsa", "home/.ssh/id_ed25519", "node_modules/x/package.json", "cert.p12"]
    assert len(rules.check_forbidden_files(bad)) == len(bad)
    assert rules.check_forbidden_files([".env.example", "src/app.js", "docs/KEYBOARD.md"]) == []


def test_oversized_files_are_flagged():
    big = rules.CFG["max_bytes"] + 1
    assert len(rules.check_big_files({"src/huge.js": big})) == 1 and rules.check_big_files({"src/ok.js": 1000}) == []


def test_unpinned_actions_are_flagged():
    sha = "11d5960a326750d5838078e36cf38b85af677262"
    assert rules.check_workflow_pins({"a.yml": f"      - uses: actions/checkout@{sha} # v4\n      - uses: ./local\n"}) == []
    for bad in ["actions/checkout@v4", "actions/checkout@main", "actions/checkout@11d5960", "actions/checkout"]:
        assert len(rules.check_workflow_pins({"a.yml": f"      - uses: {bad}\n"})) == 1, bad


def test_bad_commit_messages_are_flagged():
    assert rules.check_message("abc1234", "Add backtests\n\nBecause results must not drift.\n") == []
    for bad in ["", "x" * 200 + "\n", "WIP stuff\n", "fixup! earlier\n", "Subject\nbody right under it\n"]:
        assert rules.check_message("abc1234", bad) != [], repr(bad)


def test_built_file_edited_without_a_source_change_is_flagged():
    if not rules.CFG["built_file"]:
        return
    built = rules.CFG["built_file"]
    assert rules.check_built_without_source({built}) != []
    assert rules.check_built_without_source({built, rules.CFG["source_prefixes"][0] + "x"}) == []
