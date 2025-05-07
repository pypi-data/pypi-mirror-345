"""Fourth seat card play for defender."""

import random

from bridgeobjects.src.constants import CARD_VALUES

import inspect
from .logger import log

from bridgeobjects import SUITS, Card, Suit
from bfgdealer import Trick
import bfgcardplay.global_variables as global_vars

from .player import Player
from .utilities import (get_list_of_best_scores, get_suit_strength,
                        trick_card_values)
from .fourth_seat import FourthSeat
from .defender_play import (get_hilo_signal_card, signal_card, surplus_card,
                            best_discard)

MODULE_COLOUR = 'cyan'
PLAYER_INDEX = 3


class FourthSeatDefender(FourthSeat):
    def __init__(self, player: Player):
        super().__init__(player)
        self.player = player

    def selected_card(self) -> Card:
        """Return the card if the third seat."""
        player = self.player
        trick = player.board.tricks[-1]

        cards = player.cards_for_trick_suit(trick)

        # Void
        if not cards:
            return self._select_card_if_void(player, trick)

        # Singleton
        if len(cards) == 1:
            return log(inspect.stack(), cards[0])

        # play low if partner is winning trick
        if self._second_player_winning_trick(cards, trick, player.trump_suit):
            return log(inspect.stack(), cards[-1])

        # win trick if possible
        winning_card = self._winning_card(trick)
        unplayed_cards = player.total_unplayed_cards[trick.suit.name]
        if winning_card:
            value = winning_card.value
            play_winner = False
            while value > 1:
                value -= 1
                card = Card(CARD_VALUES[value], trick.suit.name)
                if (card in unplayed_cards and
                        card not in player.dummys_unplayed_cards[
                            trick.suit.name]):
                    play_winner = True
                    break
            if play_winner:
                return log(inspect.stack(), winning_card)

        # Play low if higher card is winner after trick played
        # losing_trick = (trick.cards[0].value > trick.cards[1].value or
        #                     trick.cards[2].value > trick.cards[1].value)
        # if len(cards) == 2 and losing_trick:
        #     winner = True
        #     for card in unplayed_cards:
        #         if card.value > cards[0].value:
        #             winner = False
        #     if winner:
        #         return log(inspect.stack(), cards[1])

        # Signal even/odd
        return get_hilo_signal_card(self)

    def _select_card_if_void(self, player: Player, trick: Trick) -> Card:
        """Return card if cannot follow suit."""
        manager = global_vars.manager

        # Trump if appropriate
        if player.trump_suit:
            values = trick_card_values(trick, player.trump_suit)
            if player.trump_cards:
                if values[0] > values[1] or values[2] > values[1]:
                    for card in player.trump_cards[::-1]:
                        if (card.value + 13 > values[0]
                                and card.value + 13 > values[2]):
                            return log(inspect.stack(), card)

        # Do not signal with winners
        # for suit in SUITS:
        #     for card in player.unplayed_cards[suit]:
        #         if not player.is_master_card(card):
        #             return log(inspect.stack(), card)

        # Signal best suit
        best_suit = self._best_suit()
        card = signal_card(player, manager, best_suit)
        if card:
            if not player.is_master_card(card):
                return log(inspect.stack(), card)

        # Discard if more cards than the opposition
        card = surplus_card(player)
        if card:
            return log(inspect.stack(), card)

        # Best discard
        return log(inspect.stack(), best_discard(player))

    def _best_suit(self) -> Suit:
        """Select suit for signal."""
        # TODO handle no points and equal suits
        player = self.player
        cards = player.hand_cards.list
        suit_points = get_suit_strength(cards)
        max_points = 0
        best_suit = self._strongest_suit()
        return best_suit
        for suit in SUITS:
            if suit != player.trump_suit.name:
                hcp = suit_points[suit]
                if hcp > max_points:
                    max_points = hcp
                    best_suit = suit
        if not best_suit:
            for suit in SUITS:
                if suit != player.trump_suit.name:
                    hcp = suit_points[suit]
                    if hcp > max_points:
                        max_points = hcp
                        best_suit = suit
        if not best_suit:
            return player.trump_suit
        return Suit(best_suit)

    def _strongest_suit(self) -> Suit | None:
        """Return the strongest_suit."""
        player = self.player
        suits = {suit: 0 for suit in SUITS}
        for suit in SUITS:
            cards = player.unplayed_cards[suit]
            for card in cards:
                suits[suit] += card.value
        if player.trump_suit:
            suits[player.trump_suit.name] = 0
        best_suits = get_list_of_best_scores(suits)
        # if not best_suits:
        #     return player.trump_suit
        return Suit(random.choice(best_suits))
