from collections.abc import Callable

from agent_salon.domain import Conversation, Provider, Turn, TurnRequest


async def relay(
    opening_message: str,
    participants: tuple[Provider, Provider],
    instructions: dict[str, str],
    max_turns: int,
    on_turn: Callable[[Turn], None] | None = None,
) -> Conversation:
    if max_turns < 1:
        raise ValueError("max_turns must be at least 1")

    conversation = Conversation(opening_message=opening_message)
    for index in range(max_turns):
        provider = participants[index % len(participants)]
        request = TurnRequest(
            opening_message=opening_message,
            history=tuple(conversation.turns),
            instructions=instructions[provider.name],
        )
        response = await provider.respond(request)
        turn = Turn(speaker=response.provider, text=response.text)
        conversation.turns.append(turn)
        if on_turn:
            on_turn(turn)
    return conversation
