"""Methods to support Defender play."""

import inspect
from .logger import log

from bridgeobjects import Card, Suit, CARD_VALUES, SUITS

import bfgcardplay.global_variables as global_vars
from .utilities import other_suit_for_signals
from .player import Player

MODULE_COLOUR = 'cyan'


def deduce_partner_void_in_trumps(player: Player) -> bool:
    """Return True if we can deduce that partner is void in trumps."""
    suit = player.trump_suit.name
    auction = player.board.auction
    opening_call = auction.seat_calls[player.declarer][0]
    if (opening_call.level == 3
            and opening_call.denomination == player.trump_suit):
        my_trumps = player.hand.cards_by_suit[suit]
        dummys_trumps = player.hands[player.dummy].cards_by_suit[suit]
        if len(my_trumps) + len(dummys_trumps) >= 5:
            return True
    return False


def dummy_is_short_trump_hand(player: Player) -> bool:
    """Return True if dummy is short trump hand."""
    return len(player.hands[player.dummy].cards_by_suit[
        player.trump_suit.name]) <= 4


def get_hilo_signal_card(caller) -> Card:
    """Return a signal card denoting even/odd"""
    player = caller.player
    cards = caller.cards
    manager = global_vars.manager
    trick = player.board.tricks[-1]
    if len(cards) % 2 == 0:
        if len(cards) == 2:
            if not cards[-2].is_honour and cards[-2].rank != 'T':
                manager.set_even_odd(player.seat, trick.suit.name, 0)
                return log(inspect.stack(), cards[-2])
            return log(inspect.stack(), cards[-1])

    manager.set_even_odd(player.seat, trick.suit.name, 1)
    return log(inspect.stack(), cards[-1])


def signal_card(player: Player, manager: object, suit: Suit) -> Card | None:
    """Signal suit preference."""
    if not manager.signal_card[player.seat]:
        suit_cards = player.suit_cards[suit.name]
        for card in suit_cards:
            if not card.is_honour:
                manager.signal_card[player.seat] = card
                return log(inspect.stack(), card)

        other_suit = other_suit_for_signals(suit)
        other_suit_cards = player.suit_cards[other_suit]
        if other_suit_cards:
            manager.signal_card[player.seat] = other_suit_cards[-1]
            return log(inspect.stack(), other_suit_cards[-1])

        for suit_name in SUITS:
            if suit_name != suit.name and suit_name != other_suit:
                final_suit_cards = player.suit_cards[suit_name]
                if final_suit_cards:
                    return log(inspect.stack(), final_suit_cards[-1])
    return None


def surplus_card(player: Player) -> Card | None:
    # Discard if more cards than the opposition
    for suit_name in SUITS:
        if player.unplayed_cards[suit_name]:
            card_count = len(player.unplayed_cards[suit_name])
            if (card_count > len(player.total_unplayed_cards[suit_name])
                    - card_count):
                return log(inspect.stack(),
                           player.unplayed_cards[suit_name][-1])
    return None


def best_discard(player: Player) -> Card:
    # Discard from longest_suit, but match suit lengths to dummy
    manager = global_vars.manager
    longest_suit = player.longest_suit
    longest_suit_cards = player.suit_cards[longest_suit]
    if player.trump_suit:
        if len(longest_suit_cards) > len(player.dummys_unplayed_cards[
                longest_suit]):
            return log(inspect.stack(), longest_suit_cards[-1])

    suits = [suit for suit in SUITS]
    if not player.trump_suit:
        if manager.signal_card[player.seat]:
            suit = manager.signal_card[player.seat].suit.name
            suits.remove(suit)
    for suit in suits:
        cards = player.suit_cards[suit]
        if (len(cards) > len(player.dummys_unplayed_cards[suit]) or
                len(cards) > 1 and cards[0].value == CARD_VALUES['A']):
            return log(inspect.stack(), cards[-1])

    # Last resort - longest_suit
    return log(inspect.stack(), longest_suit_cards[-1])
