# Orchestrator source

Implementation will live here once the language and first interaction mode are
chosen. Its responsibilities will be deliberately narrow:

1. load persona and approved-memory context;
2. call each provider through a small adapter;
3. enforce turn, time, and cost limits;
4. save transcripts and summaries;
5. place memory suggestions in the proposal inbox;
6. require human approval before changing durable memory.

