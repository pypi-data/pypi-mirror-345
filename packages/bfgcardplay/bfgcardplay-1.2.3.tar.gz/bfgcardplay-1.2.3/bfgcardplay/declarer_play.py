"""Methods to support declarer play."""

import inspect
from .logger import log

from bridgeobjects import Card, Suit, CARD_VALUES
from bfgdealer import Trick

import bfgcardplay.global_variables as global_vars
from .player import Player
from .dashboard import SuitCards


def card_combinations(player: Player, suit: str = '') -> Card | None:
    """Return a card from a defined combination, or None."""
    trick = player.board.tricks[-1]
    if not suit:
        suit = trick.suit.name
    opponents_cards = player.opponents_unplayed_cards[suit]
    our_cards = player.our_unplayed_cards[suit]
    suit_cards = SuitCards(suit).cards('A', 'J')
    (ace, king, queen, jack) = suit_cards

    if (ace in our_cards and
            (queen in our_cards or jack in our_cards) and
            king in opponents_cards):
        return missing_king_new(player, suit)

    if (ace in our_cards and
            # (king in our_cards or jack in our_cards) and
            queen in opponents_cards):
        return missing_queen_new(player, suit)
    return None


def lead_to_find_missing_ace(player: Player,
                             suit: Suit,
                             trick: Trick | None = None) -> Card | None:
    """Return the appropriate card if missing the ace."""
    manager = global_vars.manager
    my_suit_cards = player.suit_cards[suit]
    partners_suit_cards = player.partners_suit_cards[suit]
    max_length = max(len(my_suit_cards), len(partners_suit_cards))
    if max_length >= 4:
        unplayed_cards = player.our_unplayed_cards[suit.name]
        if (Card('K', suit.name) in unplayed_cards and
                Card('Q', suit.name) in unplayed_cards and
                Card('J', suit.name) in unplayed_cards and
                Card('T', suit.name) in unplayed_cards):
            for card in my_suit_cards:
                if card.value >= CARD_VALUES['T']:
                    return log(inspect.stack(), card)

    partners_entries = player.get_entries_in_other_suits(
        player.partners_hand, suit)
    if ((Card('K', suit.name) in my_suit_cards and
            Card('Q', suit.name) in my_suit_cards and partners_entries) or
            (Card('Q', suit.name) in my_suit_cards and
             Card('J', suit.name) in my_suit_cards and partners_entries)):
        card = _make_entry_to_partners_hand(player, manager, partners_entries)
        if card:
            return log(inspect.stack(), card)
    return my_suit_cards[-1]


def _make_entry_to_partners_hand(player, manager, partners_entries):
    """Return a card to enable partner to return suit_to_develop."""
    for entry in partners_entries:
        entry_suit = entry.suit.name
        my_entry_cards = player.suit_cards[entry_suit]
        if my_entry_cards:
            manager.win_trick[player.partner_seat] = True
            return my_entry_cards[-1]
    return None


def missing_king(player: Player, suit: Suit) -> Card | None:
    """Return the appropriate card if missing the king."""
    manager = global_vars.manager
    my_suit_cards = player.suit_cards[suit]
    partners_suit_cards = player.partners_suit_cards[suit]
    my_entries = player.get_entries_in_other_suits(player.hand, suit)
    partners_entries = player.get_entries_in_other_suits(
        player.partners_hand, suit)

    tenace_in_my_hand = player.get_suit_tenaces(my_suit_cards)
    right_hand_opponent_is_void = player.voids[
        player.right_hand_seat][suit.name]
    if tenace_in_my_hand and right_hand_opponent_is_void:
        for card in my_suit_cards:
            if card.value < CARD_VALUES['K']:
                return log(inspect.stack(), card)

    if tenace_in_my_hand and len(partners_entries) >= 1:
        card = _make_entry_to_partners_hand(player, manager, partners_entries)
        if card:
            return log(inspect.stack(), card)

    tenace_in_partners_hand = player.get_suit_tenaces(partners_suit_cards)
    queen = Card('Q', suit.name)
    jack = Card('J', suit.name)
    if tenace_in_partners_hand and len(my_entries) >= 1:
        return log(inspect.stack(), my_suit_cards[-1])
    elif queen in my_suit_cards and jack in my_suit_cards:
        return log(inspect.stack(), queen)
    elif queen in partners_suit_cards and jack in partners_suit_cards:
        return log(inspect.stack(), my_suit_cards[-1])

    for card in my_suit_cards[::-1]:
        if player.is_winner_declarer(card):
            return log(inspect.stack(), card)
        else:
            return log(inspect.stack(), my_suit_cards[0])

    print(f'missing_king return None {suit}')
    return None


def missing_king_new(player: Player, suit: str) -> Card | None:
    """Return the appropriate card if missing the king."""
    manager = global_vars.manager
    manager.set_missing_king(player.seat, suit, True)

    our_card_count = len(player.our_cards[suit])
    if our_card_count >= 11:
        return _missing_king_with_eleven_cards(player, suit)
    if our_card_count == 10:
        return _missing_king_with_ten_cards(player, suit)
    elif our_card_count == 9:
        return _missing_king_with_nine_cards(player, suit)
    elif our_card_count == 8:
        return _missing_king_with_eight_cards(player, suit)
    elif 5 <= our_card_count <= 8:
        return _missing_king_with_five_to_eight_cards(player, suit)

    return None


def _missing_king_with_eleven_cards(player, suit):
    my_cards = player.unplayed_cards[suit]
    (ace, king, queen, jack, ten) = SuitCards(suit).cards('A', 'T')
    if ace in my_cards:
        return log(inspect.stack(), ace)
    return log(inspect.stack(), my_cards[-1])


def _missing_king_with_ten_cards(player, suit):
    my_cards = player.unplayed_cards[suit]
    partners_cards = player.partners_unplayed_cards[suit]
    (ace, king, queen, jack, ten) = SuitCards(suit).cards('A', 'T')

    # Partner holds A and Q
    if ace in partners_cards and queen in partners_cards:
        return log(inspect.stack(), my_cards[-1])

    # A in this hand and partner holds the Q
    if ace in my_cards and queen in partners_cards:
        return log(inspect.stack(), ace)

    # QJ in this hand and partner holds the A
    if (ace in partners_cards and queen in my_cards and jack in my_cards):
        return log(inspect.stack(), queen)

    # Q in this hand and partner holds the A
    if ace in partners_cards and queen in my_cards:
        return log(inspect.stack(), my_cards[-1])

    # A and Q in this hand
    if ace in my_cards and queen in my_cards:
        return None
    return None


def _missing_king_with_nine_cards(player, suit):
    my_cards = player.unplayed_cards[suit]
    partners_cards = player.partners_unplayed_cards[suit]
    (ace, king, queen, jack, ten) = SuitCards(suit).cards('A', 'T')
    # Partner holds A and Q and this hand holds JT
    if (ace in partners_cards and queen in partners_cards and
            jack in my_cards and ten in my_cards):
        return log(inspect.stack(), jack)

    # Partner holds JT and this hand holds AQ
    if (ace in my_cards and queen in my_cards and
            jack in partners_cards and ten in partners_cards):
        return None

    # Partner holds A and Q
    if ace in partners_cards and queen in partners_cards:
        return log(inspect.stack(), my_cards[-1])

    # A in this hand
    if ace in my_cards:
        return log(inspect.stack(), ace)

    # Partner holds A
    if ace in partners_cards:
        return log(inspect.stack(), my_cards[-1])
    return None


def _missing_king_with_eight_cards(player, suit):
    my_cards = player.unplayed_cards[suit]
    partners_cards = player.partners_unplayed_cards[suit]
    (ace, king, queen, jack, ten) = SuitCards(suit).cards('A', 'T')
    # Partner holds A and Q
    if ace in partners_cards and queen in partners_cards:
        return log(inspect.stack(), my_cards[-1])
    return None


def _missing_king_with_five_to_eight_cards(player, suit):
    my_cards = player.unplayed_cards[suit]
    partners_cards = player.partners_unplayed_cards[suit]
    # We hold AQJT9
    our_cards = my_cards + partners_cards
    (ace, king, queen, jack, ten) = SuitCards(suit).cards('A', 'T')
    nine = Card('9', suit)
    if (ace in our_cards and queen in our_cards and
            jack in our_cards and ten in our_cards and nine in our_cards):
        if len(my_cards) > 1:
            return log(inspect.stack(), my_cards[1])
        else:
            return log(inspect.stack(), my_cards[-1])
    return None


def missing_queen_new(player: Player, suit: str) -> Card | None:
    """Return the appropriate card if missing the queen."""
    trick = player.board.tricks[-1]
    (ace, king, queen, jack, ten) = SuitCards(suit).cards('A', 'T')
    my_cards = player.unplayed_cards[suit]
    partners_cards = player.partners_unplayed_cards[suit]

    # hand holds AJ and partner K
    if ace in my_cards and jack in my_cards and king in partners_cards:
        if len(my_cards) > 2:
            return log(inspect.stack(), my_cards[1])

    # hand holds K and partner AJ
    elif king in my_cards and ace in partners_cards and jack in partners_cards:
        return log(inspect.stack(), king)

    # hand holds KJ and partner A
    elif king in my_cards and jack in my_cards and ace in partners_cards:
        if len(my_cards) > 2:
            return my_cards[-1]
        return log(inspect.stack(), my_cards[-1])

    # hand holds AJ and K not played by partner
    elif (ace in my_cards and jack in my_cards and trick.cards
          and trick.cards[0] != king):
        return log(inspect.stack(), jack)

    # hand holds A and K not played by partner
    elif ace in my_cards and trick.cards and trick.cards[0] != king:
        return log(inspect.stack(), ace)
    return None


def missing_queen(player: Player,
                  suit: Suit,
                  trick: Trick | None = None) -> Card | None:
    """Return the appropriate card if missing the queen."""
    manager = global_vars.manager
    my_suit_cards = player.suit_cards[suit]
    partners_suit_cards = player.partners_suit_cards[suit]
    (ace, king, queen, jack, ten) = SuitCards(suit.name).cards('A', 'T')

    if not partners_suit_cards:
        return log(inspect.stack(), my_suit_cards[0])

    if len(player.our_cards[suit.name]) >= 9:
        if trick:
            trick_cards = trick.cards
        else:
            trick_cards = []
        if ace in my_suit_cards and king not in trick_cards:
            return log(inspect.stack(), my_suit_cards[0])
        if king in my_suit_cards and ace not in trick_cards:
            return log(inspect.stack(), my_suit_cards[0])
        return log(inspect.stack(), my_suit_cards[-1])

    my_entries = player.get_entries_in_other_suits(player.hand, suit)
    partners_entries = player.get_entries_in_other_suits(
        player.partners_hand, suit)

    tenace_in_my_hand = player.get_suit_tenaces(my_suit_cards)
    right_hand_opponent_is_void = player.voids[player.right_hand_seat][
        suit.name]
    if tenace_in_my_hand and right_hand_opponent_is_void:
        for card in my_suit_cards:
            if card.value < CARD_VALUES['Q']:
                return log(inspect.stack(), card)

    if tenace_in_my_hand and len(partners_entries) >= 1:
        card = _make_entry_to_partners_hand(player, manager, partners_entries)
        if card:
            return log(inspect.stack(), card)

    if ace in partners_suit_cards:
        return log(inspect.stack(), my_suit_cards[-1])

    if not tenace_in_my_hand:
        tenace_in_partners_hand = player.get_suit_tenaces(partners_suit_cards)
        if tenace_in_partners_hand and len(my_entries) >= 1:
            if my_suit_cards[0] == ace or my_suit_cards[0] == king:
                return log(inspect.stack(), my_suit_cards[0])
            else:
                return log(inspect.stack(), my_suit_cards[-1])

    for card in my_suit_cards[::-1]:
        if player.is_winner_declarer(card):
            return log(inspect.stack(), card)
        else:
            partners_cards = player.partners_unplayed_cards[suit.name]
            if not partners_cards:
                return None
            manager.card_to_play[player.partner_seat] = partners_cards[-1]
            return log(inspect.stack(), my_suit_cards[0])
    print(f'missing_queen return None {suit}')
    return None
