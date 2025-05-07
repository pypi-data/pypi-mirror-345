
import random

from bridgeobjects import Suit, Card, RANKS, SUITS
from bfgbidding import Hand

from .utilities import get_list_of_best_scores


MODULE_COLOUR = 'yellow'


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

    def __repr__(self):
        return f'Cards: {self.by_suit}'

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
            self.by_suit[suit].append(card)
            self.by_suit[suit.name].append(card)
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


class SuitCards():
    """Represent all of the cards in a suit by name."""
    def __init__(self, suit: str):
        self.suit = suit
        self.ace = Card('A', suit)
        self.king = Card('K', suit)
        self.queen = Card('Q', suit)
        self.jack = Card('J', suit)
        self.ten = Card('T', suit)
        self.nine = Card('9', suit)
        self.eight = Card('8', suit)
        self.seven = Card('7', suit)
        self.six = Card('6', suit)
        self.five = Card('5', suit)
        self.four = Card('4', suit)
        self.three = Card('3', suit)
        self.two = Card('2', suit)

    def cards(self, top_rank: str = '', bottom_rank: str = '') -> tuple[Card]:
        """Return a tuple of the cards requested."""
        if not top_rank:
            top_rank = 'A'
        if not bottom_rank:
            bottom_rank = '2'

        cards = []
        ranks = [rank for rank in RANKS]
        ranks.reverse()
        ranks = ranks[:-1]
        top_index = ranks.index(top_rank)
        bottom_index = ranks.index(bottom_rank)
        requested_ranks = ranks[top_index:bottom_index+1]
        for rank in requested_ranks:
            cards.append(Card(rank, self.suit))
        return tuple(cards)

    def sorted_cards(self):
        """Return a list of Cards in descending order by rank."""
        ranks = [rank for rank in RANKS[1:]]
        ranks.reverse()
        cards = [Card(rank, self.suit) for rank in ranks]
        return cards


class CardArray():
    """Data structure for dashboard analyses"""
    def __init__(self, cards: list[Card]):
        self.cards = self.sort_cards(cards)
        self.suits = self._suits_from_cards()

    def _suits_from_cards(self):
        """Return a dict of suit cards."""
        suits = {suit: [] for suit in SUITS}
        for card in self.cards:
            suits[card.suit.name].append(card)
        return suits

    @property
    def count(self):
        """Return the length of cards"""
        return len(self.cards)

    def __repr__(self):
        # cprint(f'{self.cards}', MODULE_COLOUR)
        # cprint(f'{self.suits}', MODULE_COLOUR)
        return ''

    @staticmethod
    def sort_cards(cards: list[Card]) -> list[Card]:
        """Return a sorted list of cards."""
        return sorted(cards, reverse=True)
