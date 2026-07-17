from collections.abc import Callable

from agent_salon.domain import Conversation, Provider, ProviderError, Turn, TurnRequest


class RelayInterrupted(Exception):
    def __init__(self, conversation: Conversation, error: ProviderError) -> None:
        super().__init__(error.message)
        self.conversation = conversation
        self.error = error


async def relay(
    opening_message: str,
    participants: tuple[Provider, Provider],
    instructions: dict[str, str],
    max_turns: int,
    on_turn: Callable[[Turn], None] | None = None,
    on_relay_complete: Callable[[Conversation], str | None] | None = None,
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
        try:
            response = await provider.respond(request)
        except ProviderError as error:
            raise RelayInterrupted(conversation, error) from error
        turn = Turn(speaker=response.provider, text=response.text)
        conversation.turns.append(turn)
        if on_turn:
            on_turn(turn)
        relay_is_complete = (index + 1) % len(participants) == 0
        more_provider_turns_remain = index + 1 < max_turns
        if relay_is_complete and more_provider_turns_remain and on_relay_complete:
            curator_input = on_relay_complete(conversation)
            if curator_input is None:
                break
            conversation.turns.append(Turn(speaker="Curator", text=curator_input))
    return conversation
