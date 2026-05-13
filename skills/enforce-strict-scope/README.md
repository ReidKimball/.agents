# Enforce Strict Scope

An AI agent skill that audits code changes using `git diff` to ensure zero out-of-scope modifications were introduced during a coding task.

## What It Does

Prevents the common problem of AI agents making "helpful" but unauthorized changes:

- Fixing indentation on lines they didn't touch
- Deleting old comments unrelated to the task
- Renaming variables for "readability" outside the fix
- Reorganizing imports or reformatting unrelated functions

These cause noisy pull requests, Git conflicts, and frustration. This skill enforces a strict rule: if a change is not mechanically required to solve the assigned task, it must be reverted.

## Workflow

1. **Gather evidence**: Run `git diff` as the deterministic source of truth
2. **Strict audit**: Evaluate every added/removed line against the original task
3. **Correction**: Revert any unauthorized changes surgically
4. **Verification**: Re-run `git diff` and repeat the audit until clean
5. **Reporting**: Present the final clean diff to the user

## When to Use

- At the end of any coding task to verify scope discipline
- When reviewing a diff before committing
- When asked to check for unrelated changes, scope creep, or drive-by refactoring
