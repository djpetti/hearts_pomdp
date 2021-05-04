"""
Reward model for the game.
"""


from typing import AbstractSet, Any

import pomdp_py

from ..action import Action
from ..state import Card, CardValue, State, Suit


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
    _NOP_REWARD = -5.0
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
        if (
            next_state.player_1_play is None
            or next_state.player_2_play is None
        ):
            # Nop.
            return self._NOP_REWARD

        p1_card = next_state.player_1_play
        p2_card = next_state.player_2_play

        win_reward = self.__trick_reward({p1_card, p2_card})

        if p1_card.suit == p2_card.suit:
            # Higher value wins the trick.
            if p1_card.value.value > p2_card.value.value:
                return win_reward
        else:
            # The lead suit wins the trick.
            return win_reward

        # We did not win the trick.
        return 0.0
