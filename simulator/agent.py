"""
Interface for representing a hearts player.
"""


import abc

from hearts_pomdp.observation import Observation
from hearts_pomdp.state import Card, State


class ImpossiblePlayError(Exception):
    """
    Raised when we find ourselves in a situation with no possible plays.
    """


class Agent(abc.ABC):
    """
    Interface for representing a hearts player.
    """

    @abc.abstractmethod
    def get_next_play(self) -> Card:
        """
        Determines the next card that this player should play.

        Returns:
            The next card to play.

        Raises:
            `ImpossiblePlayError` if it can't find a valid play to make.

        """

    @abc.abstractmethod
    def update(self, observation: Observation, next_state: State) -> None:
        """
        Adds a new observation of the state. Meant to be called once after
        each action.

        Args:
            observation: The observation to add.
            next_state: The new state.

        """
