# Debugging Worksheet: Stack Trace Surgery

Use this template to deconstruct an error before asking for a fix.

## 1. Observation
*   **Error Name:** (e.g., `TypeError`, `KeyError`, `500 Internal Server Error`)
*   **Location:** (File path and Line number)
*   **Context:** (What was happening in the app right before the crash?)

## 2. Evidence (The "Bleeding")
*   **The Message:** Paste the specific error message text here.
*   **Stack Trace Snippet:** Paste the 3-5 lines of the trace that point to your code.

## 3. Hypothesis
*   **My Guess:** "I think it failed because..."
*   **Why?** (What logic or assumption was violated?)

## 4. Verification
*   **How to prove it:** (e.g., "I will print the value of `user_id` before line 20.")
*   **Result:** What happened when you tried to prove it?

## 5. Synthesis
*   **Root Cause:** (What was actually wrong?)
*   **The Fix:** (Describe the change in plain English)
*   **The Lesson:** (What fundamental principle did I learn?)
