"""Second seat card play for defender."""

import inspect

from .logger import log

from bridgeobjects import Card, CARD_VALUES, SUITS, Suit
import bfgcardplay.global_variables as global_vars
from .player import Player
from .utilities import get_suit_strength
from .second_seat import SecondSeat
from .defender_play import (get_hilo_signal_card, signal_card, surplus_card,
                            best_discard)
from .data_classes import SuitCards

MODULE_COLOUR = 'green'


class SecondSeatDefender(SecondSeat):
    def __init__(self, player: Player):
        super().__init__(player)

    def selected_card(self) -> Card:
        """Return the card if the second seat."""
        player = self.player
        trick = self.trick
        cards = self.cards

        # Singleton
        if len(cards) == 1:
            return log(inspect.stack(), cards[0])

        # Void
        if not cards:
            return self._select_card_if_void()

        if (player.is_winner_defender(cards[0], trick) and
                len(player.dummys_unplayed_cards[trick.suit.name]) <= 2):
            return log(inspect.stack(), cards[0])

        # Cover honour with honour
        card = self._cover_honour_with_honour()
        if card:
            return card

        # If winner and last opportunity to play it
        card = self._play_winner_if_last_opportunity()
        if card:
            return card

        # Play honour if higher honour in dummy
        card = self._beat_dummys_honour()
        if card:
            return card

        # Win trick if possible
        card = self._play_winner()
        if card:
            return card

        # Play K if doubleton
        card = self._play_doubleton_king()
        if card:
            return card

        # Signal even/odd
        card = self._signal_even_odd()
        if card:
            return card

        # Play lowest card
        return log(inspect.stack(), cards[-1])

    def _play_winner_if_last_opportunity(self) -> Card:
        player = self.player
        cards = self.cards
        trick = self.trick
        if player.trump_suit and cards:
            opponents_cards = player.opponents_unplayed_cards[trick.suit.name]
            if opponents_cards:
                if player.is_winner_defender(cards[0], trick):
                    return log(inspect.stack(), cards[0])

        # else:  # TODO add something for NT contracts
        #         for card in cards[::-1]:
        #             if card.value > trick.cards[0].value:
        #                 return card
        return None

    def _play_winner(self) -> Card:
        player = self.player
        cards = self.cards
        suit = self.trick.suit.name
        if self.trick.cards[0].value > player.unplayed_cards[suit][0].value:
            return None

        if player.trick_number >= 9:
            if not player.dummys_unplayed_cards[suit]:
                dummys_top_value = 0
            else:
                dummys_top_value = player.dummys_unplayed_cards[suit][0].value

            dummy_safe = ((player.dummy_on_right and
                          cards[0].value < dummys_top_value) or
                          (player.dummy_on_left and
                          cards[0].value > dummys_top_value))
            if dummy_safe:
                return log(inspect.stack(), cards[0])
        return None

    def _play_doubleton_king(self) -> Card:
        player = self.player
        suit = self.trick.suit.name
        (ace, king) = SuitCards(suit).cards('A', 'K')
        ace_safe = (
            player.dummy_on_right
            and ace in player.dummys_unplayed_cards[suit]
            or player.dummy_on_left
            and ace not in player.dummys_unplayed_cards[suit])
        if (len(player.unplayed_cards) == 2
                and self.cards[0] == king and ace_safe):
            return log(inspect.stack(), king)
        return None

    def _signal_even_odd(self) -> Card:
        player = self.player
        if not self.trick.suit == player.trump_suit:
            if len(player.unplayed_cards) > 2 and not self.cards[0].is_honour:
                card = get_hilo_signal_card(self)
                if card:
                    return card
        return None

    def _cover_honour_with_honour(self) -> Card:
        # TODO see this web site http://www.rpbridge.net/4l00.htm
        player = self.player
        cards = self.cards
        trick = self.trick
        cover_allowed = True
        if player.dummy_on_right:
            if player.dummy_holds_adjacent_card(trick.cards[0]):
                cover_allowed = False

        if cover_allowed and trick.cards[0].value >= CARD_VALUES['9']:
            # nine or above
            if len(cards) >= 2:
                if cards[1].value >= CARD_VALUES['T']:
                    for card in cards[::-1]:
                        if card.value > trick.cards[0].value:
                            return log(inspect.stack(), card)
        return None

    def _beat_dummys_honour(self) -> Card:
        player = self.player
        suit_name = self.trick.suit.name
        if player.dummy_on_right:
            for card in self.cards:
                if card.is_honour and card.rank != 'A':
                    value = card.value
                    test_card = Card(CARD_VALUES[value+1], suit_name)
                    if test_card in player.dummys_unplayed_cards[suit_name]:
                        return log(inspect.stack(), card)
        return None

    def _select_card_if_void(self) -> Card:
        """Return card if cannot follow suit."""
        player = self.player
        manager = global_vars.manager
        if (player.trump_suit and player.unplayed_cards[player.trump_suit]
                and player.is_defender):
            return log(inspect.stack(),
                       player.unplayed_cards[player.trump_suit][-1])

        best_suit = self._best_suit(player)

        # Signal suit preference."""
        card = signal_card(player, manager, best_suit)
        if card:
            return log(inspect.stack(), card)

        # Discard if more cards than the opposition
        card = surplus_card(player)
        if card:
            return log(inspect.stack(), card)

        # Best discard
        return best_discard(player)

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
