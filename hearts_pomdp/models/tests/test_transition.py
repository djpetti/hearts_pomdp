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
        if next_state.agent_play is None:
            # Both players should have done nothing.
            assert next_state.opponent_play is None

            assert len(next_state.agent_hand) == len(state.agent_hand)
            assert len(next_state.opponent_hand) == len(state.opponent_hand)

        else:
            # It should have played the card.
            assert next_state.agent_play == action.card
            assert next_state.opponent_play is not None

            if state.opponent_partial_play is not None:
                # The partial trick from last time should have become the
                # current trick.
                assert next_state.opponent_play == state.opponent_partial_play
            else:
                # Opponent should have played a new card this transition.
                assert next_state.opponent_play in state.opponent_hand

            # Opponent might play 0, one, or two cards.
            cards_played = 0
            if state.opponent_partial_play is None:
                # Opponent should have played a new card this time.
                cards_played += 1
            if next_state.opponent_partial_play is not None:
                # Opponent started the next trick.
                cards_played += 1

            assert len(next_state.agent_hand) == len(state.agent_hand) - 1
            assert (
                len(next_state.opponent_hand)
                == len(state.opponent_hand) - cards_played
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

        # Assert.
        self.__check_transition_invariants(
            next_state=next_state, state=initial_state, action=action
        )

        if two_of_clubs not in initial_state.agent_hand:
            # We should have done nothing, because we didn't have the card.
            assert next_state.agent_play is None

    @pytest.mark.parametrize("seed", range(10))
    def test_complete_game(self, seed: int) -> None:
        """
        Tests that we can simulate a complete game.

        Args:
            seed: The random seed to use for testing.

        """
        # Arrange.
        # Set the seed so we get a consistent initial state.
        random.seed(seed)
        # Get the initial state.
        state = random_initial_state()

        transition_model = TransitionModel()

        # Act and assert.
        while len(state.agent_hand) > 0:
            hand_size = len(state.agent_hand)

            # Systematically try playing every possible card.
            for card in state.agent_hand:
                action = Action(play=card)
                next_state = transition_model.sample(state, action)

                # Make sure this transition was valid.
                self.__check_transition_invariants(
                    next_state=next_state, state=state, action=action
                )

                state = next_state
                if len(state.agent_hand) < hand_size:
                    # The play succeeded.
                    break
            else:
                # We are in a situation where we have cards, but can't play
                # any of them.
                pytest.fail(
                    "Transition model indicates that no cards are " "playable."
                )
