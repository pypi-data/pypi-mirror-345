# first_seat_declarer_nt.py
""" First seat card play for declarer in NT contracts."""

import random
import inspect

from .logger import log

from bridgeobjects import SUITS, Card, Suit

import bfgcardplay.declarer_play as declarer
import bfgcardplay.global_variables as global_vars
from .utilities import (get_list_of_best_scores, get_suit_strength,
                        play_to_unblock, get_list_of_best_suits)
from .player import Player, Cards
from .first_seat import FirstSeat
from .declarer_play import card_combinations


class FirstSeatDeclarerNT(FirstSeat):
    def __init__(self, player: Player):
        super().__init__(player)

    def selected_card(self) -> Card:
        """Return the card for the first seat."""
        player = self.player
        self.update_manager()
        if len(player.hand.unplayed_cards) == 1:
            return log(inspect.stack(), player.hand.unplayed_cards[0])

        # dashboard = player.dashboard
        # threats = dashboard.threats
        # winners = dashboard.winners
        # suit_lengths = dashboard.suit_lengths
        # extra_winners_length = dashboard.extra_winners_length
        # extra_winners_strength = dashboard.extra_winners_strength

        card = self._select_card_from_manager_suit_to_develop()
        if card:
            return card

        # No strategy established yet so select a suit
        suit = self._select_suit()
        card = self._select_lead_card(suit)
        if card:
            return card

        raise ValueError(f'No cards for {suit}')

    def _select_card_from_manager_suit_to_develop(self) -> Card:
        """Return the selected card from suit to develop."""
        player = self.player
        manager = global_vars.manager
        suit_to_develop = manager.suit_to_develop(player.seat)

        if not suit_to_develop:
            return None

        if player.suit_cards[suit_to_develop]:
            card = card_combinations(player, suit_to_develop.name)
            if card:
                return card

        # Card from suit to develop
        card = self._card_from_suit_to_develop(suit_to_develop)
        if card:
            return card

        return None

    def _card_from_suit_to_develop(self, suit) -> Card:
        """Return card from suit to develop."""
        player = self.player
        manager = global_vars.manager
        if not player.our_unplayed_cards[suit.name]:
            manager.set_suit_to_develop(player.seat, None)
            return None

        if player.suit_cards[suit]:
            card = self._select_card_from_suit_to_develop(suit)
            if card:
                return card
        return None

    def _select_card_from_suit_to_develop(self, suit) -> Card:
        # Play card if suit has missing honours
        card = self._missing_honour(suit)
        if card:
            return card

        # Play a card if suit to develop
        card = self._develop_suit(suit)
        if card:
            return card

        # Play a card if suit has entries
        card = self._card_from_suit_with_entries(suit)
        if card:
            return card

        return None

    def _missing_honour(self, suit) -> Card:
        player = self.player
        manager = global_vars.manager
        if manager.suit_strategy(player.seat)[suit.name] == 'missing_ace':
            card = declarer.lead_to_find_missing_ace(player, suit)
            if card:
                return card
        elif manager.suit_strategy(player.seat)[suit.name] == 'missing_king':
            card = declarer.missing_king(player, suit)
            if card:
                return card
        elif manager.suit_strategy(player.seat)[suit.name] == 'missing_queen':
            card = declarer.missing_queen(player, suit)
            if card:
                return card
        return None

    def _card_from_suit_with_entries(self, suit) -> Card:
        player = self.player
        entries = player.get_entries(player.partners_hand)
        if entries:
            for suit_name, cards in entries.items():
                if cards:
                    if player.suit_cards[suit_name]:
                        card = player.suit_cards[suit_name][-1]
                        return log(inspect.stack(), card)
        return None

    def _develop_suit(self, suit) -> Card:
        player = self.player
        manager = global_vars.manager
        if (len(player.suit_cards[suit]) == 1 and
                not player.partners_suit_cards[suit]):
            card = player.suit_cards[suit][0]
            manager.set_suit_to_develop(player.seat, None)
            return log(inspect.stack(), card)
        return None

    def _select_suit(self) -> Suit:
        """Return the trick lead suit for the declarer in  a suit contract."""
        player = self.player
        manager = global_vars.manager
        if manager.suit_to_develop(player.seat):
            self._check_suit_to_develop()

        # Look for suit to develop
        # cprint(f'{dashboard.tricks_needed=}', MODULE_COLOUR)
        # cprint(f'{dashboard.sure_tricks.count=}', MODULE_COLOUR)
        # cprint(f'{dashboard.sure_tricks.cards=}', MODULE_COLOUR)
        # cprint(f'{player.declarers_tricks=}', MODULE_COLOUR)
        # cprint(f'{dashboard.probable_tricks.cards=}', MODULE_COLOUR)
        # cprint(f'{dashboard.possible_tricks.cards=}', MODULE_COLOUR)
        # # cprint(f'{dashboard.possible_promotions.cards=}', MODULE_COLOUR)

        # Play last winner in case no entry
        suit = self._play_winner_no_entry()
        if suit:
            return suit

        # suit_to_develop has been defined
        suit = manager.suit_to_develop(player.seat)
        if suit and player.unplayed_cards[suit]:
            return log(inspect.stack(), suit)

        # Look for suit to develop
        suit = self._select_suit_to_develop()
        if suit and player.unplayed_cards[suit]:
            return suit

        # This crude logic stops the player cashing their winners early
        suit = self._select_suit_with_winners()
        if suit and player.unplayed_cards[suit]:
            return suit

        suit = self._cross_to_partner()
        if suit:
            return suit

        # Develop longer suits as hands develop
        suit = self._develop_suit_as_play_progresses()
        if suit and player.unplayed_cards[suit]:
            return suit
        # Find suit, but avoid suit if better for opponents to lead
        # suit = self._avoid_suit_with_potential_winner()
        # if suit and player.unplayed_cards[suit]:
        #     return suit

        # Find a suit to develop
        suit = self._find_suit_to_develop()
        if suit and player.unplayed_cards[suit]:
            return suit

        # Find best suit
        return self._select_best_suit()

    def _cross_to_partner(self):
        """Cross to partner if that will force discards."""
        player = self.player
        transfer_hand = False
        for suit in SUITS:
            if (len(player.our_unplayed_cards[suit]) > 0
                    and not player.opponents_unplayed_cards[suit]):
                transfer_hand = True
                if player.unplayed_cards[suit]:
                    return Suit(suit)

        # Transfer to other hand
        if transfer_hand:
            for suit in SUITS:
                if player.partners_unplayed_cards[suit]:
                    unplayed_Cards = player.partners_unplayed_cards[suit][0]
                    if (unplayed_Cards in player.winners[suit] and
                            player.unplayed_cards[suit]):
                        return Suit(suit)
        return None

    def _check_suit_to_develop(self):
        player = self.player
        manager = global_vars.manager
        suit = manager.suit_to_develop(player.seat)
        card = player.unplayed_cards[suit][0]
        if not player.is_master_card(card):
            manager.set_suit_to_develop(player.seat, None)

    def _play_winner_no_entry(self):
        player = self.player
        tricks_needed = player.tricks_needed - player.declarers_tricks
        if tricks_needed <= player.sure_tricks.count:
            for suit in SUITS:
                total_cards = len(player.total_unplayed_cards[suit])
                our_cards = len(player.our_unplayed_cards[suit])
                opponents_length = total_cards - our_cards
                if opponents_length <= 2:
                    if (player.unplayed_cards[suit]
                            and not player.partners_unplayed_cards[suit]):
                        if player.is_winner_declarer(
                                player.unplayed_cards[suit][0]):
                            return log(inspect.stack(), Suit(suit))
        return None

    def _select_suit_to_develop(self) -> Suit:
        player = self.player
        manager = global_vars.manager
        extras_suits = self._find_suits_with_extras()

        if extras_suits:
            suits = {suit: 0 for suit in SUITS}
            for suit in extras_suits:
                suits[suit] = len(extras_suits[suit])
            best_suit = get_list_of_best_scores(suits)
            if len(best_suit) == 1:
                suit = Suit(best_suit[0])
                manager.set_suit_to_develop(player.seat, suit)
                if player.unplayed_cards[suit]:
                    return log(inspect.stack(), suit)
        return None

    def _select_best_suit(self) -> Suit:
        player = self.player
        suit_scores = {suit: 0 for suit in SUITS}
        if len(player.board.tricks) >= 5:
            for suit_name, suit in SUITS.items():
                if suit != player.trump_suit:
                    if player.holds_all_winners_in_suit(suit):
                        suit_scores[suit_name] = 1
        total = 0
        for score in suit_scores.values():
            total += score
        if not total:
            for suit in SUITS:
                our_cards = Cards(player.our_unplayed_cards[suit])
                suit_scores[suit] += (our_cards.value
                                      + len(player.our_unplayed_cards[suit]))
        suits = get_list_of_best_scores(suit_scores)
        if len(suits) == 1 and len(player.unplayed_cards[suits[0]]) > 0:
            return log(inspect.stack(), Suit(suits[0]))
        suit_choices = [suit for suit in SUITS
                        if len(player.unplayed_cards[suit]) > 0]
        suit = Suit(random.choice(suit_choices))
        return log(inspect.stack(), suit)

    def _find_suit_to_develop(self) -> Suit:
        player = self.player
        manager = global_vars.manager
        if not manager.suit_to_develop(player.seat):
            suit_to_develop = self._suit_to_develop()
            if suit_to_develop:
                return log(inspect.stack(), suit_to_develop)
        return None

    def _find_suits_with_extras(self) -> list[Suit]:
        player = self.player
        if player.probable_tricks.count:
            return player.probable_tricks.suits
        return player.possible_tricks.suits

    def _select_suit_with_winners(self):
        """Return"""
        player = self.player
        manager = global_vars.manager

        set_strategy_limit = 1
        if len(player.board.tricks) < 4:
            set_strategy_limit = 7

        # Play
        best_suits = get_list_of_best_suits(player)
        # best_suits = get_list_of_best_scores(winners)
        for suit in best_suits:
            if (player.winners[suit] and
                    player.unplayed_cards[suit] and
                    len(player.our_cards[suit]) >= set_strategy_limit):
                manager.set_suit_strategy(player.seat, suit, 'Play winners')
                return log(inspect.stack(), Suit(suit))
        return None

    def _develop_suit_as_play_progresses(self):
        """Return"""
        player = self.player
        manager = global_vars.manager
        candidate_suits = {}
        if len(player.board.tricks) > 1:
            for suit in SUITS:
                if (len(player.unplayed_cards[suit]) >= 4 or
                        (len(player.partners_unplayed_cards[suit]) >= 4 and
                         len(player.unplayed_cards[suit]) > 0)):
                    points = get_suit_strength(player.our_unplayed_cards[suit])
                    candidate_suits[suit] = len(
                        player.our_unplayed_cards[suit]
                        ) + points[suit]
            if candidate_suits:
                candidates = get_list_of_best_scores(candidate_suits)
                suit = candidates[0]
                manager.set_suit_to_develop(player.seat, Suit(suit))
                for card in player.partners_unplayed_cards[suit]:
                    if card.is_honour and player.is_winner_declarer(card):
                        return log(inspect.stack(), Suit(suit))
        return None

    def _avoid_suit_with_potential_winner(self):
        """Return"""
        player = self.player
        suits = []
        for suit in SUITS:
            if player.unplayed_cards[suit]:
                if not self._potential_winner(suit):
                    suits.append(suit)

        # Must have one suit!
        if not suits:
            for suit in SUITS:
                if player.unplayed_cards[suit]:
                    suits.append(suit)

        if len(suits) == 1:
            return log(inspect.stack(), Suit(suits[0]))
        return None

    def _suit_to_develop(self) -> list[str]:
        """Return a list of suits to develop."""
        player = self.player
        if len(player.board.tricks) > 9:
            return None
        manager = global_vars.manager
        suits_to_develop = self._long_suits_to_develop()
        longest_strongest_suit = self._longest_strongest_suit(suits_to_develop)
        suit = Suit(longest_strongest_suit)
        manager.set_suit_to_develop(player.seat, suit)
        suit_strategy = self._set_suit_strategy(suit)
        manager.set_suit_strategy(player.seat, suit.name, suit_strategy)
        return suit

    def _set_suit_strategy(self, suit: Suit) -> str:
        """Return the suit strategy as a string."""
        player = self.player

        missing_honours = player.missing_honours(suit)
        for missing_honour in missing_honours:
            if missing_honour.rank == 'A':
                return 'missing_ace'
            if missing_honour.rank == 'K':
                return 'missing_king'
            if missing_honour.rank == 'Q':
                return 'missing_queen'
        return ''

    def _long_suits_to_develop(self):
        """Return a list of long suits to develop."""
        player = self.player
        long_suits_to_develop = []
        for suit_name in SUITS:
            declarers_suit_cards = player.declarers_suit_cards[suit_name]
            dummys_suit_cards = player.dummys_suit_cards[suit_name]
            total_cards = len(declarers_suit_cards) + len(dummys_suit_cards)
            if (total_cards >= 6 and (len(declarers_suit_cards) >= 4
                                      or len(dummys_suit_cards) >= 4)):
                long_suits_to_develop.append(suit_name)
        return long_suits_to_develop

    def _longest_strongest_suit(self, suits: list[str]) -> str:
        """Return the longest and strongest suit from a list of suit_names."""
        player = self.player
        manager = global_vars.manager
        candidate_suits = {}
        for suit_name in suits:
            declarers_suit_cards = player.declarers_suit_cards[suit_name]
            dummys_suit_cards = player.dummys_suit_cards[suit_name]
            candidate_suits[suit_name] = len(
                declarers_suit_cards
                ) + len(dummys_suit_cards)
        long_suits = get_list_of_best_scores(candidate_suits)

        if len(long_suits) == 1:
            suit = long_suits[0]
            manager.set_suit_to_develop(player.seat, suit)
            suit_strategy = self._set_suit_strategy(Suit(suit))
            manager.set_suit_strategy(player.seat, suit, suit_strategy)
            return suit

        strong_suits = get_list_of_best_scores(candidate_suits)
        if len(strong_suits) == 1:
            return log(inspect.stack(), strong_suits[0])

        if strong_suits:
            suit = random.choice(strong_suits)
            return log(inspect.stack(), Suit(suit))
        for suit in SUITS:
            if player.winners[suit] and player.unplayed_cards[suit]:
                return log(inspect.stack(), suit)

        suits = []
        for suit in SUITS:
            if player.unplayed_cards[suit]:
                suits.append(suit)
        suit = random.choice(suits)
        return suit

    def _select_lead_card(self, suit: Suit) -> Card | None:
        """Return the selected lead card for declarer."""
        player = self.player
        manager = global_vars.manager
        cards = player.suit_cards[suit.name]
        if not cards:
            return None

        # Card combinations
        card = card_combinations(player, suit.name)
        if card:
            return log(inspect.stack(), card)

        # Play winning cards
        if (manager.suit_strategy(player.seat)[suit.name] == 'Play winners' or
                player.holds_all_winners_in_suit(suit)):
            my_cards = player.unplayed_cards[suit.name]
            partners_cards = player.partners_unplayed_cards[suit.name]
            card = play_to_unblock(my_cards, partners_cards)
            if card:
                return log(inspect.stack(), card)

            if (partners_cards and len(my_cards) > len(partners_cards) and
                    player.is_winner_declarer(partners_cards[0]) and
                    len(partners_cards) > 1):
                return log(inspect.stack(), my_cards[-1])
            for card in cards[::-1]:
                if player.opponents_unplayed_cards[suit.name]:
                    if player.is_winner_declarer(card):
                        return log(inspect.stack(), card)
                else:
                    return log(inspect.stack(), card)

        # Top of touching honours
        for index, card in enumerate(cards[:-1]):
            if card.is_honour and card.value == cards[index+1].value + 1:
                return log(inspect.stack(), card)

        # Top of doubleton
        if len(cards) == 2:
            return log(inspect.stack(), cards[0])

        # Return bottom card
        return log(inspect.stack(), cards[-1])

    def _potential_winner(self, suit: str) -> bool:
        """Return True if the suit has a potential winner."""
        player = self.player
        for cards in [
                player.unplayed_cards[suit],
                player.partners_unplayed_cards[suit]]:
            if (cards and
                    cards[0] != player.total_unplayed_cards[suit][0] and
                    cards[0] == player.total_unplayed_cards[suit][1] and
                    len(cards) >= 2):
                return True
        return False
