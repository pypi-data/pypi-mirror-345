"""Second seat card play."""

import inspect

from bridgeobjects import SUITS, Card, Suit
from bfgdealer import Trick
from .logger import log

import bfgcardplay.global_variables as global_vars
from .player import Player
from .utilities import other_suit_for_signals, get_suit_strength


class SecondSeat():
    def __init__(self, player: Player):
        self.player = player
        self.trick = player.board.tricks[-1]
        self.cards = player.cards_for_trick_suit(self.trick)

    def _select_card_if_void(self, player: Player, trick: Trick) -> Card:
        """Return card if cannot follow suit."""
        trick = self.trick
        manager = global_vars.manager
        # Trump if appropriate
        if (player.trump_suit and
                player.unplayed_cards[player.trump_suit] and
                not player.is_defender):
            if not player.opponents_trumps:
                return log(inspect.stack(), player.unplayed_cards[player.trump_suit][-1])
            elif len(player.total_unplayed_cards[trick.suit.name]) > 7:  # TODO crude
                return log(inspect.stack(), player.unplayed_cards[player.trump_suit][-1])
            else:
                return log(inspect.stack(), player.unplayed_cards[player.trump_suit][0])

        suit = self._best_suit(player)

        # Signal suit preference."""
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

        for suit_name in SUITS:
            if player.unplayed_cards[suit]:
                card_count = len(player.unplayed_cards[suit])
                if card_count > len(player.total_unplayed_cards[suit]) - card_count:
                    return log(inspect.stack(), player.unplayed_cards[suit][-1])
        return log(inspect.stack(), player.suit_cards[suit.name][-1])

    def _best_suit(self, player: Player) -> Suit:
        """Select suit for signal."""
        # TODO handle no points and equal suits
        cards = player.hand_cards.list
        suit_points = get_suit_strength(cards)
        max_points = 0
        best_suit = None
        for suit in SUITS:
            hcp = suit_points[suit]
            if hcp > max_points:
                max_points = hcp
                best_suit = suit
        if not best_suit:
            return player.longest_suit
        return Suit(best_suit)
