"""Second seat card play for declarer."""

from bridgeobjects.src.constants import CARD_VALUES

import inspect

from .logger import log

from bridgeobjects import Card, SUITS, Suit
from .player import Player
from .utilities import get_list_of_best_scores, get_suit_strength
from .second_seat import SecondSeat
import bfgcardplay.global_variables as global_vars

MODULE_COLOUR = 'green'


class SecondSeatDeclarer(SecondSeat):
    def __init__(self, player: Player):
        super().__init__(player)

    def selected_card(self) -> Card:
        """Return the card if the second seat."""
        player = self.player
        trick = self.trick
        cards = self.cards

        # Void
        if not cards:
            return self._select_card_if_void()

        # Singleton
        if len(cards) == 1:
            return log(inspect.stack(), cards[0])

        # Win trick if partner cannot
        card = self._win_trick_if_partner_cannot()
        if card:
            return log(inspect.stack(), card)

        # Look for tenace about a threat card
        (higher_card, lower_card) = player.card_from_tenace_threat()
        if lower_card:
            return log(inspect.stack(), lower_card)

        # Does a tenace exist
        lower_card = player.card_from_tenace()
        if lower_card:
            return log(inspect.stack(), lower_card)

        # Card from suit to develop
        card = self._card_from_suit_to_develop()
        if card:
            return log(inspect.stack(), card)

        # When to duck - rule of 7
        card = self._do_not_duck_if_appropriate()
        if card:
            return log(inspect.stack(), card)

        # Cover honour if own touching honours
        if trick.cards[0].is_honour:
            card = self._cover_honour()
            if card:
                return log(inspect.stack(), card)

        # Play card if it can beat intermediate lead
        card = self._win_over_intermediate_lead()
        if card:
            return log(inspect.stack(), card)

        # Partner is void or only has pips
        card = self._partner_weak()
        if card:
            return log(inspect.stack(), card)

        # Play lowest card
        return log(inspect.stack(), cards[-1])

    def _win_trick_if_partner_cannot(self) -> Card:
        if not self.player.board.contract.denomination.is_suit:
            return None
        player = self.player
        trick = self.trick
        partners_cards = player.partners_unplayed_cards[trick.suit.name]
        if partners_cards and not partners_cards[0].is_honour:
            for card in self.cards[len(partners_cards)-1::-1]:
                if player.is_winner_declarer(card, trick):
                    return log(inspect.stack(), card)
        return None

    def _do_not_duck_if_appropriate(self) -> Card:
        cards = self.cards
        duck_trick = self._can_duck_trick()
        if not duck_trick:
            if cards[0].value > self.player.board.tricks[-1].cards[0].value:
                return log(inspect.stack(), cards[0])
        return None

    def _can_duck_trick(self) -> bool:
        player = self.player
        if not player.trump_suit:
            return self._duck_trick()
        return False

    def _duck_trick(self) -> bool:
        """Return True if the player is to duck the trick."""
        player = self.player
        trick = self.trick
        cards = self.cards
        opponents_unplayed_cards = player.opponents_unplayed_cards[
            trick.suit.name]
        if cards and opponents_unplayed_cards:
            partners_cards = player.partners_suit_cards[trick.suit.name]
            partner_can_win = False
            if partners_cards:
                if partners_cards[0].value > trick.cards[0].value:
                    partner_can_win = True
            can_win_trick = (
                cards[0].value > opponents_unplayed_cards[0].value and
                cards[0].value > trick.cards[0].value and
                not partner_can_win)
            if self._rule_of_seven() and can_win_trick:
                return False
        return True

    def _cover_honour(self) -> Card:
        player = self.player
        trick = self.trick
        cards = self.cards

        # Cover honour if own touching honours
        touching_honours = player.touching_honours(
            player.our_unplayed_cards[trick.suit.name])
        my_unplayed_cards = len(player.unplayed_cards[trick.suit.name])
        partners_unplayed_cards = len(
            player.partners_unplayed_cards[trick.suit.name])
        if (trick.cards[0].value >= CARD_VALUES['T'] and
                trick.cards[0].value < cards[0].value and
                cards[0].is_honour and
                touching_honours and
                my_unplayed_cards <= partners_unplayed_cards):
            return log(inspect.stack(), cards[0])

        # TODO see this web site http://www.rpbridge.net/4l00.htm
        duck_trick = self._can_duck_trick()
        if trick.cards[0].value >= CARD_VALUES['T'] and not duck_trick:
            for card in player.suit_cards[trick.suit.name][::-1]:
                if card.value > trick.cards[0].value:
                    return log(inspect.stack(), card)

        if (len(cards) > 1 and
                cards[0].value == cards[1].value + 1 and
                CARD_VALUES['A'] > cards[1].value >= CARD_VALUES['T']):
            return log(inspect.stack(), cards[1])
        return None

    def _win_over_intermediate_lead(self) -> Card:
        trick = self.trick
        cards = self.cards
        if trick.cards[0].value >= CARD_VALUES['9']:  # nine or above
            if len(cards) >= 2:
                if cards[1].value >= CARD_VALUES['T']:
                    for card in cards[::-1]:
                        if card.value > trick.cards[0].value:
                            return log(inspect.stack(), card)
        return None

    def _partner_weak(self) -> Card:
        player = self.player
        if not player.board.contract.denomination.is_suit:
            return None
        trick = self.trick
        partner_void = True
        if player.partners_unplayed_cards[trick.suit.name]:
            partner_void = False
            partners_top_card = player.partners_unplayed_cards[
                trick.suit.name][0]
            partner_honour = partners_top_card.is_honour

        if partner_void or not partner_honour:
            for card in self.cards[::-1]:
                if card.is_honour and card.value > trick.cards[0].value:
                    return log(inspect.stack(), card)
        return None

    def _rule_of_seven(self) -> bool:
        """Return True if rule of seven applies."""
        trick = self.trick
        player = self.player
        our_cards = player.our_cards[trick.suit]
        duck_count = 7 - len(our_cards) - len(player.board.tricks)
        return duck_count < 0

    def _card_from_suit_to_develop(self):
        """Return card from a suit to develop."""
        player = self.player
        manager = global_vars.manager
        trick = player.board.tricks[-1]
        suit_to_develop = manager.suit_to_develop(player.seat)
        if suit_to_develop:
            for card in player.unplayed_cards[trick.suit.name][::-1]:
                if player.is_winner_declarer(card, trick):
                    return log(inspect.stack(), card)
        return None

    def _select_card_if_void(self) -> Card:
        """Return card if cannot follow suit."""
        player = self.player

        card = self._trump_if_appropriate()
        if card:
            return card

        for suit_name in SUITS:
            if player.unplayed_cards[suit_name]:
                card_count = len(player.unplayed_cards[suit_name])
                if card_count > len(
                        player.total_unplayed_cards[suit_name]) - card_count:
                    return log(inspect.stack(),
                               player.unplayed_cards[suit_name][-1])

        lengths = {suit: 0 for suit in SUITS}
        for suit in SUITS:
            if player.trump_suit and suit == player.trump_suit.name:
                lengths[suit] = 0
            else:
                lengths[suit] = len(player.unplayed_cards[suit])

        long_suits = get_list_of_best_scores(lengths)
        if player.unplayed_cards[long_suits[0]]:
            return log(inspect.stack(),
                       player.unplayed_cards[long_suits[0]][-1])

        return log(inspect.stack(),
                   player.unplayed_cards[player.trump_suit.name][-1])

    def _trump_if_appropriate(self) -> Suit | None:
        """Trump if appropriate."""
        player = self.player
        trick = player.board.tricks[-1]
        suit_name = trick.suit.name

        if player.trump_suit and player.unplayed_cards[player.trump_suit]:
            defender_is_void = (
                player.voids[player.right_hand_seat][suit_name] or
                player.voids[player.left_hand_seat][suit_name])
            if (len(player.opponents_unplayed_cards[suit_name]) >= 4
                    and not defender_is_void):
                trump_low = True
            else:
                trump_low = False

            partners_cards = player.partners_unplayed_cards[suit_name]
            partners_trumps = player.partners_unplayed_cards[
                player.trump_suit.name]
            my_trumps = player.unplayed_cards[player.trump_suit]
            if not partners_cards and partners_trumps:
                if len(my_trumps) > len(partners_trumps):
                    return None

            if not partners_cards or not player.is_winner_declarer(
                    partners_cards[0], trick):
                if not player.opponents_trumps:
                    return log(inspect.stack(), my_trumps[-1])
                elif trump_low:
                    return log(inspect.stack(), my_trumps[-1])
                else:
                    return log(inspect.stack(), my_trumps[0])
        return None

    def _best_suit(self, player: Player) -> Suit:
        """Select suit for signal."""
        # TODO handle no points and equal suits
        cards = player.hand_cards.list
        suit_points = get_suit_strength(cards)
        max_points = 0
        best_suit = None
        for suit in SUITS:
            if player.trump_suit and suit != player.trump_suit.name:
                hcp = 0
            else:
                hcp = suit_points[suit]
                if hcp > max_points:
                    max_points = hcp
                    best_suit = suit
        if best_suit:
            return Suit(best_suit)
        return player.longest_suit
