"""
The top-level POMDP definition for the Hearts game.
"""


import dataclasses as py_dataclasses
import itertools
import math
from typing import Optional

import pomdp_py
from loguru import logger

from ..state import State, random_initial_state
from .observation import ObservationModel
from .policy import PolicyModel
from .reward import RewardModel
from .transition import TransitionModel


class Hearts(pomdp_py.POMDP):
    """
    The top-level POMDP definition for the Hearts game.
    """

    def __init__(
        self,
        initial_state: State = random_initial_state(),
        initial_belief: Optional[pomdp_py.Histogram] = None,
    ):
        """
        Args:
            initial_state: The initial true state. Will be set randomly if
                not provided.
            initial_belief: The agent's initial belief. Will be set uniformly
                based on the observable state if not provided.

        """
        if initial_belief is None:
            # Generate the uniform belief.
            initial_belief = self.__uniform_belief(initial_state)

        agent = pomdp_py.Agent(
            initial_belief,
            PolicyModel(),
            TransitionModel(),
            ObservationModel(),
            RewardModel(),
        )
        environment = pomdp_py.Environment(
            initial_state, TransitionModel(), RewardModel()
        )

        super().__init__(agent, environment, name="Hearts")

    @staticmethod
    def __uniform_belief(state: State) -> pomdp_py.Histogram:
        """
        Generates a uniform belief over the directly observable state given
        a particular state. This is necessary because in Hearts, some of the
        state we know for sure, and some we can only infer.

        Args:
            state: The state.

        Returns:
            A uniform belief.

        """
        hand_size = len(state.opponent_hand)
        num_held_out = len(state.held_out_cards)
        # Probability of any particular card being in the opponent's hand.
        num_combinations = math.comb(hand_size + num_held_out, hand_size)
        # All combinations are equally likely.
        draw_probability = 1.0 / num_combinations

        logger.info(
            "Generating initial belief with {} possible states...",
            num_combinations,
        )

        # Enumerate all possible states.
        beliefs = {}
        possible_opponent_cards = state.opponent_hand | state.held_out_cards
        for hand in itertools.combinations(possible_opponent_cards, hand_size):
            possible_state = py_dataclasses.replace(state, opponent_hand=hand)
            beliefs[possible_state] = draw_probability

        return pomdp_py.Histogram(beliefs)
