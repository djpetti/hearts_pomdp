"""
Custom particle handling for Hearts.
"""


import dataclasses as py_dataclasses
import random

from .models.pomdp import Hearts
from .state import State


def random_particle(model: Hearts) -> State:
    """
    Generates a random particle based on the current model state.

    Args:
        model: The model.

    Returns:
        The particle that it generated.

    """
    # Determine the set of all cards that the agent knows could be in its
    # opponent's hand.
    state = model.env.state
    possible_player_2_cards = state.player_2_hand | state.held_out_cards
    player_2_hand = random.sample(
        possible_player_2_cards, len(state.player_2_hand)
    )

    return py_dataclasses.replace(
        state, player_2_hand=frozenset(player_2_hand)
    )