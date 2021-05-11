"""
An `Agent` that uses a POMDP model for planning.
"""


import pomdp_py
from loguru import logger

from hearts_pomdp.models.pomdp import Hearts
from hearts_pomdp.observation import Observation
from hearts_pomdp.particles import random_particle
from hearts_pomdp.state import Card, State

from .agent import Agent


class PomdpAgent(Agent):
    """
    An `Agent` that uses a POMDP model for planning.
    """

    def __init__(
        self,
        *,
        initial_state: State,
        max_plan_time: float = 10.0,
        exploration_const: float = 40.0
    ):
        """

        Args:
            initial_state: The initial state of the game.
            max_plan_time: Maximum time in seconds to spend planning for each
                turn.
            exploration_const: Exploration constant for POMCP planner.

        """
        # Create the model.
        self.__model = Hearts(initial_state=initial_state)
        self.__model.agent.set_belief(
            pomdp_py.Particles.from_histogram(
                self.__model.agent.init_belief, num_particles=2000
            ),
            prior=True,
        )

        # Create the planner.
        self.__planner = pomdp_py.POMCP(
            max_depth=13,
            discount_factor=1.0,
            planning_time=max_plan_time,
            exploration_const=exploration_const,
            rollout_policy=self.__model.agent.policy_model,
        )

        # The most recent action we took.
        self.__action = None

    def get_next_play(self) -> Card:
        # Determine the next action.
        logger.info("Planning next action...")
        action = self.__planner.plan(self.__model.agent)

        logger.debug("Action: {}", action)

        self.__action = action
        return action.card

    def update(self, observation: Observation, next_state: State) -> None:
        logger.debug("Adding observation: {}", observation)
        if self.__action is None:
            raise ValueError(
                "get_next_play() must be called before " "update()."
            )

        self.__model.agent.update_history(self.__action, observation)
        # Use a non-naive method of reinvigorating the belief.
        self.__planner.update(
            self.__model.agent,
            self.__action,
            observation,
            # This is kind of a hack to bypass the naive particle reinvigoration
            # that it uses by default. In this case, the state transformer
            # function actually just generates a new particle from scratch.
            state_transform_func=lambda s: random_particle(next_state),
        )

        self.__action = None
