"""
    Opening leads for Card Player class.

    Returns  a card_player_components PlayedCard which includes
    name: str
    reason: str
"""

import inspect
from .logger import log

from .card_player_components import SelectedCard

MODULE_COLOUR = 'blue'


def opening_lead_card(suit_cards, contract):
    """Return the opening lead from a list of cards given the contract."""
    cards = sorted(suit_cards, key=lambda x: x.order, reverse=True)
    for card in cards:
        if card.value == 9:  # T is regarded as an honour
            card.is_honour = True

    (card, selection_code) = _select_card_from_suit(cards, contract)
    return SelectedCard(card.name, selection_code)


def _are_adjacent(value_1, value_2):
    """Return True if the cards are adjacent."""
    if abs(value_1.value - value_2.value) == 1:
        return True
    return False


def _select_card_from_suit(cards, contract):
    """Return the correct card from the selected suit."""
    # Suits with 3 cards
    if len(cards) == 3:
        return _select_card_from_triplet(cards, contract)

    # Doubletons
    if len(cards) == 2:
        return _select_card_from_doubleton(cards)

    # Singletons
    if len(cards) == 1:
        return log(inspect.stack(), (cards[0], '015'))

    # Suits with 4 or more cards
    if len(cards) >= 4:
        if contract.is_nt:
            return _select_card_for_nt_contract(cards)
        return _select_card_for_suit_contract(cards)


def _select_card_for_suit_contract(cards):
    """Return the correct card for suit contract with four or more cards."""

    # NB Klinger's Guide to Better Card Play
    # overrides Basic Bridge for 4 card suits

    # Suit headed by an A
    if cards[0].rank == 'A':
        return log(inspect.stack(), (cards[0], '013'))

    top_of_solid_sequence = solid_sequence(cards)
    if top_of_solid_sequence:
        return log(inspect.stack(), (top_of_solid_sequence, '020'))

    top_of_near_sequence = near_sequence(cards)
    if top_of_near_sequence:
        return log(inspect.stack(), (top_of_near_sequence, '021'))

    top_of_internal_sequence = internal_sequence(cards)
    if top_of_internal_sequence:
        return log(inspect.stack(), (top_of_internal_sequence, '022'))

    top_of_touching_honours = touching_honours(cards)
    if top_of_touching_honours:
        return log(inspect.stack(), (top_of_touching_honours, '023'))

    # With 4 rags, lead second highest
    if len(cards) >= 4:
        if not cards[0].is_honour:
            if len(cards) > 4:
                return log(inspect.stack(), (cards[3], '004'))
            return log(inspect.stack(), (cards[1], '014'))

    # With an honour, lead fourth highest
    return log(inspect.stack(), (cards[3], '004'))


def _select_card_for_nt_contract(cards):
    """Return the correct card in a NT contract with four or more cards."""

    top_of_solid_sequence = solid_sequence(cards)
    if top_of_solid_sequence:
        return log(inspect.stack(), (top_of_solid_sequence, '020'))

    top_of_near_sequence = near_sequence(cards)
    if top_of_near_sequence:
        return log(inspect.stack(), (top_of_near_sequence, '021'))

    # if top_of_near_sequence:
    #     return log(inspect.stack(), (top_of_near_sequence, '021'))

    top_of_internal_sequence = internal_sequence(cards)
    if top_of_internal_sequence:
        return log(inspect.stack(), (top_of_internal_sequence, '022'))

    # With 4 rags, lead second highest
    if len(cards) >= 4:
        if not cards[0].is_honour:
            if len(cards) > 4:
                return log(inspect.stack(), (cards[3], '004'))
            return log(inspect.stack(), (cards[1], '014'))

    # Lead fourth highest
    return log(inspect.stack(), (cards[3], '004'))


def _select_card_from_triplet(cards, contract):
    """Return the correct card from a three card suit."""

    # Suit headed by A and no K in a NT contract
    if cards[0].rank == 'A' and cards[1].rank != 'K':
        if contract.is_nt:
            return log(inspect.stack(), (cards[2], '007'))
        return log(inspect.stack(), (cards[0], '013'))

    if cards[0].rank == 'A' and cards[1].rank == 'K':
        return log(inspect.stack(), (cards[0], '013'))

    # Suit headed by an honour and adjacent card
    if cards[0].is_honour and _are_adjacent(cards[0], cards[1]):
        return log(inspect.stack(), (cards[0], '003'))

    # Suit headed by an honour: top of two touching cards
    if (cards[1].is_honour and _are_adjacent(cards[1], cards[2])):
        return log(inspect.stack(), (cards[1], '008'))

    # Suit headed by two honours
    if (cards[0].is_honour and cards[1].is_honour):
        return log(inspect.stack(), (cards[2], '010'))

    # Suit headed by a single honour
    if (cards[0].is_honour and not cards[1].is_honour):
        return log(inspect.stack(), (cards[2], '007'))

    # Return middle card
    return log(inspect.stack(), (cards[1], '005'))


def _select_card_from_doubleton(cards):
    """Return the correct card from a two card suit."""
    if cards[0].rank == 'A' and cards[1].rank == 'K':
        return log(inspect.stack(), (cards[1], '002'))
    return log(inspect.stack(), (cards[0], '001'))


def solid_sequence(cards):
    """Returns the top of the solid sequence if there is one, or None."""
    if len(cards) < 3:
        return None
    for index in range(len(cards)-2):
        if (cards[index].value == cards[index+1].value + 1 and
                cards[index+1].value == cards[index+2].value + 1 and
                cards[index].value >= 9):
            return cards[index]
    return None


def near_sequence(cards):
    """Returns the top of the near sequence if there is one, or None."""
    if len(cards) < 3:
        return None
    for index in range(len(cards)-2):
        if (cards[index].value == cards[index+1].value + 1 and
                cards[index+1].value == cards[index+2].value + 2 and
                cards[index].value >= 9):
            return cards[index]
    return None


def internal_sequence(cards):
    """Returns the top of the internal sequence if there is one, or None."""
    if len(cards) < 3:
        return None
    for index in range(len(cards) - 2):
        card = _find_internal_sequence(cards, index)
        if card:
            return card
    return None


def _find_internal_sequence(cards, index):
    for offset in range(2, 5):  # Check Q, J and T
        if (cards[index].value == cards[index+1].value + offset and
                cards[index+1].value == cards[index+2].value + 1 and
                cards[index+1].is_honour):
            return cards[index+1]
    return None


def touching_honours(cards):
    """Returns the top of the touching honours if there is one, or None."""
    if len(cards) < 3:
        return None
    for index in range(len(cards)-1):
        if (cards[index].value == cards[index+1].value + 1 and
                cards[index].value >= 12):
            return cards[index]
    return None
