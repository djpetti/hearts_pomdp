"""
A policy model for the game.
"""


import random
from typing import Any, Set

import pomdp_py

from ..action import Action
from ..state import ALL_CARDS, State


class PolicyModel(pomdp_py.RandomRollout):
    """
    A policy model for the game.
    """

    def sample(self, state: State, **kwargs: Any) -> Action:
        """
        Samples the next action randomly from a uniform distribution.

        Args:
            state: The current state.
            **kwargs: Will be ignored.

        Returns:
            The next action to take.

        """
        # It would work fine to sample from the entire action space here.
        # However, since it's trivial, we might as well optimize by sampling
        # from only the cards in our hand.
        card = random.sample(state.player_1_hand, 1)[0]
        return Action(play=card)

    def get_all_actions(self, *args: Any, **kwargs: Any) -> Set[Action]:
        """
        Args:
            *args: Will be ignored.
            **kwargs: Will be ignored.

        Returns:
            All possible actions in the POMDP.

        """
        actions = {Action(play=c) for c in ALL_CARDS}
        # Add the nop action.
        actions.add(Action(play=None))

        return actions
