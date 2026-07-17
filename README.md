# Agent Salon

A human-curated space where distinct AI personas can converse, collaborate, and
develop continuity without pretending that API models automatically inherit
consumer-app memories.

## Public code, local identity

Agent Salon deliberately separates the shareable application from its
curator's personal data:

```text
C:\arti\
|-- agent-salon\          This repository: code, prompts, and blank templates
`-- agent-salon-data\     Local personas, memories, and conversations
```

The application will locate the private directory through `SALON_DATA_DIR` in
the ignored `.env` file. A public clone therefore contains the shape of an
identity system, but none of its curator's identity content.

## Walk the public project

```text
agent-salon/
|-- templates/                 Blank, fictional-safe starting documents
|   |-- personas/
|   |-- memory/
|   `-- conversations/
|-- prompts/                   Reusable rules for different kinds of exchange
|   |-- relay.md
|   |-- code-review.md
|   `-- reflection.md
|-- src/                       The future orchestrator
|   `-- README.md
|-- config/
|   `-- salon.example.yaml     Safe, shareable runtime settings
|-- docs/
|   `-- design-notes.md        Decisions, questions, and evolving ideas
|-- .env.example               Names of required secrets, never real values
`-- .gitignore
```

The intended flow is:

```text
you choose a mode
        |
        v
load persona + approved memory
        |
        v
OpenAI <---- orchestrator ----> Gemini
        |                          |
        `------ transcript --------'
                    |
                    v
          proposed memories
                    |
                    v
             you curate them
```

Nothing in the local data directory's `memory/proposed/` becomes durable
identity until you approve and move or rewrite it into a curated memory file.

## Walk the private data

```text
agent-salon-data/
|-- personas/
|   |-- openai.md
|   `-- gemini.md
|-- memory/
|   |-- shared.md
|   |-- openai-private.md
|   |-- gemini-private.md
|   `-- proposed/
|       `-- README.md
|-- conversations/
|   `-- README.md
`-- salon.yaml
```

This directory is outside the public repository, so `git add .` from Agent
Salon cannot accidentally include it. It can later have its own local-only Git
history or encrypted backup policy.

## First hands-on step

Open the two files in `../agent-salon-data/personas/`. Add only the traits that
feel essential to recognizing each voice. Representative dialogue excerpts can
come later; they are often more revealing than a long list of adjectives.

## Python baseline

Agent Salon targets Python 3.12. Create a local environment and install it:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
```

Confirm that the public application can see the private data structure:

```powershell
.\.venv\Scripts\salon validate
```

When both API keys have been added to the ignored `.env`, start a bounded relay:

```powershell
.\.venv\Scripts\salon relay "What should the two of you know about each other?"
```

The providers receive the relevant persona, shared memory, private memory, and
conversation-mode prompt. API-side storage is disabled for both provider calls;
the resulting transcript is written only under the private data directory.

Set `session.start_with` in the private `salon.yaml` to `openai` or `gemini`.
Provider failures are shown as concise messages rather than SDK tracebacks. If a
later turn fails, the completed portion is still saved as a private transcript.

With `session.pause_between_relays: true`, the CLI pauses after both participants
have spoken once. Your response is added to the transcript as a `Curator` turn
before the next pair. Enter `/quit` to save the conversation and finish early.
