"""
Represents the observations the agent can receive.
"""


from typing import Any, Dict, FrozenSet, Optional

import pomdp_py
from pydantic import validator
from pydantic.dataclasses import dataclass

from .state import Card


@dataclass(frozen=True)
class Observation(pomdp_py.Observation):
    """
    Represents the observations the agent can receive.

    Attributes:
        player_1_hand: The contents of player one's hand.
        player_2_hand: The contents of player two's hand.
        player_2_play: Player two's most recent play. Can be None if a nop
            action was taken.

    """

    player_1_hand: FrozenSet[Card]
    player_2_hand: FrozenSet[Card]
    player_2_play: Optional[Card]

    @validator("player_1_hand")
    def hand_1_is_not_too_big(cls, hand: FrozenSet[Card]) -> FrozenSet[Card]:
        assert len(hand) <= 13, "Cannot have more than 13 cards."
        return hand

    @validator("player_2_hand")
    def hand_2_is_not_too_big(cls, hand: FrozenSet[Card]) -> FrozenSet[Card]:
        assert len(hand) <= 13, "Cannot have more than 13 cards."
        return hand

    @validator("player_2_hand")
    def hands_are_disjoint(
        cls, player_2_hand: FrozenSet[Card], values: Dict[str, Any]
    ) -> FrozenSet[Card]:
        assert not (
            player_2_hand & values["player_1_hand"]
        ), "Hands cannot have the same card."
        return player_2_hand

    def __eq__(self, other: "Observation") -> bool:
        return (
            self.player_1_hand == other.player_1_hand
            and self.player_2_hand == other.player_2_hand
            and self.player_2_play == other.player_2_play
        )

    def __hash__(self) -> int:
        return (
            hash(self.player_1_hand)
            ^ hash(self.player_2_hand)
            ^ hash(self.player_2_play)
        )
