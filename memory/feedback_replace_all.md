---
name: replace_all clobbers wrapper functions
description: Using replace_all to rename a call can corrupt the wrapper function that wraps that same call
type: feedback
---

Never use `replace_all` when the old string is the exact expression being wrapped by a new helper function in the same file.

**Why:** When `api_json(resp)` was introduced to wrap `resp.json()`, a subsequent `replace_all` of `resp.json()` → `api_json(resp)` also replaced the `resp.json()` call *inside* `api_json` itself, producing infinite recursion. This caused a confusing repeated-error-message bug that was hard to diagnose.

**How to apply:** After introducing a wrapper function (e.g. `api_json` wrapping `resp.json()`), manually replace call sites one by one — or use replace_all only after confirming the wrapper body itself does not contain the target string.
