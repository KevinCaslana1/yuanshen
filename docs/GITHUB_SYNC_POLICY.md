# Permanent GitHub Sync Policy

## Scope

This is the canonical repository policy for task completion after the human approval on 2026-09-12. It applies to every future task in this repository, including documentation, validation, paper assets, experiments, and code changes.

The repository remote is `origin` and the protected delivery branch is `main`.

## Completion contract

Every completed task must close this sequence:

```text
validate
  → inspect protected paths and secrets
  → git add -A / staged diff review
  → commit
  → git fetch origin
  → divergence check
  → git push origin main
  → git lfs push --all origin main
  → git lfs fsck
  → git push origin --tags
  → local HEAD == remote refs/heads/main
  → clean git status
```

Before the push, verify the task-specific tests and deliverables, `A题/` immutability, `data/raw/` read-only status, and absence of credentials or private keys. Inspect the staged diff, not only the working-tree diff.

After committing, fetch first and inspect:

```powershell
git fetch origin
git rev-list --left-right --count origin/main...HEAD
```

If the remote is ahead or the histories diverge, stop and report the condition. Never use force push, reset, rebase, branch deletion, or history rewriting to make the numbers match. If the ordinary push fails, preserve the local commit and report `WORK COMPLETE / GITHUB SYNC FAILED`; do not claim the repository is synchronized.

For repositories using Git LFS, upload all required objects with `git lfs push --all origin main`, run `git lfs fsck`, and confirm that no required object remains pending. Push formal tags with `git push origin --tags` without rewriting existing tags.

The final remote check is an exact comparison:

```powershell
git rev-parse HEAD
git ls-remote origin refs/heads/main
git status --short
```

The task is GitHub-synchronized only when the two commit IDs are identical and the working tree is clean. The final report must include the previous remote HEAD, local commits uploaded, final local/remote HEAD, equality result, LFS result, tags, validation result, secret scan result, and unexpected-file-change result.

## Deprecated historical policy

`LOCAL COMMIT ONLY`, `DO NOT PUSH`, and “do not push because the repository is Public” are deprecated by human decision as future instructions. Existing freeze/audit documents retain their original wording when it records what happened in an earlier stage; those historical statements must not be interpreted as the current policy.

## Protected project boundaries

The policy does not authorize numerical recomputation or changes to frozen results. `A题/` remains immutable, `data/raw/` remains read-only, Q1–Q4 frozen numerical outputs remain protected, and failed experiments remain audit records. Synchronization is a delivery operation and must not be used to conceal or delete history.
