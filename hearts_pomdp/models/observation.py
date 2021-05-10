"""
Implements the observation model.
"""


from typing import Any

import pomdp_py

from ..action import Action
from ..observation import Observation
from ..state import State


class ObservationModel(pomdp_py.ObservationModel):
    """
    Implements the observation model.
    """

    @staticmethod
    def __observation_from_state(state: State) -> Observation:
        """
        Creates an observation from the given state.

        Args:
            state: The state to use.

        Returns:
            The corresponding observation.

        """
        return Observation(
            agent_hand=state.agent_hand,
            agent_play=state.agent_play,
            opponent_play=state.opponent_play,
            opponent_partial_play=state.opponent_partial_play,
            is_first_trick=state.is_first_trick,
            agent_goes_first=state.agent_goes_first,
            hearts_broken=state.hearts_broken,
            agent_took_all_penalties=state.agent_took_all_penalties,
            opponent_took_all_penalties=state.opponent_took_all_penalties,
            opponent_hand_size=len(state.opponent_hand),
        )

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
        # Assuming the state generates this observation, we're good.
        if self.__observation_from_state(next_state) == observation:
            return 1.0
        return 0.0

    def sample(
        self, next_state: State, action: Action, **kwargs: Any
    ) -> Observation:
        """
        Returns an observation "randomly" sampled according to this model. In
        practice, all our observations are deterministic, but there are some
        parts of the state that we simply can't observe.

        Args:
            next_state: The next state.
            action: The action we took.
            **kwargs: Will be ignored.

        Returns:
            The sampled observation.

        """
        return self.__observation_from_state(next_state)
