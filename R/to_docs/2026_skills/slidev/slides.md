<style>
  section { font-size: 24px; }
  table { font-size: 17px; margin: auto; }
  h1 { color: #2d5986; }
  .cover h1 { font-size: 48px; color: #1a3a5c; }
  .cover { text-align: center; }
  blockquote { border-left: 4px solid #2d5986; padding-left: 1em; color: #555; }
</style>

# CLI Agents, Skills & the Return of the Shell
**Oliver Dürr**
<!-- HTWG Konstanz / TIDIT.ch -->

---

# Resources
- https://code.claude.com/docs/en/overview Claud Code Docs (You can chat with it)
- https://github.com/mgechev/skills-best-practices

---

# LLMs — The Workhorses (API Models)

| Model | Provider | Input $/M | Cached $/M | Output $/M | SWE-bench |
|-------|----------|----------:|-----------:|-----------:|----------:|
| **Claude Opus 4.5** | Anthropic | $5.00 | $0.50 | $25.00 | **80.9%** |
| **Gemini 3.1 Pro** | Google | $2.00 | ~$0.20 | $12.00 | 80.6% |
| **GPT-5.2** | OpenAI | $1.75 | — | $14.00 | 80.0% |
| Claude Sonnet 4.6 | Anthropic | $3.00 | $0.30 | $15.00 | 79.6% |
| Claude Haiku 4.5 | Anthropic | $1.00 | $0.10 | $5.00 | — |
| GPT-5 mini | OpenAI | $0.25 | $0.025 | $2.00 | — |
| Gemini 2.5 Flash | Google | $0.15 | ~$0.02 | $0.60 | — |

SWE-bench Verified (500 human-validated problems). Prices as of Mar 2026.
Sources: [OpenAI](https://openai.com/api/pricing/) · [Anthropic](https://platform.claude.com/docs/en/about-claude/pricing) · [Google](https://ai.google.dev/gemini-api/docs/pricing) · [SWE-bench](https://www.swebench.com)

---

# LLMs — Open Source / Self-Hosted

| Model | Total Params | Active Params | Suitable Hardware |
|-------|------------:|-------------:|-------------------|
| DeepSeek R1 14B | 14B | 14B | Laptop (16 GB) |
| Qwen 3.5-35B (MoE) | 35B | 3B | Laptop (16 GB), Mac Mini 32G |
| DeepSeek R1 32B | 32B | 32B | Mac Mini 32G |
| Llama 3.3 70B | 70B | 70B | DGX Spark (128G) |
| Qwen 3.5-122B (MoE) | 122B | 10B | DGX Spark (128G) |

- **MoE** = Mixture of Experts — only a fraction of parameters active per token
- **NVIDIA DGX Spark**: 128 GB unified memory, Grace Blackwell chip
- Inference via **Ollama**, **llama.cpp**, or **vLLM** (GGUF quantized)
- Self-hosted: data stays local, ~20 ms latency on LAN vs 250–800 ms cloud

---
layout: cover
---

# Modes of Interaction

---

# Level 1 — Chat Interfaces: Just Talk

| Platform | Provider | Released | Notes |
|----------|----------|----------|-------|
| ChatGPT | OpenAI | Nov 2022 | First mainstream LLM chat |
| Bard / Gemini | Google | Mar 2023 / Feb 2024 | Rebranded to Gemini |
| Claude | Anthropic | Mar 2023 | Constitutional AI |
| HuggingChat | Hugging Face | Apr 2023 | Open-source models |
| Open WebUI | Community | 2023 | Self-hosted, Ollama backend |

- In original form: just conversation
- Tool calls: user &rarr; LLM &rarr; copy to tool &rarr; paste result &rarr; LLM
- Preferences live in the prompt (system prompt, custom instructions)

---

# Level 2 — AI Coding IDEs: Do When You Trigger Them

<!-- Screenshot will be provided -->

| Tool | Type | Released | Open Source |
|------|------|----------|:-----------:|
| GitHub Copilot | IDE Plugin | Jun 2022 | No |
| Cursor | VS Code Fork | Mar 2023 | No |
| Windsurf (Codeium) | VS Code Fork | Nov 2024 | No |
| Roo Code | VS Code Plugin | 2024 | Yes |
| Antigravity | IDE | 2025 | No |

---

# Level 2 — AI Coding IDEs (cont.)

- **Tools**: predefined tool set, Unix commands, MCP servers
- **Preferences**: `AGENTS.md`, rules files, custom instructions
- Tightly integrated in IDE, typically built for coding

> **Question:** Do we even need a traditional IDE in the future?
> Cursor is becoming more like a tool to orchestrate agents.

---

# Level 2 — Command Line Interfaces (CLI)

**Predecessors:** GitHub CLI (2023, very limited), Aider & openCode (2024)

### 2025 — The CLI Kick-Off

| CLI | Provider | Released |
|-----|----------|----------|
| **Claude Code** | Anthropic | Feb 2025 |
| **Codex CLI** | OpenAI | Apr 2025 |
| **Gemini CLI** | Google | Jun 2025 |

<!-- Screenshot will be provided -->

- **Tools**: terminal commands (naturally!), MCP servers, **skills**
- **Extensions**: browser automation, system-level actions on your behalf
- CLIs feel more natural for **non-coding tasks** (can still do coding too)
- CLIs are also the LLM providers' answer to Cursor & GitHub Copilot

---
layout: image-right
image: https://upload.wikimedia.org/wikipedia/commons/9/99/DEC_VT100_terminal.jpg
---

# The Power of the Shell

The shell — since the 1970s.
Works on Linux, macOS, Windows (PowerShell).

- **The CLI is itself a command** — it can be called by other commands
- The CLI can be part of a **Unix pipeline**
- Nothing stops you from using the CLI to call other CLIs

> We'll come back to this with demos later.

---

# Level 3 — Hosted Agents

Agents waiting to be triggered by external events.

- **n8n** — workflow / event automation with agent features
- ...
- **openClaw**

<!-- Screenshot will be provided (openClaw Mania) -->

### Trigger Sources

- Incoming E-Mail, Slack, Telegram, webhooks, etc.
- Scheduled tasks, e.g. every day at 8:00 AM
- Git events (PR opened, issue created, ...)

---
layout: cover
---

# Tool Calling & Preferences

---

# The Agentic Loop

This usually happens in a loop (aka Reason Act Loop, ReAct) 

1. The system (“You are XXX a helpful assistant…”) and the user prompt (“Please add ...”) are sent to LLM.  
2. The LLM returns the response (usually request to use a tool).  
3. The system fulfills the request (e.g. calls a **tool**) and sends the result back to the LLM.

Step 2 and 3 are iterated until success (the ReAct loop ends).

![ReAct Loop Illustration](imgs/react_from_bbs25.png)


> We will implement a simple ReAct loop 'manually' later.

---

# Predefined Tools (in the Prompt)

<!-- Screenshot will be provided (Roo Code tools, from old slides) -->

- IDE integrations started with this approach
- A set of predefined tools, registered completely in the **initial prompt**
- Example: Roo Code uses ~50K tokens just for tool definitions ()
- Repeated tool calling and parsing output (ReAct loop)

> **Problem**: fixed toolset, large prompt overhead — every model call pays for the full tool schema.

---

# MCP Servers

**Model Context Protocol** — a standard to extend LLM capabilities.

```
┌──────────────┐     MCP (JSON-RPC)     ┌────────────────┐
│  LLM Client  │◄──────────────────────►│   MCP Server   │
│  (Claude,    │                        │  (DB, API, …)  │
│   Cursor, …) │                        └────────────────┘
└──────────────┘
```

- MCP servers expose **tools**, **resources**, and **prompts** to the LLM
- Adopted by Claude Code, Cursor, Windsurf, and others
- Decouples tool implementation from the LLM client

Token efficiency: Only the relevant parts are loaded into context — saves tokens.

---

# Skills

- Introduced early 2025 with **Claude Code**
- A way to extend CLI capabilities and adapt them to your needs
- Plain **Markdown files** that can call other CLI tools
  - Including other skills, Python, Bash, etc.
- Token efficient via **progressive disclosure** — only loaded when needed

See: [Agent Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

---

## Skills — Typical Structure

```markdown
pdf-skill/
├── SKILL.md          ← main instructions (always loaded)
├── FORMS.md          ← form-filling guide (loaded on demand)
├── REFERENCE.md      ← detailed API reference (loaded on demand)
└── scripts/
    └── fill_form.py  ← utility script called by the skill
```

Saving Context with **Progressive disclosure**: 
- Level 1: Header of `SKILL.md` used to register the skill.
- Level 2: Read `SKILL.md` itself, which could also reference other files.
- Level 3: Other files like `FORMS.md` and `REFERENCE.md` are loaded on demand.

---
layout: center
---

# Demo Time

---

# Demo: easy_chef

Translates a recipe into my preferred format with mise en place and ingredient lists.

- The skill is public: [github.com/oduerr/skills_public/.../easy_chef](https://github.com/oduerr/skills_public/tree/main/skills/easy_chef)
- Uses just `SKILL.md` — no scripts needed (small header to register the skill)

```code
---
name: easy_chef
description: "Use whenever the user shares a recipe or asks to simplify, reformat, or explain a dish ..."
---

# Easy Chef
Transform any recipe into a structured, easy-to-follow format with cross-referenced ingredients and culinary critique.
...
```

Inside CLI (claude, gemini) 
```
Give me a recipe of new york cheesecake.
```

---

# Demo: email_router

- [github.com/oduerr/skills_private/.../email_router](https://github.com/oduerr/skills_private/tree/main/skills/email-router)

```
email-router/
├── SKILL.md            ← main instructions (always loaded)
├── maba.md             ← specialization for "MABA" use-case (loaded on demand)
├── praktikantenamt.md  ← specialization for the internship office (loaded on demand)
```
From SKILL.md
```markdown
# Email-Router

Du bist Oliver Dürrs persönlicher E-Mail-Assistent. Deine Aufgabe ist es, eingehende E-Mails zu klassifizieren und passende, fertig kopierbare Antworten auf Deutsch zu generieren.

## Schritt 1: Klassifikation

Lies die E-Mail und bestimme die Kategorie:

| Kategorie | Schlüsselbegriffe / Kontext |
|---|---|
| `praktikantenamt` | Praktikum, Praxissemester, PPS, Praktikantenstelle, Pflichtpraktikum, Anrechnung Praktikum |
| `maba` | Bachelorarbeit, Masterarbeit, BA, MA, Abschlussarbeit, Thesis, Betreuung, Themenvorschlag |
```
<!-- Live demo -->

---

# Demo: htwg-mail

Queries a file-based SQLite database of my HTWG mails, operating a Python script.

- Private repo: [github.com/oduerr/skills_private/.../htwg-mail](https://github.com/oduerr/skills_private/skills/htwg-mail)
- Uses `SKILL.md` + a Python script (SQLite query to access db)

**Sample prompts:**
```
Welche Mails habe ich am Schmotzigen Dunstig 2024 bekommen?
```

```
which tools did you use with which calls?
```

```
Wieviele Mails sind in der Datenbank?
```

```
which tools did you use with which calls?
```

<!--
Oh Wieviele Mails sind in der Datenbank? Geht ja gar nicht mit dem python script.
-->

---

# htwg-mail — The Surprise

Those clever bastards didn't use the Python script directly — they ran a raw **SQLite query**.

> Super-human performance (at least compared to me).

The LLM figured out the database schema on its own and wrote optimized SQL — bypassing the intended Python wrapper entirely.

Let's look at the output using `claude-devtools`:

---
layout: center
---

![HTWG Mail Query Output](imgs/emails_getting_total_num.png)


--- 

# The Power of the Shell
### (with demos)

---

# Remember the 70s?

```bash
echo "Hello, World" | wc -c
```
**Output**: `13`

```bash
echo "Hello, World" | awk '{print $2}' | wc -c
```
**Output**: `6`

```bash
wc < file.txt
```

<!--
Speaker notes:
wc -c counts the number of characters in the input.
For tokens, one could use ttok.
-->

---

# The CLI Is a Command!

```bash
echo "What is 'Hello Guys' in Chinese and Italian" | gemini
```

```bash
echo "What is 'Hello Guys' in Chinese and Italian" 
  | gemini --model gemini-2.5-flash
```

Pipe text directly into an LLM — just like any other Unix tool.

---

# Piping Across LLMs

```bash
gemini -p "Is this a good recipe?" < schwaebischer_kartoffelsalat.md 
  | claude -p "Übersetze ins Deutsche"
```

**Output**:
```
Dies ist ein ausgezeichnetes, technisch durchdachtes Rezept für einen
traditionellen schwäbischen Kartoffelsalat. Sein Erfolg liegt in
mehreren entscheidenden kulinarischen "Profi-Kniffen":

*  Thermische Absorption: Die Zwiebeln in heißer Brühe…
*  Die Ölbarriere: Das Öl zuletzt hinzuzufügen…
*  Zwiebelbehandlung: Das Blanchieren der Zwiebeln…
```

Two models, one pipeline. Gemini evaluates, Claude translates.

---

# A Skill Can Spawn Other CLIs

### Demo: Council of Bots

- A task you want to ask **Gemini, Claude, and OpenAI** simultaneously
- Start 3 CLIs in parallel and collect answers from each
- Merge and consolidate the answers

This is implemented as a skill that spawns 3 CLIs and merges responses.

See: [github.com/slds-lmu/ai-scaffolding/.../council-of-bots](https://github.com/slds-lmu/ai-scaffolding/tree/main/skills/council-of-bots)

---

<div v-if="false">

## Tracing

Observability for CLI agents — seeing what the LLM actually does.

- **Claude Code**: see [Simon Willison's writeup](https://simonwillison.net/2025/Jun/2/claude-trace/)
  Unfortunately broken in newer Claude versions.
- **Gemini CLI**: [telemetry docs](https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html)
  JSON dump available, but not very readable.

> **Future direction**: OpenTelemetry integration + dedicated visualizers
> would make agent tracing much more usable.

</div>

---

## Manuel Implementation of an Agent (Showing the ReAct Loop)

The idea is to create a simple agent in python that implements the ReAct loop, implementing the eamil-router skill.

**Prompt** given to Claude Code:
> Create a Python file (email-agent.py) that uses the OpenAI-compatible API (configured for openAI) to call LLMs and execute tools. The agent loads ~/.claude/skills/email-router/SKILL.md as system prompt and has a single tool read_context(filename) that reads .md files from the same skill directory. The ReAct loop runs until no more tool calls are made.

Full created code (minimal manuel tweeks needed) ~150 lines of code.
https://github.com/oduerr/skills_private/blob/main/mini-agents/email-agent.py

---

## Key components: definition of a (virtual) tool for the LLM

```python
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_context",
            "description": (
                "Read a context file from the email-router skill directory. "
                "Use this to load additional context before generating a reply. "
                "Available files: praktikantenamt.md, maba.md"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Filename to read, e.g. 'praktikantenamt.md'"
                    }
                },
                "required": ["filename"]
            }
        }
    }
]
```

---

## Key components (Prepare the prompt)

Composing the first message:
```python
# System-Prompt = SKILL.md 
skill_md = SKILL_MD.read_text() # "Du bist Oliver Dürrs persönlicher E-Mail-Assistent. "
history = [{"role": "system", "content": skill_md}]

mail_text = "Sehr geehrter Herr Dürr, 
 Hiermit bitte ich Sie, nachfolgend meines..."
user_message = f"Beantworte diese Mail:

{mail_text}"
history.append({"role": "user", "content": user_message})
```


---
## Key components (ReAct loop)

```python
while True:
        response = CLIENT.chat.completions.create(
          model=MODEL,
          messages=history,
          tools=TOOLS, # read_context
          tool_choice="auto" # auto-select tool or answer
        )

        message = response.choices[0].message # Returned by the LLM
        history.append(message)

        # No Tool-Call → done, final answer
        if not message.tool_calls:
            return message.content, history

        # Execute requested Tool-Call
        for tool_call in message.tool_calls:
            if tool_call.function.name == "read_context":
                filename = json.loads(tool_call.function.arguments)["filename"]
                result = read_context(filename)

                history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
```
--- 
## Practical Tips

- Skills are just Markdown files and easy to create.
- Talk to the Claude (ChatApplication) and ask it to create the skill for you. It will eat his own dogfood and use the skill creator skill.
- Skill are compatible with all CLIs (Claude Code, Gemini CLI, ...) and also run on openClaw :lobster:
- Use `claude-devtools` to inspect the output of the claude code.


---
layout: cover
---

# Thank You

**Oliver Dürr** 
