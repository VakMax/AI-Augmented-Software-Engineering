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
1. **Core Mandates** — Protect credentials, handle untrusted content, use context efficiently, follow project conventions, and report progress through topic updates.
2. **Available Sub-Agents** — Explain which specialist agents are available, when to delegate, and how to avoid conflicting parallel changes.
3. **Available Agent Skills** — List the available skills and explain how to activate their instructions.
4. **Hook Context** — Treat information from hooks as data rather than instructions that override the system prompt.
5. **Primary Workflows** — Follow research, strategy, implementation, and verification steps; require planning approval for new applications.
6. **Operational Guidelines** — Define concise communication, command safety, tool sequencing, file editing, memory handling, and user interaction.
7. **Git Repository** — Require explicit instructions before committing or pushing, review changes, and stage specific files.

### Annotations (≥6)

#### Section: Tone and Style (tone and verbosity)
> **Minimal Output:** Aim for fewer than 3 lines of text output (excluding tool use/code generation) per response whenever practical.

- **Behavior it produces:** Encourages short responses that are easy to follow in a terminal.
- **Failure it prevents:** Long explanations burying the useful information.
- **Evidence:** `prompts/system.md`, Operational Guidelines → Tone and Style.

#### Section: Engineering Standards (when not to act / confirm)
> If asked *how* to do something, explain first, don't just do it.

- **Behavior it produces:** Keeps the agent from treating a request for instructions as permission to change files.
- **Failure it prevents:** Making changes when the user only wanted an explanation.
- **Evidence:** `prompts/system.md`, Core Mandates → Engineering Standards → Confirm Ambiguity/Expansion.

#### Section: Development Lifecycle (workflow)
> Operate using a **Research -> Strategy -> Execution** lifecycle. For the Execution phase, resolve each sub-task through an iterative **Plan -> Act -> Validate** cycle.

- **Behavior it produces:** Encourages the agent to understand the project, choose an approach, make changes, and check them.
- **Failure it prevents:** Editing before understanding the problem or declaring success without verification.
- **Evidence:** `prompts/system.md`, Primary Workflows → Development Lifecycle.

#### Section: Tool Usage (tool usage)
> **File Editing Collisions:** Do NOT make multiple calls to the `replace` tool for the SAME file in a single turn.

- **Behavior it produces:** Makes the agent edit the same file sequentially.
- **Failure it prevents:** Conflicting edits that rely on an outdated version of the file.
- **Evidence:** `prompts/system.md`, Operational Guidelines → Tool Usage.

#### Section: Topic Updates
> Remember to call update_topic when you experience an unexpected event (e.g., a test failure, compilation error, environment issue, or unexpected learning) that requires a strategic detour.

- **Behavior it produces:** Encourages the agent to explain when a problem changes its approach.
- **Failure it prevents:** Leaving the user unsure why the agent changed direction.
- **Evidence:** `prompts/system.md`, Core Mandates → Topic Updates.

#### Section: Context Efficiency
> The agent passes the full history with each subsequent message. The larger context is early in the session, the more expensive each subsequent turn is.

- **Behavior it produces:** Encourages focused searches and file reads instead of collecting unnecessary information.
- **Failure it prevents:** Repeatedly carrying large, irrelevant tool outputs through later model calls.
- **Evidence:** `prompts/system.md`, Core Mandates → Context Efficiency.

### Context injection (`GEMINI.md`)
The project instructions are not included in either saved system prompt. I searched both files for the distinctive phrase "All money" from GEMINI.md, and neither contained it.

The v0.64.0 source shows how project context reaches the model instead:

1. `getSessionMemory()` retrieves project memory and wraps it in `<project_context>` inside `<loaded_context>`.
2. `getEnvironmentContext()` includes that memory in a `<session_context>` block.
3. `getInitialChatHistory()` puts this block into a message with `role: 'user'`. The client includes that history when starting the model chat.

This means the model can receive GEMINI.md's project instructions without those instructions appearing in the exported system prompt. This explanation is based on the version-pinned source, rather than a captured request payload.

**Source evidence:**
- [config.ts, lines 2611–2635: project-memory wrapping](https://github.com/google-gemini/gemini-cli/blob/v0.64.0/packages/core/src/config/config.ts#L2611-L2635)
- [environmentContext.ts, lines 63–110: session context and initial user message](https://github.com/google-gemini/gemini-cli/blob/v0.64.0/packages/core/src/utils/environmentContext.ts#L63-L110)
- [client.ts, lines 422–431: initial history passed into the chat](https://github.com/google-gemini/gemini-cli/blob/v0.64.0/packages/core/src/core/client.ts#L422-L431)

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
