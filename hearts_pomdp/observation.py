"""
Represents the observations the agent can receive.
"""


import pomdp_py
from pydantic.dataclasses import dataclass

from .state import Card, ObservableStateMixin


@dataclass(frozen=True)
class Observation(pomdp_py.Observation, ObservableStateMixin):
    """
    Represents the observations the agent can receive.

    Attributes:
        opponent_hand_size: Number of cards in opponent's hand.

    """

    opponent_hand_size: int
