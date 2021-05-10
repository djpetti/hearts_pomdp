"""
Implements the transition model.
"""


import dataclasses as py_dataclasses
import random
from typing import AbstractSet, Any

import pomdp_py

from ..action import Action
from ..state import ALL_CARDS, Card, CardValue, State, Suit, lowest_club
from ..utils import agent_won_trick


class TransitionModel(pomdp_py.TransitionModel):
    """
    Implements the transition model.
    """

    _TWO_OF_CLUBS = Card(suit=Suit.CLUBS, value=CardValue.TWO)
    _QUEEN_OF_SPADES = Card(suit=Suit.SPADES, value=CardValue.QUEEN)
    _ALL_HEARTS = {c for c in ALL_CARDS if c.suit == Suit.HEARTS}

    @classmethod
    def __transition_common(cls, state: State) -> State:
        """
        Performs the parts of the state transition that are common to all
        transitions and deterministic.

        Args:
            state: The current state.

        Returns:
            The updated state.

        """
        return py_dataclasses.replace(
            state,
            is_first_trick=False,
            # A partial trick becomes the current trick.
            opponent_play=state.opponent_partial_play,
            opponent_partial_play=None,
        )

    @classmethod
    def __possible_first_plays(cls, state: State) -> AbstractSet[Card]:
        """
        Determines the possible cards that the first player can lead with
        while still following the rules.

        Args:
            state: The initial state.

        Returns:
            The set of cards that player 1 can legally play.

        """
        if state.is_first_trick:
            # We nominally lead with the two of clubs. Note that a valid state
            # initialization always makes the player with the two of clubs
            # the first player, so if we don't have it, it can only be held out.
            assert (
                cls._TWO_OF_CLUBS not in state.second_player_hand
            ), "Second player shouldn't have the two of clubs."

            # Play our lowest club.
            first_card = lowest_club(state.first_player_hand)
            assert (
                first_card is not None
            ), "Agent should not be first if they have no clubs."
            return {first_card}

        else:
            # Normally, we can lead with anything.
            possible_plays = state.first_player_hand

            if not state.hearts_broken:
                # Hearts have not been broken, so we cannot lead with one.
                possible_plays -= cls._ALL_HEARTS
            if len(possible_plays) == 0:
                # ...except when we have nothing BUT hearts.
                possible_plays = state.first_player_hand

            return possible_plays

    @classmethod
    def __possible_second_plays(
        cls, next_state: State, state: State
    ) -> AbstractSet[Card]:
        """
        Determines the possible cards that the second player can play while
        still following the rules.

        Args:
            next_state: The known part of the final state, including player 1's
                play.
            state: The initial state.

        Returns:
            The set of cards that player 2 can legally play.

        """
        if next_state.lead_play is None:
            # If the first player did nothing, we can't do anything either.
            return set()

        lead_suit = next_state.lead_play.suit
        # We have to follow suit.
        same_suit = {
            c for c in state.second_player_hand if c.suit == lead_suit
        }

        if len(same_suit) > 0:
            # Choose from one of these.
            return same_suit

        # Otherwise, we can play any other suit.
        non_lead_suit = {
            c for c in state.second_player_hand if c.suit != lead_suit
        }
        possible_plays = non_lead_suit
        if state.is_first_trick:
            # On the first trick, we can't play hearts if we don't have to or
            # the queen of spades.
            possible_plays = (
                non_lead_suit - {cls._QUEEN_OF_SPADES} - cls._ALL_HEARTS
            )
            if len(possible_plays) == 0:
                # In this case, we have no choice but to play a heart.
                possible_plays = non_lead_suit - {cls._QUEEN_OF_SPADES}

        return possible_plays

    @classmethod
    def __handle_heartbreak(cls, next_state: State) -> State:
        """
        `assert "It's going to be okay"`

        Keeps track of when hearts have been broken and updates the state
        accordingly.

        Args:
            next_state: The partially-updated state encompassing the results
                of the current trick.

        Returns:
            The updated state.

        """
        if (
            next_state.second_play.suit == Suit.HEARTS
            or next_state.lead_play.suit == Suit.HEARTS
            or next_state.opponent_partial_play == Suit.HEARTS
        ):
            # Hearts have been broken.
            return py_dataclasses.replace(next_state, hearts_broken=True)
        return next_state

    @classmethod
    def __handle_moonshot(cls, next_state: State) -> State:
        """
        Keeps track of whether players are shooting the moon, and updates
        the state accordingly.

        Args:
            next_state: The partially-updated state, encompassing the results
                of the current trick.

        Returns:
            The updated state.

        """
        agent_took_all_penalties = next_state.agent_took_all_penalties
        opponent_took_all_penalties = next_state.opponent_took_all_penalties

        trick_painted = (
            next_state.agent_play.is_penalty
            or next_state.opponent_play.is_penalty
        )

        agent_won = agent_won_trick(next_state)
        if trick_painted and agent_won:
            # If the agent took a penalty card, the opponent can't shoot the
            # moon.
            opponent_took_all_penalties = False
        elif trick_painted and not agent_won:
            # Similarly, if the opponent took a penalty card, the agent can't
            # shoot the moon.
            agent_took_all_penalties = False

        return py_dataclasses.replace(
            next_state,
            agent_took_all_penalties=agent_took_all_penalties,
            opponent_took_all_penalties=opponent_took_all_penalties,
        )

    @classmethod
    def __handle_trick_winner(cls, next_state: State) -> State:
        """
        If the opponent wins, they go first next trick. This is simulated by
        immediately updating the state again. This method checks for this
        condition and performs the necessary state update if it is met.

        Args:
            next_state: The partially-updated state encompassing the results
                of the current trick.

        Returns:
            The updated state.

        """
        # Handle shooting the moon.
        next_state = cls.__handle_moonshot(next_state)

        # Determine the first player for the next trick.
        next_state = py_dataclasses.replace(
            next_state, agent_goes_first=agent_won_trick(next_state)
        )
        if next_state.agent_goes_first:
            # The agent goes first next round. No need to do anything else.
            return next_state

        # Otherwise, we have to simulate the first play by the opponent.
        player_1_plays = cls.__possible_first_plays(next_state)
        if len(player_1_plays) == 0:
            # We are out of cards to play, so we don't have to do anything.
            return next_state

        # Choose a random card to play.
        player_1_hand = next_state.first_player_hand
        player_1_play = random.choice(tuple(player_1_plays))
        player_1_hand -= {player_1_play}

        return py_dataclasses.replace(
            next_state,
            opponent_hand=player_1_hand,
            # Update the partial play variable since this is technically a
            # new trick.
            opponent_partial_play=player_1_play,
        )

    @classmethod
    def __sample_agent_is_first(cls, state: State, action: Action) -> State:
        """
        Handles the sampling in the case that the agent is the first player.

        Args:
            state: The current state.
            action: The action to take.

        Returns:
            The sampled next state.

        """
        nop_state = py_dataclasses.replace(
            state, agent_play=None, opponent_play=None
        )

        # The first trick flag will always be set to false.
        next_state = cls.__transition_common(state)

        # Determine possible plays for the agent.
        player_1_plays = cls.__possible_first_plays(state)
        # Make sure that our action is valid.
        if action.card is None or action.card not in player_1_plays:
            # Action is invalid. This is a nop.
            return nop_state

        # Update the state with the action.
        player_1_hand = state.first_player_hand
        player_1_hand -= {action.card}
        next_state = py_dataclasses.replace(
            next_state, agent_play=action.card, agent_hand=player_1_hand
        )

        # Determine possible plays for player 2.
        player_2_plays = cls.__possible_second_plays(next_state, state)
        assert len(player_2_plays) > 0, "Agent 2 ended up with fewer cards."

        # Select one randomly.
        player_2_play = random.choice(tuple(player_2_plays))
        player_2_hand = state.second_player_hand
        player_2_hand -= {player_2_play}

        next_state = py_dataclasses.replace(
            next_state,
            opponent_hand=player_2_hand,
            opponent_play=player_2_play,
        )

        # Handle additional modifications based on the winner of this trick.
        next_state = cls.__handle_trick_winner(next_state)
        return cls.__handle_heartbreak(next_state)

    @classmethod
    def __sample_agent_is_second(cls, state: State, action: Action) -> State:
        """
        Handles the sampling in the case that the agent is the second player.

        Args:
            state: The current state.
            action: The action to take.

        Returns:
            The sampled next state.

        """
        nop_state = py_dataclasses.replace(
            state, agent_play=None, opponent_play=None
        )

        # The first trick flag will always be set to false.
        next_state = cls.__transition_common(state)
        # In this case, we should already be halfway done with the trick from
        # the previous state update.
        if next_state.lead_play is None:
            # The opponent did a nop, so we have to do the same.
            return nop_state

        player_2_plays = cls.__possible_second_plays(next_state, state)
        assert len(player_2_plays) > 0, "Agent 2 ended up with fewer cards."
        if action.card not in player_2_plays:
            # Action is invalid. This is a nop.
            return nop_state

        # Update the state.
        player_2_hand = state.second_player_hand
        player_2_hand -= {action.card}
        next_state = py_dataclasses.replace(
            next_state, agent_hand=player_2_hand, agent_play=action.card
        )

        # Handle additional modifications based on the winner of this trick.
        next_state = cls.__handle_trick_winner(next_state)
        return cls.__handle_heartbreak(next_state)

    def sample(self, state: State, action: Action, **kwargs: Any) -> State:
        """
        Randomly samples a possible next state given a current state and an
        action.

        Args:
            state: The current state.
            action: The action to take.
            **kwargs: Will be ignored.

        Returns:
            The sampled next state.

        """
        if state.agent_goes_first:
            return self.__sample_agent_is_first(state, action)
        else:
            return self.__sample_agent_is_second(state, action)
