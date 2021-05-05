"""
Custom particle handling for Hearts.
"""


import dataclasses as py_dataclasses
import random
from typing import Any, Optional

import pomdp_py

from .models.pomdp import Hearts
from .state import State


class HeartsParticles(pomdp_py.Particles):
    """
    An extension to the basic `Particles` class that is specific to the
    Hearts game.
    """

    def __init__(self, *args: Any, model: Hearts, **kwargs: Any):
        """
        Args:
            *args: Will be forwarded to the superclass.
            model: The specific model that these particles represent
                beliefs for.
            **kwargs: Will be forwarded to the superclass.

        """
        super().__init__(*args, **kwargs)

        self.__model = model

    def random(self) -> Optional[State]:
        """
        Randomly generates a particle given what we know about the state of
        the game.

        Returns:
            The particle that it generated.

        """
        # Determine the set of all cards that the agent knows could be in its
        # opponent's hand.
        state = self.__model.env.state
        possible_player_2_cards = state.player_2_hand | state.held_out_cards
        player_2_hand = random.sample(
            possible_player_2_cards, len(state.player_2_hand)
        )

        return py_dataclasses.replace(
            state, player_2_hand=frozenset(player_2_hand)
        )
