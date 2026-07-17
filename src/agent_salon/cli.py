from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from agent_salon.config import SalonConfig, load_config, validate_config
from agent_salon.context import build_instructions
from agent_salon.domain import Turn
from agent_salon.orchestrator import RelayInterrupted, relay
from agent_salon.providers import GeminiProvider, OpenAIProvider
from agent_salon.transcript import save_conversation


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        config = load_config(Path(args.project_dir))
        errors = validate_config(config)
        if errors:
            for error in errors:
                print(f"error: {error}", file=sys.stderr)
            return 2
        if args.command == "validate":
            print(f"Configuration is valid. Private data: {config.data_dir}")
            return 0
        return asyncio.run(_run_relay(config, args.message))
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


async def _run_relay(config: SalonConfig, message: str) -> int:
    by_name = {
        "openai": OpenAIProvider(config.openai.model),
        "gemini": GeminiProvider(config.gemini.model),
    }
    other = "gemini" if config.start_with == "openai" else "openai"
    participants = (by_name[config.start_with], by_name[other])
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
        )
    except RelayInterrupted as interrupted:
        if interrupted.conversation.turns:
            session_dir = save_conversation(
                config.data_dir,
                interrupted.conversation,
                participants,
                error=interrupted.error,
            )
            print(f"\nSaved partial private transcript to {session_dir}")
        print(
            f"\n{interrupted.error.provider} could not continue: "
            f"{interrupted.error.message}",
            file=sys.stderr,
        )
        return 1
    session_dir = save_conversation(config.data_dir, conversation, participants)
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


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="salon")
    parser.add_argument("--project-dir", default=str(Path.cwd()))
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("validate", help="validate configuration and private data paths")
    relay_parser = subcommands.add_parser("relay", help="start a bounded OpenAI/Gemini relay")
    relay_parser.add_argument("message", help="the curator's opening message")
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
