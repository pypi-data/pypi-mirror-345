"""The manager supervises play and holds persistent data.
It is created in global.py."""

from bridgeobjects import SEATS, SUITS, RANKS, Suit

MODULE_COLOUR = 'magenta'

DECLARER_STRATEGY = {
    0: 'Draw trumps and establish long suit',
}

ranks = [rank for rank in RANKS]
ranks.reverse()
RANKS = ranks[:-1]


class Manager():
    def __init__(self):
        # TODO remove print statements
        # print('')
        # print('*'*50)
        # print('')
        self.initialise()

    def initialise(self):
        """Initialise variables at start of board."""
        # print('manager initialised')
        self._board = None
        self.threats = None
        # self.winning_suit = None
        self.long_player = None
        self.draw_trumps = False
        self.missing_king = {seat: {suit_name: False
                                    for suit_name in SUITS} for seat in SEATS}
        self.working_suit = {seat: None for seat in SEATS}
        self._suit_to_develop = {seat: None for seat in SEATS}
        self._suit_strategy = {seat: {suit: ''
                                      for suit in SUITS} for seat in SEATS}
        self.card_to_play = {seat: [] for seat in SEATS}
        self.voids = {seat: {suit_name: False
                             for suit_name in SUITS} for seat in SEATS}
        self.win_trick = {seat: False for seat in SEATS}
        # Defenders
        self.signal_card = {seat: None for seat in SEATS}
        self._like_dislike = {seat: {suit: 0
                                     for suit in SUITS} for seat in SEATS}
        self._even_odd = {seat: {suit: 0 for suit in SUITS} for seat in SEATS}

    def __repr__(self):
        return f'Manager {self.suit_to_develop("N")} {self.suit_strategy("N")}'

    @property
    def board(self):
        """Return the current Board."""
        return self._board

    @board.setter
    def board(self, value):
        """Set the value of the current board"""
        self._board = value

    def suit_to_develop(self, seat: str) -> Suit:
        """Return the suit to develop for a seat."""
        return self._suit_to_develop[seat]

    def set_suit_to_develop(self, seat: str, suit: Suit):
        """Set the suit to develop for a seat."""
        partners_seat = self._partners_seat(seat)
        self._suit_to_develop[seat] = suit
        self._suit_to_develop[partners_seat] = suit

    def suit_strategy(self, seat: str) -> str:
        """Return the suit to develop for a seat."""
        return self._suit_strategy[seat]

    def set_suit_strategy(self, seat: str, suit: str, strategy: str):
        """Set the suit to develop for a seat."""
        partners_seat = self._partners_seat(seat)
        self._suit_strategy[seat][suit] = strategy
        self._suit_strategy[partners_seat][suit] = strategy

    def set_missing_king(self, seat: str, suit: str, missing_king: bool):
        """Set missing king for the suit for a seat."""
        partners_seat = self._partners_seat(seat)
        self.missing_king[seat][suit] = missing_king
        self.missing_king[partners_seat][suit] = missing_king

    def like_dislike(self, seat: str, suit: str) -> int:
        """Return 1 if the player likes the suit and -1 if not."""
        return self._like_dislike[seat][suit]

    def set_like_dislike(self, seat: str, suit: str, value: bool):
        """Set the like_dislike for a seat and suit."""
        self._like_dislike[seat][suit] = value

    def _even_odd(self, seat: str, suit: str) -> bool | None:
        """Return 1 if the player has an even number the suit and -1 if not."""
        return self._even_odd[seat][suit]

    def set_even_odd(self, seat: str, suit: str, value: int):
        """Set even/odd (0/1) for a seat and suit."""
        self._even_odd[seat][suit] = value

    @staticmethod
    def _partners_seat(seat: str) -> str:
        """Return partners's seat name"""
        seat_index = SEATS.index(seat)
        partners_index = (seat_index + 2) % 4
        partners_seat = SEATS[partners_index]
        return partners_seat
