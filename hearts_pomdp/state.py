"""
Represents the state of the POMDP.
"""


import enum
import itertools
import random
from functools import cached_property, reduce
from typing import Any, Dict, FrozenSet, Optional

import pomdp_py
from pydantic import validator
from pydantic.dataclasses import dataclass


@enum.unique
class Suit(enum.IntEnum):
    """
    Represents a suit.
    """

    CLUBS = enum.auto()
    SPADES = enum.auto()
    DIAMONDS = enum.auto()
    HEARTS = enum.auto()


@enum.unique
class CardValue(enum.IntEnum):
    """
    Represents particular card values.
    """

    TWO = 2
    FOUR = 4
    SIX = 6
    EIGHT = 8
    TEN = 10
    QUEEN = 12
    ACE = 14


@dataclass
class Card:
    """
    Represents a specific card.

    Attributes:
        suit: The suit of the card.
        value: The value of the card.

    """

    suit: Suit
    value: CardValue

    def __eq__(self, other: "Card") -> bool:
        return self.suit == other.suit and self.value == other.value

    def __hash__(self) -> int:
        return hash(self.suit) ^ hash(self.value)


ALL_CARDS = frozenset(
    {Card(s, v) for s, v in itertools.product(Suit, CardValue)}
)
"""
The set of all cards in the game.
"""


@dataclass(frozen=True)
class State(pomdp_py.State):
    """
    Represents the state of the game.

    Attributes:
        player_1_hand: The contents of player one's hand.
        player_2_hand: The contents of player two's hand.
        held_out_cards: The two cards that were not dealt to any hand.
        is_first_trick: Whether this is the first trick.
        player_1_play: Player one's most recent play. Can be None if a nop
            action was taken.
        player_2_play: Player two's most recent play. Can be None if a nop
            action was taken.

    """

    player_1_hand: FrozenSet[Card]
    player_2_hand: FrozenSet[Card]
    held_out_cards: FrozenSet[Card]
    is_first_trick: bool
    player_1_play: Optional[Card]
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

    @validator("player_2_play")
    def plays_are_different(
        cls, player_2_play: Optional[Card], values: Dict[str, Any]
    ) -> Optional[Card]:
        assert (
            player_2_play is None or player_2_play != values["player_1_play"]
        ), "Players must play different cards."
        return player_2_play

    def __eq__(self, other: "State") -> bool:
        return (
            self.player_1_hand == other.player_1_hand
            and self.player_2_hand == other.player_2_hand
            and self.held_out_cards == other.held_out_cards
            and self.is_first_trick == other.is_first_trick
            and self.player_1_play == other.player_1_play
            and self.player_2_play == other.player_2_play
        )

    def __hash__(self) -> int:
        factors = (
            self.player_1_hand,
            self.player_2_hand,
            self.held_out_cards,
            self.is_first_trick,
            self.player_1_play,
            self.player_2_play,
        )
        hashes = map(hash, factors)
        return reduce(lambda a, b: a ^ b, hashes, 0)

    @cached_property
    def played_cards(self) -> FrozenSet[Card]:
        """
        Returns:
            The set of all cards that have been played so far.

        """
        return (
            ALL_CARDS
            - self.__player_1_hand
            - self.__player_2_hand
            - self.__held_out_cards
        )


def random_initial_state() -> State:
    """
    Generates a random valid initial state for the game.

    Returns:
        The initial state that it generated.

    """
    # Simulate the cards being dealt.
    deck = set(ALL_CARDS)
    player_1_hand = frozenset(random.sample(deck, 13))
    deck -= player_1_hand
    player_2_hand = frozenset(random.sample(deck, 13))
    deck -= player_2_hand
    held_out = frozenset(deck)

    return State(
        player_1_hand=player_1_hand,
        player_2_hand=player_2_hand,
        held_out_cards=held_out,
        is_first_trick=True,
        player_1_play=None,
        player_2_play=None,
    )
