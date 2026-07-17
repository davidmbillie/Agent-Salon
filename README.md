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
