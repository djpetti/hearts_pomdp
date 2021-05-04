"""
Represents the actions the agent can take.
"""


from typing import Optional

import pomdp_py
from pydantic.dataclasses import dataclass

from .state import Card


@dataclass(frozen=True)
class Action(pomdp_py.Action):
    """
    Represents the actions the agent can take.

    Args:
        attributes: The card we are playing. Can be None to indicate a nop.

    """

    play: Optional[Card]

    def __eq__(self, other: "Action") -> bool:
        return self.play == other.play

    def __hash__(self) -> int:
        return hash(self.play)

    @property
    def card(self) -> Optional[Card]:
        """
        Returns:
            The card that this action is playing, or None if it is a nop.

        """
        return self.play
