"""
Implements the observation model.
"""


import math
import random
from typing import Any, FrozenSet

import pomdp_py

from ..action import Action
from ..observation import Observation
from ..state import Card, State


class ObservationModel(pomdp_py.ObservationModel):
    """
    Implements the observation model.
    """

    @staticmethod
    def __possible_opponent_hand(state: State) -> FrozenSet[Card]:
        """
        Calculates the possible cards that can make up the opponent's hand.

        Args:
            state: The known state.

        Returns:
            The possible cards in the opponent's hand.

        """
        # By definition, we can eliminate every card from the opponents hand
        # except the ones that are actually there and the two that are held out.
        return state.player_2_hand | state.held_out_cards

    def probability(
        self,
        observation: Observation,
        next_state: State,
        action: Action,
        **kwargs: Any
    ) -> float:
        """
        Calculates `P(o | s', a)`.

        Args:
            observation: The observation.
            next_state: The next state.
            action: The action.
            **kwargs: Will be ignored.

        Returns:
            The probability of getting this observation given we took the
            action and are moving to the next state.

        """
        # Check the deterministic parts and see if they match.
        if (
            next_state.player_1_hand != observation.player_1_hand
            or next_state.player_2_play != observation.player_2_play
        ):
            return 0.0

        # Figure out which cards could possibly be in the opponent's hand.
        possible_player_2_hand = self.__possible_opponent_hand(next_state)
        if not observation.player_2_hand <= possible_player_2_hand:
            # This player 2 hand is impossible.
            return 0.0

        # Probability is based on the number of possible hands of this size that
        # we can draw.
        return 1.0 / math.comb(
            len(possible_player_2_hand), len(observation.player_2_hand)
        )

    def sample(
        self, next_state: State, action: Action, **kwargs: Any
    ) -> Observation:
        """
        Returns an observation randomly sampled according to this model.

        Args:
            next_state: The next state.
            action: The action we took.
            **kwargs: Will be ignored.

        Returns:
            The sampled observation.

        """
        # Sample the opponent's hand.
        possible_cards = self.__possible_opponent_hand(next_state)
        player_2_hand = random.sample(
            # We can see how many cards the opponent has.
            possible_cards,
            len(next_state.player_2_hand),
        )

        # Everything else is deterministic.
        return Observation(
            player_1_hand=next_state.player_1_hand,
            player_2_hand=frozenset(player_2_hand),
            player_2_play=next_state.player_2_play,
        )
