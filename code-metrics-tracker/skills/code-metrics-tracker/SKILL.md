---
name: code-metrics-tracker
description: "Use when asked about code quality, technical debt, complex or duplicated code, what to refactor first, or whether quality got better or worse over time."
---

# Code Metrics Tracker

Measure complexity, size and duplication, find the code worth refactoring, and track the numbers over time.

## 1. Measure

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/metrics.py <dir>
python3 ${CLAUDE_SKILL_DIR}/scripts/metrics.py src --threshold 15 --dup-lines 8
```

The report shows:

- totals: files, code lines (without blanks and comments), functions, average and maximum cyclomatic complexity
- functions over the complexity threshold (default 10), with file:line and length
- the largest files and functions longer than 60 lines
- duplicated blocks of 6 or more lines (ignoring whitespace, string and number literals), as pairs of locations

Python is measured exactly with `ast`. JavaScript, TypeScript, Java, Kotlin, C#, Go, PHP, Rust, Swift, C and C++ are measured by counting branches (`if`, loops, `case`, `catch`, `&&`, `||`, `??`, ternaries) inside each function, which is close to ESLint's `complexity` rule but not identical. Vendor, build, generated and migration folders are skipped.

## 2. Track over time

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/metrics.py src --save .metrics/2026-10-03.json
python3 ${CLAUDE_SKILL_DIR}/scripts/metrics.py src --compare .metrics/2026-10-03.json
```

`--compare` shows the change in every total and lists the functions that became more complex. To compare with an older commit without a saved snapshot, check it out in a temporary worktree (`git worktree add /tmp/old <ref>`), run with `--save` there, then remove the worktree.

## 3. Decide what to refactor

Complexity alone does not make code a problem. Rank candidates by:

1. **Complexity times change frequency.** Get churn with `git log --since="6 months ago" --name-only --format= | sort | uniq -c | sort -rn | head -30`. A complex file that nobody touches is low priority; a complex file changed every week is where bugs come from.
2. **Duplication of logic, not of boilerplate.** Two copies of a pricing rule matter; two similar test setups usually do not.
3. **Test coverage.** Refactoring untested complex code needs characterization tests first.

## 4. Report

Give a short table of the top 5 to 10 candidates with complexity, length, churn and the reason, then a concrete first step for each (extract function, replace conditional chain with a lookup table, early returns, merge duplicated block into one function). Do not refactor without being asked; when asked, change one function at a time and run the tests after each step.

Avoid scores that sound more precise than they are. Report the measured numbers and explain them.
