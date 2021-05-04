"""
Tests for the transition model.
"""


import random

import pytest

from hearts_pomdp.action import Action
from hearts_pomdp.models.transition import TransitionModel
from hearts_pomdp.state import (
    Card,
    CardValue,
    State,
    Suit,
    random_initial_state,
)


class TestTransitionModel:
    """
    Tests for the `TransitionModel` class.
    """

    @staticmethod
    def __check_transition_invariants(
        *, next_state: State, state: State, action: Action
    ) -> None:
        """
        Checks that all invariants are upheld by a given state transition.

        Args:
            next_state: The next state.
            state: The initial state.
            action: The action that caused the transition.

        """
        if next_state.player_1_play is None:
            # Both players should have done nothing.
            assert next_state.player_2_play is None

            assert len(next_state.player_1_hand) == len(state.player_1_hand)
            assert len(next_state.player_2_hand) == len(state.player_2_hand)

        else:
            # It should have played the card.
            assert next_state.player_1_play == action.card
            assert next_state.player_2_play is not None
            assert next_state.player_2_play in state.player_2_hand

            assert (
                len(next_state.player_1_hand) == len(state.player_1_hand) - 1
            )
            assert (
                len(next_state.player_2_hand) == len(state.player_2_hand) - 1
            )

    @pytest.mark.parametrize("seed", range(10))
    def test_transition_first(self, seed: int) -> None:
        """
        Tests that we can transition out of the initial state.

        Args:
            seed: The random seed to use for testing.

        """
        # Arrange.
        # Set the seed so we get a consistent initial state.
        random.seed(seed)
        # Get the initial state.
        initial_state = random_initial_state()

        # For our action, we'll attempt to play the 2 of clubs.
        two_of_clubs = Card(suit=Suit.CLUBS, value=CardValue.TWO)
        action = Action(play=two_of_clubs)

        transition_model = TransitionModel()

        # Act.
        # Transition to the next state.
        next_state = transition_model.sample(initial_state, action)
        state_prob = transition_model.probability(
            next_state, initial_state, action
        )

        # Assert.
        self.__check_transition_invariants(
            next_state=next_state, state=initial_state, action=action
        )

        if two_of_clubs not in initial_state.player_1_hand:
            # We should have done nothing, because we didn't have the card.
            assert next_state.player_1_play is None

        # No matter what, the probability of getting this result should be
        # consistent.
        assert state_prob > 0.0

    def test_complete_game(self) -> None:
        """
        Tests that we can simulate a complete game.

        """
        # Arrange.
        # Set the seed so we get a consistent initial state.
        random.seed(1337)
        # Get the initial state.
        state = random_initial_state()

        transition_model = TransitionModel()

        # Act and assert.
        while len(state.player_1_hand) > 0:
            hand_size = len(state.player_1_hand)

            # Systematically try playing every possible card.
            for card in state.player_1_hand:
                action = Action(play=card)
                next_state = transition_model.sample(state, action)

                # Make sure this transition was valid.
                self.__check_transition_invariants(
                    next_state=next_state, state=state, action=action
                )
                assert (
                    transition_model.probability(next_state, state, action)
                    > 0.0
                )

                state = next_state
                if len(state.player_1_hand) < hand_size:
                    # The play succeeded.
                    break
            else:
                # We are in a situation where we have cards, but can't play
                # any of them.
                pytest.fail(
                    "Transition model indicates that no cards are " "playable."
                )
