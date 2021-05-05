"""
Miscellaneous common utilities.
"""


from .state import Card, State


def lead_won_trick(*, lead_card: Card, second_card: Card) -> bool:
    """
    Determines which player one a trick.

    Args:
        lead_card: The lead card in the trick.
        second_card: The second card in the trick.

    Returns:
        True if the lead card wins the trick, false otherwise.

    """
    if lead_card.suit == second_card.suit:
        # Higher value wins the trick.
        return lead_card.value.value > second_card.value.value
    else:
        # The lead suit wins the trick.
        return True


def agent_won_trick(state: State) -> bool:
    """
    Determines if the agent won the last trick.

    Args:
        state: The current state.

    Returns:
        True if the agent won the most recent trick.

    """
    lead_won = lead_won_trick(
        lead_card=state.lead_play, second_card=state.second_play
    )
    # Either the agent was the lead and it won, or it wasn't the lead,
    # and it won.
    return lead_won == state.agent_goes_first
