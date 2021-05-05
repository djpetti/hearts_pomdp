"""
Script that performs policy planning with the hearts POMDP.
"""


from functools import partial

import pomdp_py
from loguru import logger

from hearts_pomdp.models.observation import ObservationModel
from hearts_pomdp.models.pomdp import Hearts
from hearts_pomdp.particles import random_particle

# How long to allow for each planning step, in seconds.
_MAX_PLAN_TIME = 5.0


def update_planner(model: Hearts, planner: pomdp_py.Planner) -> None:
    """
    Updates the planner with simulation results for a single timestep. The
    observation model will be used to simulate an actual observation.

    Args:
        model: The POMDP model to use.
        planner: The POMDP planner to use.

    """
    # Determine the next action.
    logger.info("Planning next action...")
    action = planner.plan(model.agent)

    # Simulate the environment.
    reward = model.env.state_transition(action)

    logger.info(
        "Action: {}, Our play: {}, Opponent's play: {}",
        action,
        model.env.state.player_1_play,
        model.env.state.player_2_play,
    )
    logger.info("Player 1 hand: {}", model.env.state.player_1_hand)
    logger.info("Player 2 hand: {}", model.env.state.player_2_hand)
    logger.info("Reward: {}", reward)

    # Simulate an observation.
    observation_model = ObservationModel()
    observation = model.env.provide_observation(observation_model, action)

    model.agent.update_history(action, observation)
    # Use a non-naive method of reinvigorating the belief.
    planner.update(
        model.agent,
        action,
        observation,
        # This is kind of a hack to bypass the naive particle reinvigoration
        # that it uses by default. In this case, the state transformer
        # function actually just generates a new particle from scratch.
        state_transform_func=lambda s: random_particle(model),
    )


def main():
    # Create the model.
    model = Hearts()
    model.agent.set_belief(
        pomdp_py.Particles.from_histogram(
            model.agent.init_belief, num_particles=2000
        ),
        prior=True,
    )

    # Create the planner.
    planner = pomdp_py.POMCP(
        max_depth=13,
        discount_factor=1.0,
        planning_time=_MAX_PLAN_TIME,
        exploration_const=10,
        rollout_policy=model.agent.policy_model,
    )

    for _ in range(13):
        update_planner(model, planner)


if __name__ == "__main__":
    main()
