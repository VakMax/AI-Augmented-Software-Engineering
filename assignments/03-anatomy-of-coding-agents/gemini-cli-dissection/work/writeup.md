# Week 3 Writeup — Inside a Coding Agent

**Name:** Maxim Vakulchik
**Gemini CLI version (`gemini --version`):** 0.64.0
**OS / shell:** Windows + Git Bash in VS Code
**Model(s) seen in trace:** gemini-3.5-flash-lite
**Session commit:** `751ba91`

> Evidence tags: `[OBSERVED]` = cite a timeline line, call number, or diff hunk.
> `[INFERRED]` = say what you're reasoning from.

---

## Part I — Session

**Narrative (one paragraph):** I gave Gemini the required prompt and let it work without giving it hints. It read TASK.md, inspected the code and tests, and ran pytest before making changes (calls 1–3). It then fixed the code, added shipping, and updated the tests, running them again as it went (calls 4–9). The trace also recorded three failed update_topic calls, even though none of the model calls failed. Gemini finished with a summary of its changes, and I checked the tests myself in a separate terminal: all 17 passed.

| Metric | Value |
|---|---|
| User prompts | 1 |
| Model calls | 14 |
| Tool calls (failed) | 27 (3) |
| Final `pytest` result | 17 passed in 0.03s in my independent check |
| Did you step in? When / what? | No extra prompts or hints. I only approved tool calls and ran the final tests separately. |

---

## Part II — System prompt annotation

### Outline
1. TODO — label
2. TODO — label
3. …

### Annotations (≥6)
#### Section: TODO (tone and verbosity)
> quote
- **Behavior it produces:** TODO
- **Failure it prevents:** TODO

#### Section: TODO (when not to act / confirm)
> quote
- **Behavior it produces:** TODO
- **Failure it prevents:** TODO

#### Section: TODO (workflow)
> quote
- **Behavior it produces:** TODO
- **Failure it prevents:** TODO

#### Section: TODO (tool usage)
> quote
- **Behavior it produces:** TODO
- **Failure it prevents:** TODO

#### Section: TODO
> quote
- **Behavior it produces:** TODO
- **Failure it prevents:** TODO

#### Section: TODO
> quote
- **Behavior it produces:** TODO
- **Failure it prevents:** TODO

### Context injection (`GEMINI.md`)
TODO — where it enters, with evidence.

---

## Part III — Tool design

### Inventory
| Category | Tools | Used in session (count) |
|---|---|---|
| File | TODO | TODO |
| Search | TODO | TODO |
| Shell | TODO | TODO |
| Web | TODO | TODO |
| Memory / other | TODO | TODO |

### Tool A: TODO
- **Source file:** TODO
- **Schema:**
  ```
  TODO
  ```
- **Why each parameter:** TODO
- **Description line that corrects a model mistake:** > TODO. **Mistake:** TODO
- **Deliberately does not:** TODO

### Tool B: TODO
- **Source file:** TODO
- **Schema:**
  ```
  TODO
  ```
- **Why each parameter:** TODO
- **Description line that corrects a model mistake:** > TODO. **Mistake:** TODO
- **Deliberately does not:** TODO

### Why old/new string edits?
TODO — two reasons plus a trace moment.

### Per-model tool descriptions
TODO — tool compared, what differs between model families, why.

---

## Part IV — Behavioral analysis

### 1. The loop
```
TODO: call#1 → tool → call#2 → …
```
What ended it: TODO

### 2. Context growth
TODO — chart or table, then explanation (growth and caching).

### 3. Planning
TODO

### 4. Error recovery
> quoted failure
TODO — what happened next and whether it was good.

### 5. The tests
TODO — any edits to existing tests, quoted diff, allowed by TASK.md?

### 6. Models
TODO
