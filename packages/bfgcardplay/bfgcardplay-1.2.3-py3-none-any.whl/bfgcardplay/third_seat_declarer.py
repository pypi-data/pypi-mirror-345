"""Third seat card play for declarer."""

from bridgeobjects import SUITS, Card, Suit

import inspect

from .logger import log

import bfgcardplay.global_variables as global_vars
from .player import Player, SuitCards
from .third_seat import ThirdSeat
from .declarer_play import card_combinations
from .utilities import trick_card_values, play_lowest_winning_card


class ThirdSeatDeclarer(ThirdSeat):
    def __init__(self, player: Player):
        super().__init__(player)

    def selected_card(self) -> Card:
        """Return the card if the third seat."""

        # Variables set in third_seat.py
        player = self.player
        trick = self.trick
        cards = self.cards

        manager = global_vars.manager

        # Void
        if not cards:
            return self._select_card_if_void()

        # Singleton
        if len(cards) == 1:
            return log(inspect.stack(), cards[0])

        # Choice of card has already been made
        if manager.card_to_play[player.seat]:
            card = manager.card_to_play[player.seat]
            manager.card_to_play[player.seat] = None
            return log(inspect.stack(), card)

        # This is a suit to develop
        suit_to_develop = manager.suit_to_develop(player.seat)
        if (suit_to_develop and
                suit_to_develop == trick.suit and
                player.suit_cards[suit_to_develop]):
            card = self._select_card_in_suit_to_develop(suit_to_develop)
            return card

        # Win trick if possible
        winning_card = self._get_winning_card()
        if winning_card:
            return winning_card

        # Cover honour with honour
        if (trick.cards[1].is_honour and
                trick.cards[1].value > trick.cards[0].value):
            for card in cards[::-1]:
                if card.value > trick.cards[1].value:
                    return log(inspect.stack(), card)

        return log(inspect.stack(), cards[-1])

    def _select_card_in_suit_to_develop(self, suit: Suit) -> Card:
        """Return the card from a suit to develop."""
        player = self.player
        trick = self.trick
        manager = global_vars.manager
        cards = player.suit_cards[suit.name]

        # Win trick if possible
        card = self._manager_win_trick(suit)
        if card:
            return card

        # Missing Ace
        card = self._missing_ace(suit)
        if card:
            return card

        # Holds all the winners
        if player.holds_all_winners_in_suit(suit, trick):
            return log(inspect.stack(), cards[0])

        # Missing King
        card = self._missing_king(suit)
        if card:
            return card

        # Missing Queen
        card = self._missing_queen(suit)
        if card:
            return card

        # Play top card if winner and suit nearly played out
        card = self._play_suit_out()
        if card:
            return card

        # Play next to top card if winner
        if (cards[0].is_honour and
                cards[0].value == cards[1].value + 1 and
                cards[1].value > trick.cards[1].value):
            return log(inspect.stack(), cards[1])

        # Play bottom of tenace if missing King
        missing_king = manager.missing_king[player.seat][suit.name]
        if player.is_tenace(cards[0], cards[1]) and missing_king:
            return log(inspect.stack(), cards[1])

        # Force out honour
        opps_unplayed_cards = player.opponents_unplayed_cards[suit.name]
        if len(cards) > 1 and len(opps_unplayed_cards) > 1:
            if (cards[1].value > opps_unplayed_cards[1].value and
                    cards[1].value > trick.cards[1].value):
                return log(inspect.stack(), cards[1])

        # Play winner if needed to make contract
        tricks_needed = player.tricks_needed - player.declarers_tricks
        if tricks_needed <= player.sure_tricks.count:
            card = play_lowest_winning_card(player, cards, trick)
            if card:
                return log(inspect.stack(), card)

        if len(opps_unplayed_cards) == 1:
            card = play_lowest_winning_card(player, cards, trick)
            if card:
                return log(inspect.stack(), card)

        unplayed_cards = player.unplayed_cards[suit.name]
        partners_unplayed_cards = player.partners_unplayed_cards[suit.name]
        if len(partners_unplayed_cards) < len(unplayed_cards):
            return log(inspect.stack(), cards[-1])

        if not player.is_winner_declarer(trick.cards[0], trick):
            for index, card in enumerate(cards[:-1]):
                if (card.value > trick.cards[1].value and
                        card. value > cards[index+1].value + 1):
                    return log(inspect.stack(), card)

        return log(inspect.stack(), cards[-1])

    def _manager_win_trick(self, suit) -> Card:
        player = self.player
        cards = self.cards
        manager = global_vars.manager
        if manager.win_trick[player.seat]:
            opps_unplayed_cards = player.opponents_unplayed_cards[suit.name]
            manager.win_trick[player.seat] = False
            for card in cards[::-1]:
                if card.value > opps_unplayed_cards[0].value:
                    return log(inspect.stack(), card)
        return None

    def _missing_ace(self, suit) -> Card:
        player = self.player
        manager = global_vars.manager
        if manager.suit_strategy(player.seat)[suit.name] == 'missing_ace':
            if not self.trick.cards[0].is_honour:
                for card in self.cards:
                    if (card.is_honour and
                            card.value > self.trick.cards[1].value):
                        return log(inspect.stack(), card)
        return None

    def _missing_king(self, suit) -> Card:
        player = self.player
        trick = self.trick
        cards = self.cards
        manager = global_vars.manager
        (ace, king, queen, jack) = SuitCards(suit.name).cards('A', 'J')
        missing_king = manager.missing_king[player.seat][suit.name]
        if missing_king:
            if ace in cards and queen not in cards and trick.cards[0] != queen:
                return log(inspect.stack(), ace)
        if manager.suit_strategy(player.seat)[suit.name] == 'missing_king':
            if trick.cards[0] == queen or trick.cards[0] == jack:
                return log(inspect.stack(), cards[-1])
        return None

    def _missing_queen(self, suit) -> Card:
        player = self.player
        manager = global_vars.manager
        (ace, king, queen, jack) = SuitCards(suit.name).cards('A', 'J')
        missing_queen = queen in player.opponents_unplayed_cards[suit.name]
        manage_strategy = manager.suit_strategy(player.seat)[suit.name]
        if (manage_strategy == 'missing_queen' and missing_queen):
            card = self._get_winning_card()
            if card:
                return card
        return None

    def _play_suit_out(self) -> Card:
        player = self.player
        if player.sure_tricks.count == 13 - player.trick_number:
            for card in self.cards[::-1]:
                if player.is_winner_declarer(card, self.trick):
                    return log(inspect.stack(), card)
        return None

    def _get_winning_card(self) -> Card | None:
        """Return a card if it can win the trick."""
        player = self.player
        trick = self.trick
        cards = self.cards

        # Trick cards
        values = trick_card_values(trick, player.trump_suit)

        # Look for tenace about a threat card and play lower card
        (higher_card, lower_card) = player.card_from_tenace_threat()
        if (lower_card and
                lower_card.value > values[0] and
                lower_card.value > values[1]):
            return log(inspect.stack(), lower_card)

        # Is this a suit to develop?
        card = self._card_from_suit_to_develop(values[0])
        if card:
            return card

        # If we hold all the winners, take the trick
        card = self._card_from_all_winners()
        if card:
            return card

        # If we probably hold all the winners, take the trick
        card = self._card_from_probable_winners()
        if card:
            return card

        # Take finesse
        card = card_combinations(player)
        if card:
            return log(inspect.stack(), card)

        card = self._get_card_over_top_of_tenace()
        if card:
            return card

        # Win trick if possible to de-block suit
        card = self._deblock_suit()
        if card:
            return card

        # Cover honour with honour
        card = self._cover_honour_with_honour()
        if card:
            return card

        # Push out honour
        if (cards[0].is_honour and
                not player.is_winner_declarer(cards[0]) and
                len(cards) > 1):
            return log(inspect.stack(), cards[1])

        # Overtake partner if appropriate
        card = self._overtake_partner()
        if card:
            return card

        # Play winner
        card = self._play_winner()
        if card:
            return card

        return None

    def _play_winner(self) -> Card:
        player = self.player
        trick = self.trick
        if not player.is_winner_declarer(trick.cards[0], trick):
            for card in self.cards[::-1]:
                if player.is_winner_declarer(card, trick):
                    return log(inspect.stack(), card)
        return None

    def _deblock_suit(self) -> Card:
        player = self.player
        trick = self.trick
        cards = self.cards
        if trick.cards[0].value < cards[0].value:
            values = trick_card_values(trick, player.trump_suit)
            is_winner = (player.is_winner_declarer(trick.cards[0], trick) and
                         values[0] > values[1])
            if (len(player.partners_unplayed_cards[trick.suit.name]) > 1 and
                    is_winner):
                return log(inspect.stack(), cards[-1])

            our_cards = player.our_unplayed_cards[trick.suit.name]
            partners_length = len(player.partners_unplayed_cards[trick.suit.name])
            my_length = len(player.unplayed_cards[trick.suit.name])
            if (player.is_winner_declarer(our_cards[0], trick) and
                    player.is_winner_declarer(our_cards[1], trick) and
                    my_length < partners_length):
                return log(inspect.stack(), cards[0])
        return None

    def _overtake_partner(self) -> Card:
        player = self.player
        trick = self.trick
        cards = self.cards
        if not player.is_winner_declarer(trick.cards[0], trick):
            values = trick_card_values(trick, player.trump_suit)
            for index, card in enumerate(cards[:-1]):
                card_value = card.value
                # trick card values already adjusted for trumps
                if card.suit == player.trump_suit:
                    card_value += 13

                if (card_value > values[0] + 1 and
                        card_value > values[1] and
                        card.value != cards[index+1].value + 1):
                    if not self._ace_is_deprecated(trick, card):
                        return log(inspect.stack(), card)
        return None

    def _cover_honour_with_honour(self) -> Card:
        trick = self.trick
        if (trick.cards[1].is_honour and
                trick.cards[1].value > trick.cards[0].value):
            for card in self.cards[::-1]:
                if (card.value > trick.cards[0].value and
                        card.value > trick.cards[1].value):
                    return log(inspect.stack(), card)

    def _get_card_over_top_of_tenace(self) -> Card:
        player = self.player
        trick = self.trick
        our_unplayed_cards = player.our_unplayed_cards[trick.suit.name]
        top_in_tenace = player.get_suit_tenaces(our_unplayed_cards)
        if top_in_tenace:
            for card in self.cards:
                if card.value < top_in_tenace.value + 1:
                    return log(inspect.stack(), card)
        return None

    def _card_from_all_winners(self) -> Card:
        player = self.player
        trick = self.trick
        cards = self.cards
        opps_unplayed_cards = player.opponents_unplayed_cards[trick.suit]
        if (player.holds_all_winners_in_suit(trick.suit, trick) or
                player.sure_tricks.count >= 13 - player.trick_number):
            if opps_unplayed_cards:
                if (trick.cards[0].value > opps_unplayed_cards[0].value and
                        trick.cards[0].value > trick.cards[1].value):
                    return log(inspect.stack(), cards[-1])
                else:
                    card = play_lowest_winning_card(player, cards, trick)
                    return log(inspect.stack(), card)
        return None

    def _card_from_probable_winners(self) -> Card:
        player = self.player
        trick = self.trick
        cards = self.cards
        opps_unplayed_cards = player.opponents_unplayed_cards[trick.suit]
        if player.holds_all_winners_in_suit(trick.suit, trick):
            if opps_unplayed_cards:
                if (trick.cards[0].value > opps_unplayed_cards[0].value and
                        trick.cards[0].value > trick.cards[1].value):
                    return log(inspect.stack(), cards[-1])
                else:
                    return log(inspect.stack(), cards[0])
        return None

    def _card_from_suit_to_develop(self, card_value) -> Card:
        player = self.player
        trick = self.trick
        cards = self.cards
        manager = global_vars.manager
        opponents_cards = []
        manage_strategy = manager.suit_strategy(player.seat)[trick.suit.name]
        if (manager.suit_to_develop(player.seat) == trick.suit or
                manage_strategy == 'missing_queen'):
            opponents_cards = player.opponents_unplayed_cards[trick.suit.name]

            card = self._card_from_tenace_in_my_hand(cards)
            if card:
                return card

            if opponents_cards:
                card = self._card_can_win(card_value, opponents_cards[0])
                if card:
                    return card
        return None

    def _card_from_tenace_in_my_hand(self, cards) -> Card:
        player = self.player
        tenace_in_my_hand = player.get_suit_tenaces(cards)
        if tenace_in_my_hand:
            for card in cards:
                if card.value < tenace_in_my_hand.value:
                    return log(inspect.stack(), card)
        return None

    def _card_can_win(self, card_value, opps_card) -> Card:
        cards = self.cards
        for card in cards[::-1]:
            if card.value > card_value + 1 and card.value > opps_card.value:
                return log(inspect.stack(), card)
        return None

    def _select_card_if_void(self) -> Card:
        """Return card if cannot follow suit."""
        player = self.player
        trick = self.trick

        # Trump if appropriate
        if player.trump_suit:
            trumps = player.trump_suit
            if not player.is_winner_declarer(trick.cards[0], trick):
                opponents_trumps = player.opponents_unplayed_cards[trumps]
                if player.trump_cards and not opponents_trumps:
                    return log(inspect.stack(), player.trump_cards[-1])
                if player.trump_cards and opponents_trumps:
                    if self._trump_partners_card():
                        card_value = trick.cards[1].value
                        if trick.cards[1].suit == player.trump_suit:
                            card_value += 13
                        trump_cards = player.unplayed_cards[player.trump_suit]
                        for card in trump_cards[::-1]:
                            if card.value + 13 > card_value:
                                return log(inspect.stack(), card)

        opponents_cards = player.opponents_unplayed_cards[trick.suit.name]

        # Find card to discard
        if player.trump_suit:
            suits = {suit_name: suit for suit_name, suit in SUITS.items()
                     if suit_name != player.trump_suit.name}
        else:
            suits = {suit_name: suit for suit_name, suit in SUITS.items()}

        # Find a loser
        suit_length: dict[str, int] = {}
        for suit_name in suits.keys():
            if player.suit_cards[suit_name]:
                suit_length[suit_name] = len(player.suit_cards[suit_name])
                our_cards = player.our_unplayed_cards[suit_name]
                opponents_cards = player.opponents_unplayed_cards[suit_name]
                if opponents_cards:
                    unplayed_cards = player.unplayed_cards[suit_name]
                    if (our_cards[0].value < opponents_cards[0].value and
                            len(unplayed_cards) > len(opponents_cards) / 2):
                        return log(inspect.stack(),
                                   player.suit_cards[suit_name][-1])
                elif (player.board.contract.denomination.is_suit and
                      not self.player.is_declarer):
                    return log(inspect.stack(),
                               player.suit_cards[suit_name][-1])

        # Only trumps left
        if not suit_length:
            return log(inspect.stack(), player.trump_cards[-1])

        # Return smallest in longest suit
        # TODO we might not want to do this
        sorted_suit_length = {
            key: value for key, value in sorted(suit_length.items(),
                                                key=lambda item: item[1],
                                                reverse=True)
            }
        long_suit = list(sorted_suit_length)[0]
        return log(inspect.stack(), player.suit_cards[long_suit][-1])
