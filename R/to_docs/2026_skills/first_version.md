---
title: "Skills, CLI, and OpenClaw"
author: Oliver Dürr
format:
  revealjs:
    theme: simple
    slide-number: true
    code-copy: true
---

Prompt:
This is the outline of the talk I want to give. What do you think of it? You give your feedback, first we start and factcheck did I forgot something.

# Title: skills, cli, and openclaw

# Llms the work horses

Table with current llm for agents include frontier models cheaper ones from the big 3 and open source models for Dgx spark, Mac mini 32g and laptop. Als columns also include price read cached read and write and and one or two benchmarks for swe engineering and agents.

Sources
	- OpenAI pricing: https://openai.com/api/pricing/  ￼
	- Claude pricing: https://platform.claude.com/docs/en/about-claude/pricing  ￼
	- Gemini pricing overview: https://ai.google.dev/gemini-api/docs/pricing
	- SWE-bench leaderboard: https://www.swebench.com
    - Check if other benchmarks (AgentBench / GAIA)


# Break slide Modes of interaction 

## Level 1 Chat-interfaces, just talk

 table with ChatGPT, Gemini, Claude and one or two popular open source variants. Columns year and month of release. 

- in original form just conversation
- tool calls: user → LLM → copy to tool → paste result → LLM
- preferences in the prompt

## Level 2 do when you trigger them (plugins / AI Coding IDE)

Screenshot (will be provided by me)

Bullet list of GitHub [group by IDE/plugin add year and month of release] 
copilot, cursor, antigravity, windsurf, roo code (openscoure) and other open source variants,...

- tools: predefined tool set, but also unix commands, mcp servers
- preferences Agents.md

Tightly integrated in IDE, typically built for coding. 

Question: Do we need ide in the future? Cursor is becoming more like a tool to orchestrate agents.

## Level 2 do when you trigger them: Command Line Interfaces (CLI) 
Predecessors: github-cli (2023) very limited, open source variants (aider, openCode) 2024

2025 CLI kick off:
- Feb   Claude Code (Anthropic)
- Apr   Codex CLI (OpenAI)
- Jun   Gemini CLI (Google)

Screenshot (will be provided by me)

**tools**: Can run the terminal commands directly (naturally), mcp, skills 

**tools**: Extensions like Chrome Browser operated the system on your behalf.


Command line interfaces are feel more natural, when doing non-coding tasks (can also be used for coding tasks).
CLI are also answer of LLMs providers (Google, openai, Anthropic) to compete with Cursor and GitHub Copilot.
## The power of the shell

[Add image from the 1970's showing ancient computer terminal]

The power of the shell\footnote{Works in Linux, MacOS, Windows (PowerShell), since the 1970s.}:
- **The CLI is itself a command**, it can be called by other commands
- The CLI can be part of a unix pipeline.
- Nothing stops you from using the CLI to call other CLI.

## Level 3 Hosted Agents, can be triggered by external events

- n8n → workflow/event automation with agent features
- ...
- openClaw

Screenshot (will be provided by me, openClaw Mania)


- Agents waiting to be triggered 
    - Incomming E-Mail, Slack, Telegram, webhooks, etc.
    - Schedule a task, e.g. every day at 8:00 AM

# Tool calling and preferences
## The agentic loop

```{mermaid}
flowchart LR

    A[Your prompt] --> B[Gather context]
    B --> C[Take action]
    C --> D[Verify results]
    D --> E[Done]


    subgraph Agentic Loop
        B
        C
        D
    end

    U -.-> B
```

Diagram from <https://code.claude.com/docs/en/how-claude-code-works> for more details.

## Predefined tools (in the prompt)
Screenshot (will be provided by me, from Roo Code, old slides)
- IDE integrations started with this approach
- Have a set of predfined tools, requisterd completly in the initial promopt.
- Example Roo Code has 50K tokens for tools.
- Repeated tools calling and parsing output (React loop)

## MCP servers

- MCP servers are a way to extend the capabilities of the LLM, can be used to call tools.

## Skills
- Introduced early 2025 with Claude Code.
- Skills are a way to extend the capabilities of the CLI and adapt it to your needs. 
- Use Markdown files and can call other CLI tools:
- Including other skills, python, bash, etc.

Typical Skill structure:
```
pdf-skill/
├── SKILL.md (main instructions)
├── FORMS.md (form-filling guide)
├── REFERENCE.md (detailed API reference)
└── scripts/
    └── fill_form.py (utility script)
```

- Skills are quite token efficient by progressive progressive disclosure.
See also
https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview



## Demo Time (easy_chef)
Translates a recipe into a recipe into my preferred version with mise en place and list of ingredients.
- The Skill is public at https://github.com/oduerr/skills_public/tree/main/skills/easy_chef 
- Uses just SKILL.md

# Demo Time (htwg-mail), the second one will suprise you.
Queries a file-based database of my HTWG mails, operating a python script. 

- The Skill is in a private repository at https://github.com/oduerr/skills_private/skills/htwg-mail 
- Uses SKILL.md and a python script.



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

That clever bastards, did not use the python script directly but an sqlite query. Super human performance (at least compared to me).

# The power of the shell

## Remember the 70s?

```bash
echo "Hello, World" | wc -c
```
→ **Output**: 13

```bash
echo "Hello, World" | awk '{print $2}' | wc -c 
 ```
 → **Output**: 6

```bash
wc < file.txt
```

-- Speaker notes
wc -c is counting the number of characters in the input.
For token, one could use ttok

## The CLI is a command!

```
echo "What is 'Hello Guys' in Chinese and Italien" | gemini 
```

```bash
echo "What is 'Hello Guys' in Chinese and Italien" | gemini --model gemini-2.5-flash 
```
## The CLI is a command!

```bash
gemini -p "Is is a good recipe?" < schwaebischer_kartoffelsalat.md | claude -p "Übersetze ins Deutsche"
```

→ **Output**:
```
Dies ist ein ausgezeichnetes, technisch durchdachtes Rezept für einen traditionellen schwäbischen Kartoffelsalat. Sein Erfolg liegt in mehreren entscheidenden kulinarischen „Profi-Kniffen", die einen mittelmäßigen Salat von einem „schlotzigen" Meisterwerk unterscheiden:
Warum dieses Rezept funktioniert:
*   **Thermische Absorption:** Die Zwiebeln in heißer Brühe zu schwitzen ...
*   **Die Ölbarriere:** Das Öl **zuletzt** hinzuzufügen ist der wichtigste Schritt...
*   **Zwiebelbehandlung:** Das Blanchieren der Zwiebeln in der kochenden Brühe (Schritt 3)...
*   **Kartoffelwahl:** Die Angabe von *Linda* oder *Sieglinde* (festkochende Sorten) ... **ACHTUNG DAS STAND NICHT DRING!!**
```

**In the original recipe, the author did not mention the potato variety (Linda or Sieglinde).**





## A Skill can spawn other CLI
Council of Bots:
- Task you want to ask, gemnini, claude, openai for a particular answer. 
- Start 3 CLI and get the answer from each.
- Merge and consolidate the answers.

This can be done in a skill, which starts 3 CLI and get the answer from each and merge the answers. See <https://github.com/slds-lmu/ai-scaffolding/tree/main/skills/council-of-bots>











# Demo Time (tracing, TODO)
Tracing 
- claude see <https://simonwillison.net/2025/Jun/2/claude-trace/> Unfortunatly dose not work with the new claude.
- gemini see <https://google-gemini.github.io/gemini-cli/docs/cli/telemetry.html>
One can dump the json file to a log but not very easy to read. Maybe go with opentelemetry and visualisers lates.

