""" Third seat card play."""

from bridgeobjects import Card, Denomination
from bfgdealer import Trick

from .player import Player
from .utilities import trick_card_values, get_seat

PLAYER_INDEX = 2


class ThirdSeat():
    def __init__(self, player: Player):
        self.player = player
        self.trick = player.board.tricks[-1]
        self.seat = get_seat(self.trick, PLAYER_INDEX)
        self.cards = player.cards_for_trick_suit(self.trick)

    def _ace_is_deprecated(self, trick: Trick, card: Card) -> bool:
        """Return True if the ace is not to be played."""
        player = self.player
        if card.value != 13:
            return False

        king = Card(f'K{card.suit.name}')
        # print(player.card_has_been_played(king), trick.cards[1] == king)
        if self.player.card_has_been_played(king) or trick.cards[1] == king:
            return False

        if len(player.total_unplayed_cards[trick.suit]) < 9:
            return False

        return True

    def _trump_partners_card(self) -> bool:
        """Return True if third hand is to overtump partner's lead."""
        player = self.player
        trick = self.trick
        values = trick_card_values(trick, player.trump_suit)
        opponents_cards = player.opponents_unplayed_cards[trick.suit.name]
        if values[1] > values[0] and trick.cards[0].suit != player.trump_suit:
            return True
        for card in opponents_cards:
            if card.value > trick.cards[0].value:
                return True
        return False

    # def _best_suit(self, player: Player) -> Suit:
    #     """Select suit for signal."""
    #     # TODO handle no points and equal suits
    #     cards = player.hand_cards.list
    #     suit_points = get_suit_strength(cards)
    #     max_points = 0
    #     best_suit = None
    #     for suit in SUITS:
    #         hcp = suit_points[suit]
    #         if hcp > max_points:
    #             max_points = hcp
    #             best_suit = suit
    #     if not best_suit:
    #         return player.longest_suit
    #     return Suit(best_suit)
