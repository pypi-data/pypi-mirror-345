"""Fourth seat card play."""
import inspect
from .logger import log

from bridgeobjects import Card, Denomination
from bfgdealer import Trick
from .player import Player
from .utilities import trick_card_values

MODULE_COLOUR = 'blue'


class FourthSeat():
    def __init__(self, player: Player):
        self.player = player
        self.trick = player.board.tricks[-1]
        self.cards = player.cards_for_trick_suit(self.trick)

    def _winning_card(self, trick: Trick) -> Card | None:
        """Return the card if can win trick."""
        player = self.player
        cards = self.cards

        values = trick_card_values(trick, player.trump_suit)
        if cards:
            for card in cards[::-1]:
                card_value = card.value
                if card.suit == player.trump_suit:
                    card_value += 13
                if card_value > values[0] and card_value > values[2]:
                    log(inspect.stack(), f'{card}')
                    return card

        # No cards in trick suit, look for trump winner
        elif player.trump_cards:
            for card in player.trump_cards[::-1]:
                if card.value + 13 > values[2]:
                    log(inspect.stack(), f'{card}')
                    return card
        return None

    def _second_player_winning_trick(self, cards: list[Card], trick: Trick,
                                     trumps: Denomination) -> bool:
        """Return True if the second player is winning the trick."""
        values = trick_card_values(trick, trumps)
        if values[1] > values[0] and values[1] > values[2]:
            return True
        return False

    def can_win_trick(self, player, card) -> bool:
        """Return True if card can win trick."""
        trick = player.board.tricks[-1]
        trumps = player.trump_suit
        values = trick_card_values(trick, trumps)
        if values[1] > values[0] and values[1] > values[2]:
            return False
        if card.value > values[0] and card.value > values[2]:
            return True
        return False
