""" First seat card play."""

import random

from bridgeobjects import SUITS, Card, Suit, CARD_NAMES

import bfgcardplay.global_variables as global_vars
from .player import Player
from .utilities import get_list_of_best_scores

MODULE_COLOUR = 'red'


class FirstSeat():

    DEFAULT_SCORE = 1
    PARTNERS_SUIT_SCORE = 5
    TENACE_SCORE = 3
    STRENGTH_SCORE = 2
    TRUMP_SCORE = 2
    FROZEN_SUIT_SCORE = 5
    LENGTH_SCORE = 2
    RUFF_AND_DISCARD_SCORE = 5
    VOID_SCORE = 1000
    DRAW_TRUMPS_SCORE = 20
    TOUCHING_HONOURS = 10
    PARTNERS_VOID = 20
    SHORTAGE_SCORE = 10

    def __init__(self, player: Player):
        self.player = player

    def update_manager(self):
        """Update the manager with played cards"""
        player = self.player
        manager = global_vars.manager
        suit = manager.suit_to_develop(player.seat)
        if suit:
            unplayed_cards = player.total_unplayed_cards[suit.name]
            suit_strategy = manager.suit_strategy(player.seat)[suit.name]
            if suit_strategy == 'missing_ace':
                if Card('A', suit.name) not in unplayed_cards:
                    manager.set_suit_strategy(player.seat, suit.name, '')

            if suit_strategy == 'missing_king':
                if Card('K', suit.name) not in unplayed_cards:
                    manager.set_suit_strategy(player.seat, suit.name, '')

            if suit_strategy == 'missing_queen':
                if Card('Q', suit.name) not in unplayed_cards:
                    manager.set_suit_strategy(player.seat, suit.name, '')

            if suit_strategy == 'ruff_in_void' and player.trump_suit:
                partner_seat = player.partner_seat
                if (player.voids[player.seat][player.trump_suit.name] or
                        player.voids[partner_seat][player.trump_suit.name]):
                    manager.set_suit_strategy(
                        player.seat, player.trump_suit.name, '')

            suit = manager.suit_to_develop(player.seat)
            if suit:
                if not player.unplayed_cards[suit]:
                    manager.set_suit_to_develop(player.seat, None)

    def _deprecate_suits(self) -> list[tuple[str, int]]:
        """Assign score to suits based on void."""
        suit_scores = {suit_name: 0 for suit_name in SUITS}
        for suit in SUITS:
            if not self.player.suit_cards[suit]:
                suit_scores[suit] -= self.VOID_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    def _partners_suit(self) -> list[tuple[str, int]]:
        """Assign score to suits based on it being suit partner led."""
        suit_scores = {suit_name: 0 for suit_name in SUITS}
        partners_suit = self._get_partners_suit()
        if partners_suit and not partners_suit == self.player.trump_suit:
            suit_scores[partners_suit.name] += self.PARTNERS_SUIT_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    def _tenace_check(self) -> list[tuple[str, int]]:
        """Assign score to suits based on tenaces in dummy."""
        suit_scores = {suit_name: 0 for suit_name in SUITS}
        dummy_tenaces = self.identify_dummy_tenaces()
        for suit in dummy_tenaces:
            if isinstance(suit, str):
                if self.player.dummy_on_left:
                    # Lead through tenaces
                    suit_scores[suit] += self.TENACE_SCORE
                elif self.player.dummy_on_right:
                    # Lead to tenaces
                    suit_scores[suit] -= self.TENACE_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    def _lead_through_strength(self) -> list[tuple[str, int]]:
        """Assign score to suits where you lead through or to strength."""
        suit_scores = {suit_name: 0 for suit_name in SUITS}
        player = self.player
        if player.dummy_on_left:
            for suit, points in player.dummy_suit_strength.items():
                if points >= 5:
                    suit_scores[suit] += self.STRENGTH_SCORE
        elif player.dummy_on_right:
            for suit, points in player.dummy_suit_strength.items():
                if not player.trump_suit:
                    if points <= 2:
                        suit_scores[suit] += self.STRENGTH_SCORE
                else:
                    if suit != player.trump_suit.name:
                        if points <= 2:
                            suit_scores[suit] += self.STRENGTH_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    def _frozen_suits(self) -> list[tuple[str, int]]:
        """Assign score to suits based on frozen suits."""
        suit_scores = {suit_name: 0 for suit_name in SUITS}
        frozen_suits = []
        for suit in SUITS:
            if self._frozen_suit(suit):
                frozen_suits.append(suit)
        for suit in frozen_suits:
            suit_scores[suit] -= self.FROZEN_SUIT_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    def _frozen_suit(self, suit: str) -> bool:
        """Return true if suit is potentially frozen."""
        cards = self.player.dummys_suit_cards[suit]
        dummy_honours = 0
        hand_honours = 0
        for card in cards:
            if card.is_honour:
                dummy_honours += 1
        if dummy_honours == 1:
            suit_cards = self.player.suit_cards[suit]
            for card in suit_cards:
                if card.is_honour:
                    hand_honours += 1
        if dummy_honours == 1 and hand_honours == 1:
            return True
        return False

    def _long_suits(self) -> list[tuple[str, int]]:
        """Assign score to suits based on length (long)."""
        suit_scores = {suit_name: 0 for suit_name in SUITS}
        for suit in SUITS:
            cards = self.player.suit_cards[suit]
            number_cards = len(cards) - 4
            if number_cards > 0 and cards[0].value >= 12:
                suit_scores[suit] = number_cards * self.LENGTH_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    def _short_suits(self) -> list[tuple[str, int]]:
        """Assign score to suits based on length (short)."""
        suit_scores = {suit_name: 0 for suit_name in SUITS}
        player = self.player
        if player.trump_suit:
            if len(player.trump_cards) > 0:
                for suit in SUITS:
                    number_cards = len(player.suit_cards[suit])
                    if 0 < number_cards < 3:
                        score = (2-number_cards) * self.LENGTH_SCORE
                        suit_scores[suit] = score
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    def _ruff_and_discard(self) -> list[tuple[str, int]]:
        """Assign score to suits based on potential for ruff and discard."""
        suit_scores = {suit_name: 0 for suit_name in SUITS}
        if len(self.player.dummys_suit_cards[self.player.trump_suit.name]) > 0:
            for suit in SUITS:
                if len(self.player.dummys_suit_cards[suit]) == 0:
                    suit_scores[suit] -= self.RUFF_AND_DISCARD_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    def _get_partners_suit(self) -> Suit | None:
        """Return partner's suit if this is 3rd hand on first lead."""
        trick_one = self.player.board.tricks[0]
        if trick_one.leader == self.player.partner_seat:
            opening_lead = trick_one.cards[0]
            if opening_lead.suit != self.player.trump_suit:
                if (opening_lead.value < 7
                        and self.player.suit_cards[opening_lead.suit.name]):
                    return opening_lead.suit
        return None

    def identify_dummy_tenaces(self) -> list[Suit]:
        """Return a list of suits with a tenace in dummy."""
        suits = []
        player = self.player
        for suit, tenace in player.dummy_suit_tenaces.items():
            if player.suit_cards[suit]:
                if tenace and (player.trump_suit
                               and not suit == player.trump_suit.name):
                    tenace_index = CARD_NAMES.index(tenace.name)
                    next_card_name = CARD_NAMES[tenace_index+1]
                    if Card(next_card_name) not in player.hand_cards.list:
                        suits.append(suit)
        return suits

    def _best_suit(self, score_reasons: dict[str, int]) -> Suit:
        """Return the best suit based on score."""
        suit_scores = {suit_name: 0 for suit_name in SUITS}
        player = self.player
        for reason, suits in score_reasons.items():
            for suit in suits:
                suit_scores[suit[0]] += suit[1]

        candidate_suits = get_list_of_best_scores(suit_scores)
        if not candidate_suits:
            suit = self._select_best_suit(player)
            return suit

        allowed_suits = [suit for suit in candidate_suits
                         if player.unplayed_cards[suit]]
        return Suit(random.choice(allowed_suits))

    def _select_best_suit(self, player: Player) -> Suit:
        """Select suit for signal."""
        # TODO handle no points and equal suits
        cards = player.hand_cards.list
        strong_suits = player.get_strongest_suits(cards)
        if len(strong_suits) == 1:
            return Suit(strong_suits[0])
        # TODO get longest if multiple candidates
        long_suit_candidates = {}
        for suit_name in strong_suits:
            cards = player.suit_cards[suit_name]
            long_suit_candidates[suit_name] = len(cards)
        long_suits = get_list_of_best_scores(long_suit_candidates)
        if len(long_suits) == 1:
            return Suit(long_suits[0])
        return Suit(random.choice(long_suits))
