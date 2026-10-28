# Issue Table — library_catalog_system.py



| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Shell command built from input (Bandit B605, High) | Security | 58 | `os.system("echo ... " + filename)` passes a string to a shell, so a crafted filename could inject commands. | Removed `os.system`; use `print(f"...")`. Dropped the now-unused `os` use for shell calls. |
| Weak MD5 hash (Bandit B324, High) | Security | 47 | `hashlib.md5` is cryptographically broken and unsuitable for identifying patrons. | Switched to `hashlib.sha256`. |
| `eval` on a caller-supplied string (Bandit B307 / Pylint W0123, Medium) | Security | 40-43 | `calculate_fine(days, "days * 2.0")` runs arbitrary Python from the `calc_expr` argument, which allows remote code execution if the string ever comes from a user. | Removed `eval`; signature is now `calculate_fine(days_overdue, daily_rate=2.0)` and returns `days_overdue * daily_rate`. Updated the caller. |
| Non-cryptographic `random` for a PIN (Bandit B311, Low) | Security | 51 | `random.randint` is predictable, so temporary PINs could be guessed. | Use `secrets.randbelow`: `1000 + secrets.randbelow(9000)`. |
| Bare `except: pass` (Bandit B110 / Flake8 E722 / Pylint W0702) | Bug / Security | 24-27 | Swallows every exception including `KeyboardInterrupt`; an unknown book ID fails silently. | Catch only `KeyError`; later reworked into an explicit `catalog.get` check that reports the problem. |
| Hardcoded secret, printed to stdout (not flagged by any tool) | Security | 62, 70 | `MASTER_LIB_ACCESS_TOKEN_2026` is committed to source and echoed to the console. Bandit's B105 did not match the variable name `librarian_key`. | Read from the `LIBRARIAN_KEY` environment variable; print only whether it is configured. |
| Return inflates stock (not flagged by any tool) | Logic bug | 23-27, 64 | `return_book("B02")` raised B02 from 1 to 2 copies even though it was never issued. A silent data-integrity bug visible only by reading the output/export. | Added a `total` field per book; `return_book` refuses unknown IDs and returns that would exceed `total`. |
| Mutable default argument (Pylint W0102) | Bug | 15 | `active_issues=[]` is created once and shared across every call, so issue logs leak between callers. | Default to `None` and create a new list inside the function. |
| Non-snake_case name `issueBook` (Pylint C0103) | Style | 15 | Violates PEP 8 naming; inconsistent with the other functions. | Renamed to `issue_book` and updated the caller. |
| Missing docstrings (Pylint C0116) | Style | 15, 23, 30, 40, 46, 50, 54, 61 | Eight functions are undocumented. | Added a one-line docstring to every function. |
| File opened without `with` / encoding (Pylint R1732, W1514) | Bug (resource leak) | 55-57 | File is not closed if `write` raises; encoding depends on the platform. | `with open(..., "w", encoding="utf-8")`. |
| `%` formatting (Pylint C0209) | Style | 19 | Old-style string formatting. | Converted to f-strings. |
| Redundant if/else returns (Pylint R1703, R1705) | Style | 34-37 | `if cond: return True else: return False` can be a single expression. | `return catalog[book_id]["copies"] > 0`. |
| `== None` comparison (Pylint C0121 / Flake8 E711) | Style | 32 | Identity checks against `None` should use `is`. | Changed to `is None`. |
| Unused variables `late_fee`, `days` (Pylint W0612 / Flake8 F841) | Dead code | 31, 41 | Assigned but never used. | Removed both. |
| Unused import `csv` (Pylint W0611 / Flake8 F401) | Dead code | 6 | Import never used. | Removed. |
| Missing final newline (Pylint C0304 / Flake8 W292) | Style | 73 | File does not end with a newline. | Added. |
| `main()` runs on import | Design | 73 | Importing the module executes the demo, so it cannot be reused or tested. | Wrapped in `if __name__ == "__main__":`. |

## Results

| Tool | Before | After |
|------|--------|-------|
| Pylint | 5.32/10 (22 messages) | 10.00/10 |
| Bandit | 5 issues (2 High, 1 Medium, 2 Low) | 0 issues |
| Flake8 | 6 issues | 0 issues |

