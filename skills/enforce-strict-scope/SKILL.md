---
name: enforce-strict-scope
description: Audits the agent's code changes using `git diff` to ensure absolutely zero out-of-scope changes were made. Use this at the end of a coding task or when asked to check for unrelated changes, scope creep, or drive-by refactoring.
---
# Enforce Strict Scope

This skill provides a zero-tolerance workflow for ensuring that you have not introduced any out-of-scope changes, drive-by refactoring, or unrelated formatting adjustments during your coding task.

## The Problem

Coding agents frequently make "helpful" but unauthorized changes:
- Fixing indentation on lines they didn't write.
- Deleting old comments that were not part of the task.
- Renaming variables for "readability" outside the specific fix.
- Re-organizing imports or re-formatting unrelated functions.

This causes noisy pull requests, Git conflicts, and frustration. **This skill enforces a strict rule: if a code change is not mechanically required to solve the original assigned task, it must be reverted.**

## Workflow Instructions

Follow these steps exactly when triggered or when finishing a coding task. Do not skip any steps.

### 1. Gather the Evidence
Run `git diff` (or `git diff HEAD` if changes are already staged). This is your deterministic source of truth. You must use the raw diff to evaluate your work.

### 2. The Strict Audit
Read every single hunk in the `git diff` output.
For every single line added (`+`) or removed (`-`), ask yourself:
*"Is this exact line change mechanically required to solve the original task?"*

**Zero Tolerance Policy:** If a line change does any of the following, it is a **Violation**:
- Fixes formatting or indentation on an adjacent line.
- Removes an existing comment not related to the core logic of the fix.
- Changes a variable name for general "readability."
- Restructures code that was working fine just to make it "cleaner."
- Alters anything not explicitly asked for by the user.

### 3. The Correction Phase
If you identify any Violations in the audit:
- You **MUST** revert the unauthorized changes.
- Use surgical file edits (e.g., the `replace` tool) or `git restore <file>`, or `git checkout <file>` to revert the out-of-scope lines back to their original state.
- Focus specifically on putting back comments, reverting formatting tweaks, and undoing unnecessary refactors.

### 4. The Final Verification
- Run `git diff` again.
- Repeat the Strict Audit (Step 2) on the new diff.
- You must loop through these steps until the diff contains *only* the absolute minimum code required for the assigned task.

### 5. Reporting
Once the diff is clean:
- Present the final, clean `git diff` to the user.
- Confirm that all out-of-scope changes were purged and that the remaining changes strictly adhere to the original prompt.
