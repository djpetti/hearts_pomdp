"""
Represents the observations the agent can receive.
"""


from typing import Any, Dict, FrozenSet, Optional

import pomdp_py
from pydantic import validator
from pydantic.dataclasses import dataclass

from .state import Card, ObservableStateMixin


@dataclass(frozen=True)
class Observation(pomdp_py.Observation, ObservableStateMixin):
    """
    Represents the observations the agent can receive.

    """
