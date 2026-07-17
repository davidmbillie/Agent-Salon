# Public templates

These files define the expected shape of a private Agent Salon data directory.
They must remain blank or use obviously fictional example content.

Real personas, memories, and conversations belong in the directory identified
by `SALON_DATA_DIR`, never here.

`salon init-data` copies these templates into a new private data directory.

## Persona examples

The `personas/examples/` gallery contains fictional, non-personal starting points
with contrasting styles:

- **Rowan, the Cartographer:** calm exploration and uncertainty mapping.
- **Sol, the Workshop Host:** energetic prototyping and learning by making.
- **Vesper, the Constructive Critic:** rigorous but humane adversarial review.

Copy, combine, or rewrite one into `personas/openai.md` or
`personas/gemini.md`. The examples are demonstrations, not required identities;
the two runtime files remain blank so setup never silently chooses a personality
for the curator.
