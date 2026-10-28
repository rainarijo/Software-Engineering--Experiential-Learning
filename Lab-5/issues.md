# Lab 5 – Issue Table (parking_lot_system.py)

| # | Issue | Type | Tool / Code | Line(s) | Description | Fix Approach |
|---|-------|------|-------------|---------|-------------|--------------|
| 1 | Shell command injection | Security (High) | Bandit B605 | 64 | `os.system("echo ... " + filename)` runs a shell command with user-controllable text; a filename like `x; rm -rf ~` would execute. | Replaced with a plain `print()`; no shell needed. |
| 2 | Weak MD5 hash | Security (High) | Bandit B324 | 53 | MD5 is broken and collision-prone. | Switched to `hashlib.sha256`. |
| 3 | Use of `eval` | Security (Medium) | Bandit B307, Pylint W0123 | 48 | `eval(surge_expr)` executes any string passed in – arbitrary code execution. | Function now takes a numeric `surge_multiplier`; fee = `base_rate * float(surge_multiplier)`. |
| 4 | Insecure random for ticket PIN | Security (Low) | Bandit B311 | 57 | `random.randint` is predictable; PINs could be guessed. | Used `secrets.randbelow(9000) + 1000`. |
| 5 | try / except / pass | Bug + Security (Low) | Bandit B110, Pylint W0702, Flake8 E722 | 28–33 | Bare `except: pass` silently hides every error (even typos / KeyboardInterrupt). | Catch only `KeyError` and print a message. |
| 6 | Hard-coded secret printed to console | Security (manual review) | Not flagged by tools | 76, 85 | Gate key is in source code and printed in plain text. | Read from env var `GATE_BARRIER_KEY`; print only whether it is configured. |
| 7 | Mutable default argument | Bug | Pylint W0102 | 15 | `entry_logs=[]` is shared across all calls, so logs leak between calls. | Default to `None`, create a new list inside the function. |
| 8 | `global` statement | Design | Pylint W0603 | 16 | Function mutates a global float. | Moved total into a module-level `ledger` dict. |
| 9 | Unused import / variables | Code quality | Flake8 F401/F841, Pylint W0611/W0612 | 4, 37, 47, 69 | `math`, `overtime_fee`, `base_rate` (unused because of eval), loop var `s`. | Removed them; `base_rate` is now actually used. |
| 10 | `== None` comparison | Style | Flake8 E711, Pylint C0121 | 38 | Should use identity check. | Changed to `is None`. |
| 11 | File opened without `with` / encoding | Bug risk | Pylint R1732, W1514 | 61 | File not closed if `write` fails; platform-dependent encoding. | `with open(filename, "w", encoding="utf-8")`. |
| 12 | Shadowed name | Code quality | Pylint W0621 | 67 | Parameter `parking_slots` hides the global. | Renamed parameter to `slots`. |
| 13 | Naming / docstrings / formatting | Style | Pylint C0103, C0114, C0116, C0209, C0301; Flake8 E501, W292 | Whole file | camelCase names, no docstrings, long lines, `%` formatting, no final newline. | snake_case names, docstrings, f-strings, lines ≤ 79, final newline, `if __name__ == "__main__":` guard. |

**Result:** Pylint 4.10 → 10.00/10, Bandit 5 issues → 0, Flake8 10 issues → 0. Program output is unchanged apart from the hash (now SHA-256) and the key no longer being printed.
