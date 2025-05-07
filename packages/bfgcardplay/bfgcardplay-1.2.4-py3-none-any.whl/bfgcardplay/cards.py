"""Common functionality for cardplay."""

import random

from bridgeobjects import Suit, Card, SUITS
from bfgbidding import Hand

from .utilities import get_list_of_best_scores

MODULE_COLOUR = 'magenta'


class Cards():
    """A class representing a set of cards."""
    def __init__(self, input: list[str] | list[Card] | Hand):
        self.list = []
        self.longest_suit = None
        by_suit = {suit: [] for key, suit in SUITS.items()}
        by_suit_name = {key: [] for key, suit in SUITS.items()}
        self.by_suit = {**by_suit, **by_suit_name}
        self._value = 0
        self._create(input)

    def count(self) -> int:
        """Return the number of cards."""
        return len(self.list)

    def _create(self, input: list[str] | list[Card] | Hand):
        """Create a set of cards"""
        if isinstance(input, Hand):
            cards = input.cards
        elif not isinstance(input, list):
            raise TypeError('Cards must be a list of cards')
        else:
            cards = input

        raw_list = []
        for card in cards:
            if isinstance(card, str):
                card = Card(card)
            raw_list.append(card)
        self.list = self.sort_cards(raw_list)

        self._value = 0
        for card in self.list:
            suit = card.suit
            suit_name = suit.name
            self.by_suit[suit].append(card)
            self.by_suit[suit_name].append(card)
            self._value += card.value
        self.longest_suit = self._longest_suit()

    @staticmethod
    def sort_cards(cards: list[Card]) -> list[Card]:
        """Return a sorted list of cards."""
        return sorted(cards, reverse=True)

    def _longest_suit(self) -> Suit:
        """Return the suit with most cards."""
        suit_dict = {}
        for suit, card_list in self.by_suit.items():
            if isinstance(suit, Suit):
                suit_dict[suit] = len(card_list)
        suits = get_list_of_best_scores(suit_dict)
        suit = random.choice(suits)
        return suit

    @property
    def value(self) -> int:
        """Return the sum of the values of the cards."""
        return self._value
