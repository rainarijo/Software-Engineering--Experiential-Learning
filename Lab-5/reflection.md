# Lab 5 – Reflection

**1. Which issues were the easiest to fix, and which were the hardest? Why?**
The easiest were style issues from Flake8 and Pylint: removing the unused `math` import, changing `== None` to `is None`, wrapping long lines and adding the final newline. They are mechanical and do not change behaviour. The hardest was removing `eval`. It was not a one-line change because the function's interface had to change from accepting an expression string to accepting a numeric multiplier, and every caller had to be updated. The `global` statement was also harder because I had to decide where the running total should live instead.

**2. Did the static analysis tools report any false positives? If so, describe one example.**
Bandit B311 (pseudo-random generator) would be a false positive in a context where randomness is not security related, such as shuffling demo data. Here, though, it generates a ticket PIN, so I treated it as a real issue. The reverse also happened: the tools missed real problems. Bandit did not flag the hard-coded `gate_barrier_key` (its name does not match Bandit's "password/secret/token" patterns), and the code printed that key to the console. Only manual review caught that.

**3. How would you integrate static analysis tools into your actual software development workflow?**
I would run Flake8 and Pylint locally through a pre-commit hook so style problems never reach the repository. In CI (for example a GitHub Actions workflow), I would run all three tools on every pull request. The build would fail on any Bandit medium/high finding, any Flake8 error, or a Pylint score below a threshold such as 9.5. I would also keep a shared config (`.pylintrc`, `setup.cfg`) so the whole team uses the same rules.

**4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?**
The Pylint score went from 4.10 to 10.00, and Bandit and Flake8 now report zero issues. Security improved: there is no arbitrary code execution through `eval`, no shell injection through `os.system`, MD5 has been replaced with SHA-256, the PIN is unpredictable, and the secret is no longer in source or output. Robustness improved because errors are no longer silently swallowed, files always close, and logs no longer leak between calls. Readability improved through consistent snake_case names, docstrings, f-strings and shorter functions.
