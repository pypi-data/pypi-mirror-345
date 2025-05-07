"""Third seat card play for defender."""

from termcolor import cprint

import inspect
from .logger import log

from bridgeobjects import SUITS, Card, CARD_VALUES, Suit
from .player import Player
from .utilities import (other_suit_for_signals, get_suit_strength,
                        trick_card_values, card_values)

from .third_seat import ThirdSeat
from .defender_play import deduce_partner_void_in_trumps, get_hilo_signal_card
import bfgcardplay.global_variables as global_vars

MODULE_COLOUR = 'blue'

MAXIMUM_TRICKS = 13
TRUMP_VALUE_UPLIFT = 13


class ThirdSeatDefender(ThirdSeat):
    def __init__(self, player: Player):
        super().__init__(player)

    def selected_card(self) -> Card:
        """Return the card if the third seat."""

        # Variables set in third_seat.py
        player = self.player
        trick = self.trick
        seat = self.seat

        cards = self.cards

        # Void
        if not cards:
            return self._select_card_if_void()

        # Singleton
        if len(cards) == 1:
            return log(inspect.stack(), cards[0])

        self._update_manager()

        # win trick if possible
        card = self._winning_card()
        if card:
            return card

        # Play high
        card = self._play_high_card()
        if card:
            player.highest_card[seat][card.suit.name] = card
            return card

        # Unblock suit
        card = self._unblock_suit()
        if card:
            return card

        # Play highest honour if winner
        card = self._play_winning_honour()
        if card:
            return card

        # Play winner if possible
        if (not player.is_winner_defender(trick.cards[0], trick) and
                not trick.cards[0].is_honour and
                cards[0].value > trick.cards[1].value):
            return log(inspect.stack(), cards[0])

        # Doubleton - play the higher
        card = self._top_of_doubleton()
        if card:
            return card

        # signal attitude
        return self._signal_attitude()

    def _update_manager(self):
        player = self.player
        trick = self.trick
        manager = global_vars.manager

        if len(player.board.tricks) == 1:
            manager.signal_card[player.partner_seat] = trick.cards[0]

        if player.trump_suit and trick.suit == player.trump_suit:
            if deduce_partner_void_in_trumps(player):
                player.voids[player.partner_seat][player.trump_suit.name] = True

        suit_name = trick.suit.name
        if player.trick_number == 1:
            if trick.cards[0].is_honour:
                manager.set_like_dislike(player.partner_seat, suit_name, True)

    def _play_high_card(self) -> Card:
        player = self.player
        cards = self.cards
        values = trick_card_values(self.trick, player.trump_suit)
        if self.trick.cards[0].is_honour and cards[0].value - values[0] <= 2:
            return None
        if cards[0].value > values[0] and cards[0].value > values[1]:
            return log(inspect.stack(), cards[0])
        return None

    def _unblock_suit(self) -> Card:
        player = self.player
        trick = self.trick
        cards = self.cards
        if player.trick_number == 1:
            if trick.cards[0].is_honour and len(cards) <= 2:
                return log(inspect.stack(), cards[0])
        if player.trick_number == 2:
            if player.board.tricks[0] == trick.suit:
                if player.board.tricks[0].cards[0].is_honour and len(cards) <= 2:
                    return log(inspect.stack(), cards[0])
        if len(cards) == 3:
            leading_card = trick.cards[0]
            if leading_card.value < cards[0].value:
                return log(inspect.stack(), cards[0])
        return None

    def _play_winning_honour(self) -> Card:
        player = self.player
        trick = self.trick
        # TODO is this too specific?
        suit = trick.suit
        jack = Card('J', suit.name)
        queen = Card('Q', suit.name)
        king = Card('K', suit.name)
        ace = Card('A', suit.name)
        if (trick.cards[0] == jack and
                ace in player.dummys_unplayed_cards[suit.name] and
                player.dummy_on_right and
                king in player.unplayed_cards[suit.name] and
                queen not in player.unplayed_cards[suit.name]):
            return log(inspect.stack(), king)
        return None

    def _top_of_doubleton(self) -> Card:
        player = self.player
        cards = self.cards
        manager = global_vars.manager
        suit_name = self.trick.suit.name
        if len(cards) == 2 and cards[0].value < CARD_VALUES['K']:
            manager.set_like_dislike(player.seat, suit_name, 1)
            return log(inspect.stack(), cards[0])
        return None

    def _signal_attitude(self) -> Card:
        player = self.player
        cards = self.cards
        manager = global_vars.manager
        suit_name = self.trick.suit.name
        if not manager.like_dislike(player.seat, suit_name) or not player.suit_rounds[suit_name]:
            if cards[0].is_honour:
                for card in cards[1:]:
                    if not card.is_honour:
                        if card.value >= CARD_VALUES['7']:
                            manager.set_like_dislike(player.seat, card.suit.name, 1)
                        return log(inspect.stack(), card)
                manager.set_like_dislike(player.seat, cards[-1].suit.name, 0)
        return get_hilo_signal_card(self)

    def _winning_card(self) -> Card | None:
        """Return the card if can win trick."""

        # No cards in trick suit, look for trump winner
        card = self._trump_if_void()
        if card:
            return card

        # Defeat contract if possible
        card = self._defeat_contract()
        if card:
            return card

        # Play winner if long suit
        card = self._winner_in_long_suit()
        if card:
            return card

        # Look for winner
        card = self._look_for_winner()
        if card:
            return card

        card = self._select_card_based_on_position()
        if card:
            return card

        return None

    def _trump_if_void(self) -> Card:
        if self.cards:
            return None
        player = self.player
        values = trick_card_values(self.trick, player.trump_suit)
        if player.trump and player.trump_cards:
            for card in player.trump_cards[::-1]:
                if (card.value + TRUMP_VALUE_UPLIFT > values[0] + 1 and
                        card.value + TRUMP_VALUE_UPLIFT > values[1]):
                    return log(inspect.stack(), card)
        return None

    def _defeat_contract(self) -> Card:
        player = self.player
        trick = self.trick
        if (player.is_winner_defender(self.cards[0], trick) and
                not player.is_winner_defender(trick.cards[0], trick) and
                player.defenders_tricks >= MAXIMUM_TRICKS - player.declarers_target):
            return log(inspect.stack(), self.cards[0])
        return None

    def _winner_in_long_suit(self) -> Card:
        player = self.player
        trick = self.trick
        cards = self.cards

        # Play winner if all winners
        card = self._all_winners_in_long_suit()
        if card:
            return card

        if len(cards) >= 5:
            for card in cards[::-1]:
                if player.is_winner_defender(trick.cards[0], trick):
                    return log(inspect.stack(), cards[-1])

                if player.is_winner_defender(card, trick):
                    return log(inspect.stack(), card)
        return None

    def _all_winners_in_long_suit(self) -> Card | None:
        # Play winner if all winners
        player = self.player
        trick = self.trick
        cards = self.cards

        winners = False
        dummys_cards = player.dummys_unplayed_cards[trick.suit.name]
        total_unplayed_cards = player.total_unplayed_cards[trick.suit.name]
        if len(cards) + len(dummys_cards) == len(total_unplayed_cards):
            winners = True
            for index, card in enumerate(dummys_cards):
                if index < len(self.cards):
                    if card.value > self.cards[index].value:
                        winners = False
                        break
        if winners:
            return log(inspect.stack(), cards[0])
        return None

    def _look_for_winner(self) -> Card:
        player = self.player
        trick = self.trick
        if not player.is_winner_defender(trick.cards[0], trick):
            top_touching_honour = player.touching_honours_in_hand(player.hand, trick.suit.name)
            if top_touching_honour and top_touching_honour.value > trick.cards[1].value:
                return log(inspect.stack(), top_touching_honour)
        return None

    def _select_card_based_on_position(self) -> Card:
        player = self.player
        if not player.dummy_on_left:
            return None

        cards = self.cards
        trick = self.trick
        # Win trick if possible
        my_values = card_values(cards)
        for index, value in enumerate(my_values[::-1]):
            if value > trick.cards[1].value:
                return log(inspect.stack(), cards[::-1][index])

        my_short_cards = [card for card in cards]
        for index, test_card in enumerate(my_short_cards[::-1]):
            # If dummy on left and can win, do so
            card = self._dummy_on_left(test_card)
            if card:
                return card

            card = self._dummy_tenace_not_dominated(test_card, index)
            if card:
                return card
        return None

    def _get_card_value(self, card) -> int:
        card_value = card.value
        # trick card values already adjusted for trumps
        if card.suit == self.player.trump_suit:
            card_value += TRUMP_VALUE_UPLIFT
        return card_value

    def _dummy_on_left(self, card) -> Card:
        player = self.player
        trick = self.trick

        if player.dummys_unplayed_cards[trick.suit.name]:
            values = trick_card_values(trick, player.trump_suit)
            if values[1] > values[0]:
                card_value = self._get_card_value(card)
                if card_value > player.dummys_unplayed_cards[trick.suit.name][0].value:
                    return log(inspect.stack(), card)
        return None

    def _dummy_tenace_not_dominated(self, card, index) -> Card:
        player = self.player
        card_value = self._get_card_value(card)
        values = trick_card_values(self.trick, player.trump_suit)
        if (card_value > values[0] + 3 and
                card_value > values[1] and
                len(self.cards) > index + 1 and
                card.value != self.cards[index+1].value + 1):
            if (not self._seat_dominates_left_hand_dummy_tenace(card) and
                    not self._ace_is_deprecated(self.trick, card)):
                return log(inspect.stack(), card)
        return None

    def _seat_dominates_left_hand_dummy_tenace(self, card: Card) -> bool:
        """Return True if hand dominated dummies tenace in that suit."""
        if self.player.dummy_on_left:
            return False
        tenace = self.player.dummy_suit_tenaces[card.suit.name]
        if tenace:
            if card.value > tenace.value:
                return True
        return False

    def _select_card_if_void(self) -> Card:
        """Return card if cannot follow suit."""
        player = self.player
        trick = self.trick
        # Trump if appropriate
        if player.trump_suit:
            values = trick_card_values(trick, player.trump_suit)
            if player.trump_cards:
                unplayed_cards = player.total_unplayed_cards[trick.suit.name]
                if unplayed_cards:
                    ic(values)
                    if (values[1] > values[0] or
                            trick.cards[0].value < unplayed_cards[0].value):
                        for card in player.trump_cards[::-1]:
                            if card.value+13 > values[1]:
                                return log(inspect.stack(), card)

        # Signal suit preference first time it is led."""
        if len(player.board.tricks) == 1:
            signal_card = self._signal_on_first_lead()
            if signal_card:
                return signal_card

        best_suit = self._best_suit(player)
        other_suit = other_suit_for_signals(best_suit)
        if other_suit != player.trump_suit:
            other_suit_cards = player.suit_cards[other_suit]
            if other_suit_cards and not other_suit_cards[-1].is_honour:
                return log(inspect.stack(), other_suit_cards[-1])

        long_suit_cards = {}
        selected_card = None
        for suit in SUITS:
            cards = player.suit_cards[suit]
            long_suit_cards[suit] = len(cards)
            if player.trump_suit and suit != player.trump_suit.name:
                if cards and not cards[-1].is_honour:
                    selected_card = cards[-1]
        if selected_card:
            return log(inspect.stack(), selected_card)

        for suit_name in SUITS:
            cards = player.unplayed_cards[suit]
            dummys_cards = player.dummys_unplayed_cards[suit]
            if len(cards) > len(dummys_cards):
                return log(inspect.stack(), cards[-1])

            # if suit_name != best_suit.name and suit_name != other_suit:
            #     final_suit_cards = player.suit_cards[suit_name]
            #     if final_suit_cards:
            #         return log(inspect.stack(), final_suit_cards[-1])

        # print(f'{player.suit_cards[suit][0]=}')
        max_length = 0
        for suit in SUITS:
            if long_suit_cards[suit] > max_length:
                max_length = long_suit_cards[suit]
                long_suit = suit
        return log(inspect.stack(), player.suit_cards[long_suit][-1])

    def _signal_on_first_lead(self) -> Card | None:
        """Return a card if it is first time that partner led it."""
        player = self.player
        trick = self.trick
        suits_already_signed = []
        if player.trump_suit:
            suits_already_signed.append(player.trump_suit)
        for board_trick in player.board.tricks:
            if board_trick.leader == player.partner_seat and board_trick != trick:
                suits_already_signed.append(board_trick.start_suit)

        if trick.start_suit not in suits_already_signed:
            suit = self._best_suit(player)
            suit_cards = player.suit_cards[suit.name]
            for card in suit_cards:
                if not card.is_honour:
                    return log(inspect.stack(), card)
        return None

    def _best_suit(self, player: Player) -> Suit:
        """Select suit for signal."""
        # TODO handle no points and equal suits
        cards = player.hand_cards.list
        suit_points = get_suit_strength(cards)
        max_points = 0
        best_suit = None
        for suit in SUITS:
            if player.trump_suit and suit == player.trump_suit.name:
                continue
            hcp = suit_points[suit]
            if hcp > max_points:
                max_points = hcp
                best_suit = suit
        if not best_suit:
            return player.longest_suit
        return Suit(best_suit)
