"""
Represents the state of the POMDP.
"""


import enum
import itertools
import random
from functools import cached_property
from typing import Any, Dict, FrozenSet, Iterable, Optional

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


@dataclass(frozen=True)
class Card:
    """
    Represents a specific card.

    Attributes:
        suit: The suit of the card.
        value: The value of the card.

    """

    suit: Suit
    value: CardValue

    @cached_property
    def is_penalty(self) -> bool:
        """
        Returns:
            True if the card is a penalty card.

        """
        return self.suit == Suit.HEARTS or (
            self == Card(suit=Suit.SPADES, value=CardValue.QUEEN)
        )


ALL_CARDS = frozenset(
    {Card(s, v) for s, v in itertools.product(Suit, CardValue)}
)
"""
The set of all cards in the game.
"""


@dataclass(frozen=True)
class ObservableStateMixin:
    """
    Encapsulates the portions of the state that are directly observable.

    Attributes:
        agent_hand: The contents of the agent's hand.
        agent_play: The agent's most recent play. Can be None if a nop
            action was taken.
        opponent_play: The opponent's most recent play. Can be None if a nop
            action was taken.
        opponent_partial_play: The opponent's play from a partial trick. This
            can arise in a case where the opponent goes first the next trick
            and this is handled in the transition for the previous trick.

        is_first_trick: Whether this is the first trick.
        agent_goes_first: Whether the agent is going first in the next trick.
        hearts_broken: Whether hearts have been broken.
        agent_took_all_penalties: Whether the agent has taken all penalty cards
            so far.
        opponent_took_all_penalties: Whether the opponent has taken all penalty
            cards so far.

    """

    agent_hand: FrozenSet[Card]
    agent_play: Optional[Card]
    opponent_play: Optional[Card]
    opponent_partial_play: Optional[Card]

    is_first_trick: bool
    agent_goes_first: bool
    hearts_broken: bool
    agent_took_all_penalties: bool
    opponent_took_all_penalties: bool

    @validator("agent_hand")
    def hand_1_is_not_too_big(cls, hand: FrozenSet[Card]) -> FrozenSet[Card]:
        assert len(hand) <= 13, "Cannot have more than 13 cards."
        return hand

    @validator("opponent_play")
    def plays_are_different(
        cls, player_2_play: Optional[Card], values: Dict[str, Any]
    ) -> Optional[Card]:
        assert (
            player_2_play is None or player_2_play != values["agent_play"]
        ), "Players must play different cards."
        return player_2_play

    @property
    def lead_play(self) -> Optional[Card]:
        """
        Gets the card played by the first player in the most recent trick.

        Returns:
            The card, or None if it was a nop.

        """
        if self.agent_goes_first:
            return self.agent_play
        return self.opponent_play

    @property
    def second_play(self) -> Optional[Card]:
        """
        Gets the card played by the second player in the most recent trick.

        Returns:
            The card, or None if it was a nop.

        """
        if self.agent_goes_first:
            return self.opponent_play
        return self.agent_play


@dataclass(frozen=True)
class State(pomdp_py.State, ObservableStateMixin):
    """
    Represents the state of the game.

    Attributes:
        opponent_hand: The contents of the opponent's hand.
        held_out_cards: The two cards that were not dealt to any hand.

    """

    opponent_hand: FrozenSet[Card]
    held_out_cards: FrozenSet[Card]

    @validator("opponent_hand")
    def hand_2_is_not_too_big(cls, hand: FrozenSet[Card]) -> FrozenSet[Card]:
        assert len(hand) <= 13, "Cannot have more than 13 cards."
        return hand

    @validator("opponent_hand")
    def hands_are_disjoint(
        cls, player_2_hand: FrozenSet[Card], values: Dict[str, Any]
    ) -> FrozenSet[Card]:
        assert not (
            player_2_hand & values["agent_hand"]
        ), "Hands cannot have the same card."
        return player_2_hand

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

    @property
    def first_player_hand(self) -> FrozenSet[Card]:
        """
        Gets the hand of the first player in the most recent trick.

        Returns:
            The hand.

        """
        if self.agent_goes_first:
            return self.agent_hand
        return self.opponent_hand

    @property
    def second_player_hand(self) -> FrozenSet[Card]:
        """
        Gets the hand of the second player in the most recent trick.

        Returns:
            The hand.

        """
        if self.agent_goes_first:
            return self.opponent_hand
        return self.agent_hand


_TWO_OF_CLUBS = Card(suit=Suit.CLUBS, value=CardValue.TWO)


def lowest_club(hand: Iterable[Card]) -> Optional[Card]:
    """
    Finds the lowest club in a hand.

    Args:
        hand: The hand to look in.

    Returns:
        The lowest club, or None if there are no clubs.

    """
    # Extract and sort the clubs.
    all_clubs = [c for c in hand if c.suit == Suit.CLUBS]
    all_clubs.sort(key=lambda c: c.value)

    if len(all_clubs) == 0:
        # No clubs.
        return None
    else:
        return all_clubs[0]


def random_initial_state() -> State:
    """
    Generates a random valid initial state for the game.

    Returns:
        The initial state that it generated.

    """
    # Simulate the cards being dealt.
    deck = set(ALL_CARDS)
    agent_hand = frozenset(random.sample(deck, 13))
    deck -= agent_hand
    opponent_hand = frozenset(random.sample(deck, 13))
    deck -= opponent_hand
    held_out = frozenset(deck)

    # Determine which player goes first.
    agent_lowest_club = lowest_club(agent_hand)
    opponent_lowest_club = lowest_club(opponent_hand)
    agent_goes_first = True
    if agent_lowest_club is None:
        agent_goes_first = False
    elif opponent_lowest_club is not None:
        agent_goes_first = agent_lowest_club.value < opponent_lowest_club.value

    opponent_partial_play = None
    if not agent_goes_first:
        # In this case, it expects us to perform the first opponent play.
        opponent_partial_play = opponent_lowest_club
        opponent_hand -= {opponent_lowest_club}

    return State(
        agent_hand=agent_hand,
        opponent_hand=opponent_hand,
        held_out_cards=held_out,
        agent_play=None,
        opponent_play=None,
        opponent_partial_play=opponent_partial_play,
        is_first_trick=True,
        agent_goes_first=agent_goes_first,
        hearts_broken=False,
        agent_took_all_penalties=True,
        opponent_took_all_penalties=True,
    )
