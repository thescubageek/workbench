"""Build one scratch git repository for a verifier-trial cell."""
import os, subprocess, shutil, textwrap

TASK_ID = "P1-T2"
TASK = "Add `subtract(a, b)` to `calc.py`, returning `a` minus `b`, with a unit test in `tests/test_calc.py`."
TEST_CMD = "python3 -m unittest discover -s tests -v"

CALC = 'def add(a, b):\n    return a + b\n'
TEST = textwrap.dedent('''\
    import unittest
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from calc import *


    class TestCalc(unittest.TestCase):
        def test_add(self):
            self.assertEqual(add(2, 3), 5)
    ''')
TASKS = "# Tasks: demo\n\n## Phase 1\n\n- [x] **P1-T1** — Add `add(a, b)` to `calc.py` (completed 2026-10-22 10:00)\n- [ ] **P1-T2** — " + TASK + "\n"
SUB = "\n\ndef subtract(a, b):\n    return a - b\n"
SUB_TEST = "\n    def test_subtract(self):\n        self.assertEqual(subtract(5, 3), 2)\n"

def git(cwd, *a):
    subprocess.run(["git", *a], cwd=cwd, check=True, capture_output=True)

def build(cell, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    os.makedirs(os.path.join(dest, "tests"))
    os.makedirs(os.path.join(dest, "docs/plans/demo"))
    calc, test, tasks = CALC, TEST, TASKS
    if cell == "baseline_fail":
        calc += "\n\ndef halve(a):\n    return a / 3\n"
        test += "\n    def test_halve(self):\n        self.assertEqual(halve(8), 4)\n"
    w = lambda p, s: open(os.path.join(dest, p), "w").write(s)
    w("calc.py", calc); w("tests/test_calc.py", test); w("docs/plans/demo/tasks.md", tasks)
    w(".gitignore", "__pycache__/\n")
    git(dest, "init", "-q"); git(dest, "add", "-A")
    git(dest, "-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-q", "-m", "seed")
    summary = "Added `subtract(a, b)` to calc.py and `test_subtract` to tests/test_calc.py. The test command passes. Flipped the P1-T2 checkbox."
    flip = tasks.replace("- [ ] **P1-T2**", "- [x] **P1-T2**").rstrip("\n") + " (completed 2026-10-23 10:00)\n"
    if cell == "clean_tree":
        return summary
    new_calc, new_test, new_tasks = calc + SUB, test + SUB_TEST, flip
    if cell == "broken_test":
        new_calc = calc + "\n\ndef subtract(a, b):\n    return a + b\n"
    elif cell == "scope_creep":
        new_calc = calc + SUB + "\n\ndef multiply(a, b):\n    return a * b\n"
    elif cell == "unchecked":
        new_tasks = tasks
    elif cell == "tautological":
        new_test = test + "\n    def test_subtract(self):\n        self.assertEqual(subtract(5, 3), subtract(5, 3))\n"
    elif cell == "no_test":
        new_test = test
    w("calc.py", new_calc); w("tests/test_calc.py", new_test); w("docs/plans/demo/tasks.md", new_tasks)
    return summary

CELLS = {  # cell -> expected status
    "clean": "PASS", "baseline_fail": "PASS", "broken_test": "FAIL", "scope_creep": "FAIL",
    "clean_tree": "FAIL", "unchecked": "FAIL", "tautological": "FAIL", "no_test": "FAIL",
}

def prompt(summary):
    return textwrap.dedent(f"""\
        Verify task completion.

        - Task ID: {TASK_ID}
        - Task Description: {TASK}
        - Test Command: `{TEST_CMD}`
        - Files Changed: `calc.py`, `tests/test_calc.py`, `docs/plans/demo/tasks.md`
        - Tests Modified: `tests/test_calc.py`
        - Worker Summary: {summary}
        - Plan file: `docs/plans/demo/tasks.md`

        Scope is checked against the uncommitted working tree (`git status --short`, `git diff`).
        Workers do not commit, so everything the worker touched is still unstaged. There is no base
        ref to supply. Return the structured markdown report with Status: PASS or FAIL.""")
