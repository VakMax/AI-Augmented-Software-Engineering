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
| Category | Tools | Used in recorded session (count) |
|---|---|---|
| File | read_file, list_directory, write_file, replace | read_file: 7; replace: 3; others: 0 |
| Search | glob, grep_search | 0 |
| Shell | run_shell_command, list_background_processes, read_background_output | run_shell_command: 5; others: 0 |
| Web | google_web_search, web_fetch | 0 |
| Planning and narration | update_topic, enter_plan_mode | update_topic: 12 attempts, including 3 failures; enter_plan_mode: 0 |
| Delegation and skills | invoke_agent, activate_skill | 0 |
| User interaction | ask_user | 0 |

**Evidence:** Tool availability comes from `/tools` in Gemini CLI 0.64.0. Usage counts come from `submission/session_timeline.txt`, which records 27 tool calls in the original session.

### Tool A: replace

- **Source files:** [Model-facing declaration](https://github.com/google-gemini/gemini-cli/blob/v0.64.0/packages/core/src/tools/definitions/model-family-sets/gemini-3.ts#L356-L394) and [implementation](https://github.com/google-gemini/gemini-cli/blob/v0.64.0/packages/core/src/tools/edit.ts#L1176-L1238).

- **Schema:** The declaration's types and required fields are reproduced below. Its parameter descriptions are explained afterward.

  ```json
  {
    "type": "object",
    "properties": {
      "file_path": { "type": "string" },
      "instruction": { "type": "string" },
      "old_string": { "type": "string" },
      "new_string": { "type": "string" },
      "allow_multiple": { "type": "boolean" }
    },
    "required": [
      "file_path",
      "instruction",
      "old_string",
      "new_string"
    ]
  }
  ```

- **Why each parameter:**
  - `file_path`: Identifies which file to edit.
  - `instruction`: Explains the goal of the change, giving meaning to the replacement.
  - `old_string`: Identifies the existing text to replace. Surrounding context helps target the right occurrence.
  - `new_string`: Supplies the complete replacement text.
  - `allow_multiple`: Explicitly permits replacing every matching occurrence. It is optional; the default behavior expects one match.

- **Description line that corrects a model mistake:**
  > Do not use omission placeholders like '(rest of methods ...)', '...', or 'unchanged code'; provide exact literal code.

  **Mistake:** Writing a shortened example into the actual file instead of supplying complete code. The implementation also checks for newly introduced omission placeholders.

- **Deliberately does not:** Replace every matching occurrence by default. Multiple replacements require `allow_multiple: true`, helping prevent an edit from changing unrelated occurrences.

### Tool B: run_shell_command

- **Source files:** [Dynamic description and schema](https://github.com/google-gemini/gemini-cli/blob/v0.64.0/packages/core/src/tools/definitions/dynamic-declaration-helpers.ts#L36-L159) and [implementation](https://github.com/google-gemini/gemini-cli/blob/v0.64.0/packages/core/src/tools/shell.ts#L1220-L1258).

- **Schema:** These are the parameter types and required fields for the no-sandbox configuration shown in my CLI. Descriptions are explained below.

  ```json
  {
    "type": "object",
    "properties": {
      "command": { "type": "string" },
      "description": { "type": "string" },
      "dir_path": { "type": "string" },
      "is_background": { "type": "boolean" },
      "delay_ms": { "type": "integer" }
    },
    "required": ["command"]
  }
  ```

- **Why each parameter:**
  - `command`: Specifies the command to execute; it is required.
  - `description`: Gives the user a short explanation of the command.
  - `dir_path`: Selects an existing working directory within the workspace. If omitted, the project root is used.
  - `is_background`: Allows a long-running server or watcher to continue in the background.
  - `delay_ms`: Controls how long to wait for initial output after starting a background process.

  When tool sandboxing is enabled, the source conditionally adds `additional_permissions` for requesting network and filesystem access.

- **Description line that corrects a model mistake:**
  > This tool executes a given shell command as `powershell.exe -NoProfile -Command <command>`.

  **Mistake:** Assuming commands use Bash syntax because I launched Gemini from Git Bash. The Windows tool description explicitly identifies PowerShell as the command interpreter.

- **Deliberately does not:** Create a missing working directory through `dir_path`. The parameter description requires an existing directory within the workspace. This helps avoid treating a mistyped path as a request to create a new folder.

### Why old/new string edits?
1. **It targets the code by its contents.** Line numbers can shift when earlier edits add or remove lines. Matching the existing text and surrounding context helps identify the intended code without depending on its position. The default single-match rule also guards against ambiguous replacements.

2. **It keeps changes focused.** Sending only the old and new text usually takes fewer tokens than rewriting a whole file. Smaller changes are also easier to review and reduce the chance of accidentally deleting unrelated code. The tool description explicitly gives these reasons.

**Trace example:** After model call 4, the `replace` call at 22:22:54 supplied an `old_string` beginning with `def add_item(...)`. This shows the agent targeting the method by its text rather than a line number. All three recorded replacements succeeded; the trace does not show a replacement failing because its target moved or became ambiguous.

**Source:** [Gemini 3 replace description](https://github.com/google-gemini/gemini-cli/blob/v0.64.0/packages/core/src/tools/definitions/model-family-sets/gemini-3.ts#L356-L384).

### Per-model tool descriptions
I compared `replace` in `default-legacy.ts` and `gemini-3.ts`, both at tag `v0.64.0`.

| Detail | default-legacy.ts | gemini-3.ts |
|---|---|---|
| Read before editing | Explicitly tells the model to use `read_file` before replacing text. | That instruction is absent from the tool description. |
| Matching context | Requires at least 3 lines before and after the target text. | Requests significant context without a fixed line count. |
| Instruction guidance | Includes WHY/WHERE/WHAT questions and good/bad examples. | Uses a shorter explanation requiring a clear, self-contained goal. |
| Reason to choose the tool | Does not include the newer surgical-edit justification. | Highlights lower token usage, easier reviews, and avoiding accidental deletions. |
| Parameter structure | Five properties; four required. | Same property types and required fields. |

For example, the legacy description says:
> Include at least 3 lines of context BEFORE and AFTER the target text, matching whitespace and indentation precisely.

The Gemini 3 description instead says:
> This tool requires providing significant context around the change to ensure precise targeting.

**[INFERRED]** Different models may need different amounts of guidance to use the same tool reliably. The legacy version supplies more examples and repeated instructions, while the Gemini 3 version is shorter. These files show the wording differences, but do not prove which description performs better.

**Sources:**
- [default-legacy.ts, replace declaration](https://github.com/google-gemini/gemini-cli/blob/v0.64.0/packages/core/src/tools/definitions/model-family-sets/default-legacy.ts#L349-L410)
- [gemini-3.ts, replace declaration](https://github.com/google-gemini/gemini-cli/blob/v0.64.0/packages/core/src/tools/definitions/model-family-sets/gemini-3.ts#L356-L394)

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
