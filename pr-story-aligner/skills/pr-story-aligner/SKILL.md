---
name: pr-story-aligner
description: "Use before opening or merging a pull request, to check the changes against the acceptance criteria of the linked GitHub issue, Jira ticket or Linear issue."
---

# PR Story Aligner

Check that a branch or pull request does what its ticket asks for, before review or merge.

## 1. Get the requirements

Find the ticket reference in the branch name, PR title or description, or commit messages (`#123`, `PROJ-123`, `ENG-45`), or ask the user.

- **GitHub issue**: `gh issue view <number> --comments`
- **Jira or Linear**: use the Jira or Linear connector tools if the user has one connected. Otherwise ask the user to paste the ticket text
- Extract the acceptance criteria as a numbered list. If the ticket has none, derive them from the description and tell the user

## 2. Get the changes

- Open PR: `gh pr view <number>` and `gh pr diff <number>`
- Local branch: `git diff <base>...HEAD` and `git log <base>..HEAD --oneline`, where base is usually `main`

## 3. Compare

For each criterion, mark:

- **Done**: point to the files and lines that implement it, and the test that covers it
- **Partial**: say what is missing
- **Not found**: nothing in the diff addresses it

Also list **changes outside the ticket's scope** and missing tests for new behavior.

## 4. Report

Give a short table, then the gaps to fix before merge. Offer to draft a PR description that maps each criterion to the change. Do not post comments or edit the ticket or PR unless the user asks.
