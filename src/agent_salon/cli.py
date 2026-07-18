from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from agent_salon.bootstrap import initialize_data
from agent_salon.config import SalonConfig, load_config, validate_config
from agent_salon.context import build_instructions
from agent_salon.curator_input import read_text_file
from agent_salon.domain import Conversation, Turn
from agent_salon.orchestrator import RelayInterrupted, relay
from agent_salon.providers import GeminiProvider, OpenAIProvider
from agent_salon.transcript import load_conversation, next_provider, save_conversation


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        project_dir = Path(args.project_dir)
        if args.command == "init-data":
            destination = initialize_data(project_dir, Path(args.destination))
            print(f"Created private Agent Salon data at {destination}")
            print("Add OPENAI_API_KEY and GEMINI_API_KEY to the project's ignored .env file.")
            return 0

        config = load_config(project_dir)
        errors = validate_config(config)
        if errors:
            for error in errors:
                print(f"error: {error}", file=sys.stderr)
            return 2
        if args.command == "validate":
            print(f"Configuration is valid. Private data: {config.data_dir}")
            return 0
        if args.command == "relay":
            message = _relay_message(args.message, args.message_file)
            return asyncio.run(_run_relay(config, message))
        conversation, lineage = load_conversation(Path(args.source))
        continuation = _optional_message(args.message, args.message_file)
        if continuation:
            conversation.turns.append(Turn(speaker="Curator", text=continuation))
        return asyncio.run(
            _run_relay(
                config,
                conversation.opening_message,
                conversation=conversation,
                resumed_from=lineage,
            )
        )
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


async def _run_relay(
    config: SalonConfig,
    message: str,
    conversation: Conversation | None = None,
    resumed_from: str | None = None,
) -> int:
    by_name = {
        "openai": OpenAIProvider(config.openai.model),
        "gemini": GeminiProvider(config.gemini.model),
    }
    first = next_provider(conversation, config.start_with) if conversation else config.start_with
    other = "gemini" if first == "openai" else "openai"
    participants = (by_name[first], by_name[other])
    if conversation:
        print(
            f"Resuming {len(conversation.turns)} existing turns. "
            f"{participants[0].name} speaks next."
        )
    instructions = {
        "OpenAI": build_instructions(config, config.openai),
        "Gemini": build_instructions(config, config.gemini),
    }
    try:
        conversation = await relay(
            opening_message=message,
            participants=participants,
            instructions=instructions,
            max_turns=config.max_turns,
            on_turn=_print_turn,
            on_relay_complete=_prompt_curator if config.pause_between_relays else None,
            conversation=conversation,
        )
    except RelayInterrupted as interrupted:
        if interrupted.conversation.turns:
            session_dir = save_conversation(
                config.data_dir,
                interrupted.conversation,
                participants,
                error=interrupted.error,
                resumed_from=resumed_from,
            )
            print(f"\nSaved partial private transcript to {session_dir}")
        print(
            f"\n{interrupted.error.provider} could not continue: "
            f"{interrupted.error.message}",
            file=sys.stderr,
        )
        return 1
    session_dir = save_conversation(
        config.data_dir, conversation, participants, resumed_from=resumed_from
    )
    print(f"\nSaved private transcript to {session_dir}")
    return 0


def _print_turn(turn: Turn) -> None:
    print(f"\n{turn.speaker}:\n{turn.text}")


def _prompt_curator(_conversation) -> str | None:
    try:
        response = input("\nCurator ([Enter] or /continue, /quit): ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return None
    if response.lower() == "/quit":
        return None
    if response.lower() == "/continue":
        return ""
    return response


def _relay_message(message: str | None, message_file: str | None) -> str:
    if message and message_file:
        raise ValueError("Use either a message or --file, not both")
    if message_file:
        return read_text_file(Path(message_file))
    if message:
        return message
    raise ValueError("Relay requires a message or --file")


def _optional_message(message: str | None, message_file: str | None) -> str | None:
    if message and message_file:
        raise ValueError("Use either --message or --message-file, not both")
    return read_text_file(Path(message_file)) if message_file else message


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="salon")
    parser.add_argument("--project-dir", default=str(Path.cwd()))
    subcommands = parser.add_subparsers(dest="command", required=True)
    init_parser = subcommands.add_parser("init-data", help="create a private data directory")
    init_parser.add_argument(
        "destination",
        nargs="?",
        default="../agent-salon-data",
        help="private data path, relative to the project (default: ../agent-salon-data)",
    )
    subcommands.add_parser("validate", help="validate configuration and private data paths")
    relay_parser = subcommands.add_parser("relay", help="start a bounded OpenAI/Gemini relay")
    relay_parser.add_argument("message", nargs="?", help="the curator's opening message")
    relay_parser.add_argument(
        "--file",
        dest="message_file",
        help="read the curator's opening message from a UTF-8 text file",
    )
    resume_parser = subcommands.add_parser("resume", help="continue a saved conversation")
    resume_parser.add_argument("source", help="session directory, transcript.md, or conversation.yaml")
    resume_parser.add_argument(
        "--message",
        help="append a Curator turn before the next provider speaks",
    )
    resume_parser.add_argument(
        "--message-file",
        help="read a Curator continuation from a UTF-8 text file",
    )
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
