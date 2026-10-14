# Week 3 Writeup — Inside a Coding Agent

**Name:** Maxim Vakulchik
**Gemini CLI version (`gemini --version`):** 0.64.0
**OS / shell:** Windows + Git Bash in VS Code
**Model(s) seen in trace:** gemini-3.5-flash-lite
**Session commit:** `b0e66a6`

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
**[OBSERVED]** The recorded loop was: model call → tool calls and their results → next model call. The table lists the tools following each response, in order.

| Model call | Tools called afterward |
|---|---|
| 1 | update_topic → read_file (TASK.md) |
| 2 | update_topic (failed) → read_file ×5 (code and tests) |
| 3 | update_topic → run_shell_command (pytest) |
| 4 | update_topic (failed) → replace (cart.py) |
| 5 | update_topic → replace (pricing.py) |
| 6 | update_topic → run_shell_command (pytest) |
| 7 | update_topic → read_file (test_cart.py excerpt) |
| 8 | update_topic → replace (test_cart.py) |
| 9 | update_topic → run_shell_command (pytest) |
| 10 | update_topic → run_shell_command (git status) |
| 11 | run_shell_command (git diff) |
| 12 | update_topic (failed) |
| 13 | update_topic (completion summary) |
| 14 | Final text response; no further tool calls |

**Evidence:** `submission/session_timeline.txt`, responses #1–#14 and the intervening TOOL entries.

**[OBSERVED] What ended it:** The agent gave its completion summary after call 14. I then independently confirmed 17 tests passed and exited with `/quit`. The recorded timeline shows no model-call errors or limit stopping the task.

### 2. Context growth
**[OBSERVED]** The CSV records the following input and cached-token counts:

| Call | Input tokens | Cached input tokens |
|---|---:|---:|
| 1 | 11,398 | 6,093 |
| 2 | 11,983 | 8,116 |
| 3 | 13,972 | 10,122 |
| 4 | 14,647 | 12,138 |
| 5 | 19,605 | 14,192 |
| 6 | 21,830 | 18,251 |
| 7 | 22,674 | 20,270 |
| 8 | 23,539 | 20,263 |
| 9 | 25,505 | 22,292 |
| 10 | 25,698 | 22,278 |
| 11 | 26,040 | 22,266 |
| 12 | 29,855 | 24,318 |
| 13 | 30,052 | 26,338 |
| 14 | 30,373 | 26,332 |

**Evidence:** `submission/session_calls.csv`, columns `input_token_count` and `cached_content_token_count`.

**[OBSERVED]** Input grew from 11,398 to 30,373 tokens, an increase of 18,975. Between calls 11 and 12, it increased by 3,815 tokens; the intervening tool call was `git diff` (`session_timeline.txt`, 22:24:44).

**[INFERRED]** The context grows because later requests carry earlier conversation content, including tool results, code, test output, and the agent's responses. The timing suggests the diff output contributed to the increase before call 12. The exported prompt's Context Efficiency section also states that full history is passed with subsequent messages.

**[INFERRED]** The cached-token count indicates that some input was served through caching rather than processed entirely from scratch. Reusing context can reduce processing work, latency, and input charges where cached-token pricing applies. Cached tokens are part of the input, not extra tokens to add to it. These logs do not establish how much money or time caching saved.

### 3. Planning
**[OBSERVED]** The agent used `update_topic` to describe its phases: reading requirements (call 1), researching the code and tests (call 2), implementing fixes and shipping (call 4), running tests (calls 6 and 9), and reviewing Git changes (call 10). There were 12 topic-update attempts, including 3 failures.

**[OBSERVED]** The recorded session contains no `enter_plan_mode` or `write_todos` calls. The timeline does not reproduce every text response, so it cannot rule out additional planning written in plain text.

**[INFERRED]** The main sequence matched the announced work: inspect the project, run tests, edit the implementation, update tests for shipping, verify, and review the diff. This follows the system prompt's research → strategy → execution workflow.

**[OBSERVED]** One departure from a clean phase transition occurred after call 4: the update titled "Implementing Code Fixes and Shipping Rules" failed, but the agent proceeded with the cart edit. Another interruption occurred after call 12, when the completion-topic update failed; call 13 retried successfully.

**[OBSERVED]** The system prompt says not to use `update_topic` on every turn and suggests topics spanning roughly 3–10 turns. This session used it on most model turns: 12 attempts across 14 calls.

**Evidence:** `submission/session_timeline.txt`, calls 1–14; `prompts/system.md`, Topic Updates and Development Lifecycle sections.

### 4. Error recovery
**[OBSERVED]** The first recorded failure was an `update_topic` call after model call 2, at 22:21:42:

> update_topic [FAILED] decision=None

Its requested title was "Researching Codebase and Test Suite." This occurred before the first recorded pytest command.

**[OBSERVED]** The agent continued by reading five files: `shopcart/cart.py`, `shopcart/pricing.py`, `shopcart/catalog.py`, `tests/test_cart.py`, and `tests/test_pricing.py`. After call 3, another `update_topic` succeeded, followed by the first pytest run.

**[INFERRED]** Recovery was reasonable because the failed progress update did not stop the investigation. The agent continued gathering relevant information and successfully updated its topic on the next model turn. However, the timeline does not include the tool's full error message, so I cannot establish the exact cause of the failure from this report.

**Evidence:** `submission/session_timeline.txt`, failed update at 22:21:42, the five following `read_file` entries, and the successful topic update at 22:21:43.

### 5. The tests
**[OBSERVED]** The agent changed three existing assertions in `tests/test_cart.py`. Each expected total increased by 599 cents, and each comment explains the added shipping:

```diff
-    assert cart.total() == 2160  # 2000 + 8% tax
+    assert cart.total() == 2759  # (2000 + 8% tax) + $5.99 shipping

-    assert cart.total() == 2333  # (2400 - 10%) + 8% tax
+    assert cart.total() == 2932  # ((2400 - 10%) + 8% tax) + $5.99 shipping

-    assert cart.total() == 3240  # (4000 - 1000) + 8% tax
+    assert cart.total() == 3839  # ((4000 - 1000) + 8% tax) + $5.99 shipping
```

**[OBSERVED]** TASK.md permits these changes:

> Some existing tests check `Cart.total()` with values from before shipping existed. You may update those expected values — and only those — and note why in a comment.

**[INFERRED]** All three assertion edits fit that permission: they preserve the original setups and add only the required shipping amount. They do not weaken the original quantity or discount tests to hide a bug.

**[OBSERVED]** The agent also added:
- `test_free_shipping_threshold`: verifies free shipping at a subtotal of 6000 cents.
- `test_empty_cart_shipping_is_zero`: verifies an empty cart totals zero.
- `test_shipping_is_not_taxed`: verifies a 1200-cent subtotal totals 1895 cents with tax and shipping.

**[OBSERVED]** The new threshold test uses 6000 cents, so it does not directly test the exact 5000-cent boundary or a discount moving an order below that boundary. Passing 17 tests therefore does not establish exhaustive coverage of the shipping rules.

**Evidence:** Commit `b0e66a6`, `tests/test_cart.py` diff hunks beginning at lines 43 and 58; `work/run/TASK.md`, sections 2–3. No changes to `tests/test_pricing.py` appear in that commit.

### 6. Models
**[OBSERVED]** All 14 rows in `session_calls.csv` identify the model as `gemini-3.5-flash-lite`. I launched Gemini with `-m gemini-3.5-flash-lite`, and the recorded session shows no other model.

**[OBSERVED]** The three calls with the largest `thoughts_token_count` were:

| Call | Thoughts tokens | Nearby recorded activity |
|---|---:|---|
| 4 | 4,253 | After the first pytest run; before editing `cart.py`. |
| 5 | 760 | After the cart edit; before editing `pricing.py`. |
| 7 | 399 | After another pytest run; before rereading `test_cart.py`. |

**Evidence:** `submission/session_calls.csv`, rows 4, 5, and 7; corresponding entries in `submission/session_timeline.txt`.

**[INFERRED]** Call 4 likely involved diagnosing the failures and choosing the implementation changes. Call 5 likely focused on the pricing and shipping changes. Call 7 likely involved deciding how to update tests for the new shipping behavior. These interpretations come from the surrounding tool calls; token counts alone do not reveal the model's reasoning.

**[OBSERVED]** The assignment describes the default setup without `-m` as using `gemini-3.5-flash-lite` for routing and `gemini-3.8-flash` for the main work. My trace does not demonstrate that two-model setup because I explicitly selected one model.

**[INFERRED]** A smaller routing model can handle a simpler decision quickly and cheaply, while a larger model handles more demanding work. Running the entire session on a larger model would generally be expected to cost more and could take longer, with a possible improvement in difficult reasoning or code quality. Better results are not guaranteed, and I did not run that comparison.

**Source for the default-model description:** [Week 3 assignment, Part IV question 6](https://github.com/scottyUX/AI-Augmented-Software-Engineering/blob/main/assignments/03-anatomy-of-coding-agents/gemini-cli-dissection/assignment.md).
