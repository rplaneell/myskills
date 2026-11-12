# Porting plan (template)

Status: plan for approval. Nothing is ported yet. Each step starts only after the owner says yes.

## Why
(The shipped file is not produced by the sources. Say what that costs: tests protect the wrong file, nothing proves which code produced it.)

## What is different (measured on DATE with script_inventory.py)
* identical: ...
* changed versions of existing modules (lines added and removed for each): ...
* embedded media (type and size): ...
* only in the shipped file (one line per feature, with the size of its script): ...
What the backtests already show: (agreement on N scenarios, and the exact list of differing lines).

## The order (smallest and most measurable first)
1. Step name. Exit rule: (a test that can check it).
2. ...

After each step: rebuild, run the whole suite, scans and audits, raise the coverage floor if it rose, update the known differences list, commit with a message that says which numbers moved and why.

## Decisions needed from the owner
1. ...

## Risks
* ...

## Done means
(All steps ported or dropped on purpose, no known differences left in the oracle comparison, floors and scans green, a tagged rebuild recorded in the release manifest naming its commit.)
