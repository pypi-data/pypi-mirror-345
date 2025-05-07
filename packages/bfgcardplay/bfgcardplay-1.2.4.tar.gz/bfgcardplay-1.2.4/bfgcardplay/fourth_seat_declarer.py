"""Fourth seat card play for declarer."""
import random

import inspect
from .logger import log

from bridgeobjects import SUITS, Card, Suit, CARD_VALUES
from bfgdealer import Trick
from .player import Player
from .utilities import (get_list_of_best_scores, trick_card_values,
                        get_long_hand)
from .fourth_seat import FourthSeat
import bfgcardplay.global_variables as global_vars

MODULE_COLOUR = 'cyan'


class FourthSeatDeclarer(FourthSeat):
    def __init__(self, player: Player):
        super().__init__(player)
        self.player = player

    def selected_card(self) -> Card:
        """Return the card if the third seat."""
        player = self.player
        trick = player.board.tricks[-1]
        manager = global_vars.manager

        cards = player.cards_for_trick_suit(trick)

        # Void
        if not cards:
            return self._select_card_if_void()

        # Singleton
        if len(cards) == 1:
            return log(inspect.stack(), cards[0])
        if manager.suit_strategy == '':
            pass

        # Play low if partner is winning trick
        if self._second_player_winning_trick(cards, trick, player.trump_suit):
            return log(inspect.stack(), cards[-1])

        # When to duck - rule of 7
        if not player.trump_suit:
            if trick.suit == player.board.tricks[0].cards[0].suit:
                if self._duck_trick(player, trick, cards):
                    return log(inspect.stack(), cards[-1])
                for card in cards[::-1]:
                    if self.can_win_trick(player, card):
                        return log(inspect.stack(), card)

        # Win trick if possible
        winning_card = self._winning_card(trick)
        if winning_card:
            return winning_card

        # Play smallest card
        return log(inspect.stack(), cards[-1])

    def _select_card_if_void(self) -> Card:
        """Return card if cannot follow suit."""
        player = self.player
        trick = player.board.tricks[-1]

        # Trump if appropriate
        if player.trump_suit:
            values = trick_card_values(trick, player.trump_suit)
            if player.trump_cards:
                if values[0] > values[1] or values[2] > values[1]:
                    for card in player.trump_cards[::-1]:
                        if (card.value + 13 > values[0]
                                and card.value + 13 > values[2]):
                            return log(inspect.stack(), card)

        # Discard if winner in partner's hand
        random_suits = [suit for suit in SUITS]
        if player.trump_suit:
            random_suits.remove(player.trump_suit.name)

        # TODO do not discard an entry to partner's hand
        for suit in SUITS:
            my_cards = player.unplayed_cards[suit]
            partners_cards = player.partners_unplayed_cards[suit]
            (long_hand, short_hand) = get_long_hand(my_cards, partners_cards)
            if my_cards == short_hand:
                for index, card in enumerate(my_cards[::-1]):
                    if player.is_master_card(partners_cards[index]):
                        if card.suit.name in random_suits:
                            random_suits.remove(card.suit.name)
                            break

        random.shuffle(random_suits)
        for suit in random_suits:
            my_cards = player.unplayed_cards[suit]
            partners_cards = player.partners_unplayed_cards[suit]
            if my_cards and partners_cards:
                if len(my_cards) > 1:
                    if player.is_winner_declarer(partners_cards[0]):
                        return log(inspect.stack(), my_cards[-1])

        # Find a card that is not an honour
        for suit in random_suits:
            if player.unplayed_cards[suit]:
                if not player.unplayed_cards[suit][-1].is_honour:
                    return log(inspect.stack(),
                               player.unplayed_cards[suit][-1])

        # Last resort - dump a low card
        for suit in random_suits:
            if player.unplayed_cards[suit]:
                return log(inspect.stack(), player.unplayed_cards[suit][-1])

        # If all else fails play a trump
        return log(inspect.stack(), player.trump_cards[-1])

    def _best_suit(self) -> Suit:
        """Select suit for signal."""
        # TODO handle no points and equal suits
        best_suit = self._strongest_suit()
        return best_suit

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
        if not best_suits:
            return player.trump_suit
        return Suit(random.choice(best_suits))

    def _duck_trick(self, player: Player, trick:
                    Trick, cards: list[Card]) -> bool:
        """Return True if the player is to duck the trick."""
        opponents_unplayed_cards = player.opponents_unplayed_cards[
            trick.suit.name]
        if cards and opponents_unplayed_cards:
            # partners_cards = player.partners_suit_cards[trick.suit.name]
            # partner_can_win = False
            # if partners_cards:
            #     if  partners_cards[0].value > trick.cards[0].value:
            #         partner_can_win = True
            if (len(cards) == 2 and cards[0].value == CARD_VALUES['K'] and
                    Card('A', trick.suit.name) in opponents_unplayed_cards):
                return False
            can_win_trick = (
                cards[0].value > opponents_unplayed_cards[0].value and
                cards[0].value > trick.cards[0].value and
                cards[0].value > trick.cards[2].value)
            if self._rule_of_seven(player, trick) and can_win_trick:
                return False
        return True

    @staticmethod
    def _rule_of_seven(player: Player, trick: Trick) -> bool:
        """Return True if rule of seven applies."""
        our_cards = player.our_cards[trick.suit]
        duck_count = 7 - len(our_cards) - len(player.board.tricks)
        return duck_count < 0
