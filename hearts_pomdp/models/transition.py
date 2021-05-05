"""
Implements the transition model.
"""
import random
from typing import AbstractSet, Any, Optional

import pomdp_py

from ..action import Action
from ..state import ALL_CARDS, Card, CardValue, State, Suit


class TransitionModel(pomdp_py.TransitionModel):
    """
    Implements the transition model.
    """

    _TWO_OF_CLUBS = Card(suit=Suit.CLUBS, value=CardValue.TWO)
    _QUEEN_OF_SPADES = Card(suit=Suit.SPADES, value=CardValue.QUEEN)
    _ALL_HEARTS = {c for c in ALL_CARDS if c.suit == Suit.HEARTS}

    @classmethod
    def __deterministic_next_state(cls, state: State, action: Action) -> State:
        """
        Computes the parts of the next state that are known deterministically.

        Args:
            state: The current state.
            action: The action being taken.

        Returns:
            The next state. The parts that cannot be known deterministically
            will be arbitrary.

        """
        nop_state = State(
            player_1_hand=state.player_1_hand,
            player_2_hand=state.player_2_hand,
            held_out_cards=state.held_out_cards,
            is_first_trick=state.is_first_trick,
            player_1_play=None,
            player_2_play=None,
        )

        if action.card is None:
            # Nop action.
            return nop_state
        if action.card not in state.player_1_hand:
            # We can't play a card we don't have, so this ends up being a nop.
            return nop_state

        if state.is_first_trick:
            if (
                action.card != cls._TWO_OF_CLUBS
                and cls._TWO_OF_CLUBS in state.player_1_hand
            ):
                # If we have the two of clubs, we must lead with it.
                return nop_state
            elif action.card == cls._QUEEN_OF_SPADES:
                # We can never play the queen of spades on the first trick.
                return nop_state
            has_suits = {c.suit for c in state.player_1_hand}
            if action.card.suit == Suit.HEARTS and len(has_suits) > 1:
                # We cannot play a heart on the first trick if we have other
                # options.
                return nop_state

        # Play the selected card.
        return State(
            player_1_hand=state.player_1_hand - {action.card},
            player_2_hand=state.player_2_hand,
            held_out_cards=state.held_out_cards,
            is_first_trick=False,
            player_1_play=action.card,
            player_2_play=None,
        )

    @staticmethod
    def __draw_probability(
        card_set: AbstractSet, card: Optional[Card]
    ) -> float:
        """
        Small helper function that determines the probability that we will
        draw a specific card from a set of cards.

        Args:
            card_set: The set of cards to draw from.
            card: The card we are drawing.

        Returns:
            The probability that this card will be drawn.

        """
        if card in card_set:
            return 1.0 / len(card_set)
        elif card is None and len(card_set) == 0:
            # Special case: we don't have any cards, and we're not picking one.
            return 1.0

        # Not in the set.
        return 0.0

    @staticmethod
    def __opponent_play_obeys_semantics(
        next_state: State, state: State
    ) -> bool:
        """
        Determines whether player 2's play obeys the semantics of the state.

        Args:
            next_state: The final state.
            state: The initial state.

        Returns:
            True if it obeys the semantics, false otherwise.

        """
        if next_state.player_1_play is None:
            # If the first player is not taking an action, we can't either.
            if (
                next_state.player_2_play is not None
                or next_state.player_2_hand != state.player_2_hand
            ):
                return False

        elif next_state.player_2_play is None:
            # If the agent played a card, the opponent must play one too.
            return False

        new_expected_hand = next_state.player_2_hand
        if state.player_2_play is not None:
            new_expected_hand -= {state.player_2_play}
        if next_state.player_2_hand != new_expected_hand:
            # Our new hand must reflect the card we played.
            return False

        return True

    @classmethod
    def __possible_opponent_plays(
        cls, next_state: State, state: State
    ) -> AbstractSet[Card]:
        """
        Determines the possible cards that the opponent can play while still
        following the rules.

        Args:
            next_state: The known part of the final state, including player 1's
                play.
            state: The initial state.

        Returns:
            The set of cards that player 2 can legally play.

        """
        if next_state.player_1_play is None:
            # If the first player did nothing, we can't do anything either.
            return set()

        lead_suit = next_state.player_1_play.suit
        # We have to follow suit.
        same_suit = {c for c in state.player_2_hand if c.suit == lead_suit}

        if len(same_suit) > 0:
            # Choose from one of these.
            return same_suit

        # Otherwise, we can play any other suit.
        non_lead_suit = {c for c in state.player_2_hand if c.suit != lead_suit}
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
    def __opponent_play_probability(
        cls, next_state: State, state: State
    ) -> float:
        """
        Determines the probability of the second player making a particular
        move.

        Args:
            next_state: The final state.
            state: The initial state.

        Returns:
            The probability of reaching this final state, given that the
            portions of the state governed by the first player are already
            known.

        """
        if not cls.__opponent_play_obeys_semantics(next_state, state):
            return 0.0

        possible_plays = cls.__possible_opponent_plays(next_state, state)
        return cls.__draw_probability(possible_plays, next_state.player_2_play)

    def probability(
        self, next_state: State, state: State, action: Action, **kwargs: Any
    ) -> float:
        """
        Calculates `P(s' | s, a)`.

        Args:
            next_state: The resulting state.
            state: The initial state.
            action: The action we are taking.
            **kwargs: Will be ignored.

        Returns:
            The probability to transitioning to the next state from the
            initial state after taking the specified action.

        """
        # Check the deterministic part of the state.
        known_actual = (
            next_state.player_1_hand,
            next_state.held_out_cards,
            next_state.is_first_trick,
            next_state.player_1_play,
        )
        deterministic_state = self.__deterministic_next_state(state, action)
        known_expected = (
            deterministic_state.player_1_hand,
            deterministic_state.held_out_cards,
            deterministic_state.is_first_trick,
            deterministic_state.player_1_play,
        )
        if known_actual != known_expected:
            return 0.0

        # Check the opponent's play.
        return self.__opponent_play_probability(next_state, state)

    def sample(self, state: State, action: Action, **kwargs: Any) -> State:
        """
        Randomly samples a possible next state given a current state and an
        action.

        Args:
            state: The current state.
            action: The action to take.
            **kwargs: Will be ignored.

        Returns:
            The sampled next action.

        """
        # Get the deterministic part of the next state.
        fixed_next_state = self.__deterministic_next_state(state, action)

        # Determine possible plays for player 2.
        player_2_plays = self.__possible_opponent_plays(
            fixed_next_state, state
        )
        player_2_play = None
        player_2_hand = state.player_2_hand
        if len(player_2_plays) > 0:
            # Select one randomly.
            player_2_play = random.sample(player_2_plays, 1)[0]
            player_2_hand -= {player_2_play}

        return State(
            player_1_hand=fixed_next_state.player_1_hand,
            player_2_hand=player_2_hand,
            held_out_cards=fixed_next_state.held_out_cards,
            is_first_trick=fixed_next_state.is_first_trick,
            player_1_play=fixed_next_state.player_1_play,
            player_2_play=player_2_play,
        )
