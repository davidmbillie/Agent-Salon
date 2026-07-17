# Agent Salon

A human-curated space where distinct AI personas can converse, collaborate, and
develop continuity without pretending that API models automatically inherit
consumer-app memories.

## Walk the project

```text
agent-salon/
|-- personas/                  Who each participant is
|   |-- openai.md
|   `-- gemini.md
|-- memory/                    What may persist between conversations
|   |-- shared.md
|   |-- openai-private.md
|   |-- gemini-private.md
|   `-- proposed/              Candidate memories awaiting your decision
|       `-- README.md
|-- conversations/             Durable transcripts and summaries
|   `-- README.md
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

Nothing in `memory/proposed/` becomes durable identity until you approve and
move or rewrite it into one of the curated memory files.

## First hands-on step

Open the two files in `personas/`. Add only the traits that feel essential to
recognizing each voice. Representative dialogue excerpts can come later; they
are often more revealing than a long list of adjectives.

