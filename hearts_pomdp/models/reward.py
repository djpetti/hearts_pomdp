"""
Reward model for the game.
"""


from typing import AbstractSet, Any

import pomdp_py

from ..action import Action
from ..state import Card, CardValue, State, Suit
from ..utils import agent_won_trick


class RewardModel(pomdp_py.RewardModel):
    """
    A reward model for the game.
    """

    _QUEEN_OF_SPADES = Card(suit=Suit.SPADES, value=CardValue.QUEEN)

    _HEART_REWARD = -1.0
    """
    Reward for winning a heart.
    """
    _QUEEN_REWARD = -13.0
    """
    Reward for taking the queen of spades.
    """
    _NOP_REWARD = -15.0
    """
    Cost associated with a nop. We make this large, because the agent should
    always be able to make a play that does not result in a nop.
    """

    @classmethod
    def __trick_reward(cls, cards: AbstractSet[Card]) -> float:
        """
        Calculates the reward for winning a particular trick.

        Args:
            cards: The cards in the trick.

        Returns:
            The reward.

        """
        win_reward = 0.0

        # Hearts count for a point each.
        heart_cards = {c for c in cards if c.suit == Suit.HEARTS}
        win_reward += len(heart_cards) * cls._HEART_REWARD

        # Queen of spades counts for extra.
        if cls._QUEEN_OF_SPADES in cards:
            win_reward += cls._QUEEN_REWARD

        return win_reward

    def sample(
        self, state: State, action: Action, next_state: State, **kwargs: Any
    ) -> float:
        """
        Gets the corresponding reward for a particular state transition. This
        can be stochastic, but in this case, it is deterministic.

        Args:
            state: The initial state.
            action: The action taken.
            next_state: The resulting state.
            **kwargs: Will be ignored.

        Returns:
            The associated reward.

        """
        if next_state.agent_play is None or next_state.opponent_play is None:
            # Nop.
            return self._NOP_REWARD

        win_reward = self.__trick_reward(
            {next_state.lead_play, next_state.second_play}
        )
        if agent_won_trick(next_state):
            return win_reward
        else:
            return 0.0
