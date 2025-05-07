# first_seat_declarer.py
""" First seat card play for declarer."""

import inspect
from .logger import log

from bridgeobjects import SUITS, Card, Suit

import bfgcardplay.global_variables as global_vars
from .utilities import get_list_of_best_scores
from .player import Player
from .first_seat import FirstSeat
from .declarer_play import card_combinations

ALL_WINNERS = 5


def return_and_print(obj: object, text: str, can_print: bool) -> object:
    """Print text and return object."""
    if can_print:
        print(f'{obj} {text}')
    return obj


class FirstSeatDeclarerSuit(FirstSeat):
    def __init__(self, player: Player):
        super().__init__(player)

    def selected_card(self) -> Card:
        """Return the card for the first seat."""
        player = self.player

        if len(player.hand.unplayed_cards) == 1:
            return log(inspect.stack(), player.hand.unplayed_cards[0])

        card = self._play_out_winners()
        if card:
            return card

        card = self._manager_force_play_card()
        if card:
            return card

        card = self._card_from_suit_to_develop()
        if card:
            return card

        suit = self._select_suit()
        if not player.suit_cards[suit.name]:
            raise ValueError(f'No cards for {suit}')
        card = self._select_lead_card(suit)
        return card

    def _play_out_winners(self):
        # +1 because the next trick has already been created
        player = self.player
        if player.winner_count >= 13 - len(player.board.tricks) + 1:
            card = self._play_all_winners()
            if card:
                return card
        return None

    def _manager_force_play_card(self) -> Card:
        player = self.player
        manager = global_vars.manager
        self.update_manager()

        if manager.card_to_play[player.seat]:
            card = manager.card_to_play[player.seat][0]
            manager.card_to_play[player.seat].pop(0)
            if (manager.suit_to_develop(player.seat)
                    and manager.card_to_play[player.seat]):
                manager.card_to_play[player.seat] = player.suit_cards[
                    manager.suit_to_develop][-1]
            return log(inspect.stack(), card)
        return None

    def _card_from_suit_to_develop(self) -> Card:
        player = self.player
        manager = global_vars.manager
        suit_to_develop = manager.suit_to_develop(player.seat)
        if suit_to_develop:
            if player.unplayed_cards[suit_to_develop.name]:
                strategy = manager.suit_strategy(player.seat)[
                    suit_to_develop.name]
                if strategy == 'ruff_in_short_hand':
                    if player.threats[suit_to_develop.name]:
                        if player.is_declarer:
                            my_cards = player.unplayed_cards[
                                suit_to_develop.name]
                            dummys_cards = player.dummys_unplayed_cards[
                                suit_to_develop.name]
                            if dummys_cards:
                                value = my_cards[0].value
                                if dummys_cards[0].value > value:
                                    return log(inspect.stack(), my_cards[-1])
                        card = player.unplayed_cards[suit_to_develop.name][0]
                        return log(inspect.stack(), card)
        return None

    def _select_suit(self) -> Suit:
        """Return the trick lead suit for the declarer in  a suit contract."""
        player = self.player
        manager = global_vars.manager

        # Draw trumps?
        can_draw_trumps = self._can_draw_trumps()
        if player.opponents_trumps and can_draw_trumps:
            return log(inspect.stack(), player.trump_suit)

        # Suit to develop
        suit = self._define_suit_to_develop()
        if suit:
            return suit
        else:
            self._define_suit_with_winners()

        # Play master
        suit = self._select_suit_with_master()
        if suit:
            return suit

        # Long suits
        suit = self._lead_towards_tenace()
        if suit:
            return suit

        # Play suit to develop
        suit = manager.suit_to_develop(player.seat)
        if suit and player.unplayed_cards[suit.name]:
            return log(inspect.stack(), suit)
        self._update_manager_with_threats()

        # Suit to develop
        suit = self._get_suit_to_develop()
        if suit:
            return suit

        # Lead to tenace
        suit = self._lead_to_tenace()
        if suit:
            return suit

        # Play touching honours
        suit = self._play_touching_honours()
        if suit:
            return suit

        # Look for void in partner's hand
        suit = self._void_in_partners_hand()
        if suit:
            return suit

        # Select best suit
        score_reasons = self._get_score_reasons()
        best_suit = self._best_suit(score_reasons)
        return log(inspect.stack(), best_suit)

    def _get_score_reasons(self) -> dict[str, int]:
        score_reasons = {
            'trumps': self._deprecate_trumps(),
            'shortage': self._shortage_score(self.player.controls),
            'void': self._deprecate_suits(),
            'all_winners': self._all_winners_score(),
            'frozen': self._frozen_suits(),
            'long': self._long_suits(),
        }
        return score_reasons

    def _define_suit_to_develop(self) -> Suit:
        player = self.player
        manager = global_vars.manager
        suit_to_develop = manager.suit_to_develop(player.seat)
        if suit_to_develop and player.unplayed_cards[suit_to_develop]:
            return log(inspect.stack(), suit_to_develop)
        return None

    def _define_suit_with_winners(self) -> Suit:
        # Holds all winners
        player = self.player
        manager = global_vars.manager
        for suit_name, suit in SUITS.items():
            if suit != player.trump_suit:
                if player.holds_all_winners_in_suit(suit):
                    manager.set_suit_to_develop(player.seat, suit)
        return None

    def _select_suit_with_master(self) -> Suit:
        player = self.player
        if not player.opponents_trumps:
            total_cards = 0
            for suit in SUITS:
                holding = player.unplayed_cards[suit]
                total_cards += len(holding)
            if len(player.unplayed_cards[player.trump_suit]) > total_cards - 2:
                return log(inspect.stack(), player.trump_suit)

            for suit in SUITS:
                if (suit != player.trump_suit.name
                        and player.unplayed_cards[suit]):
                    if player.is_winner_declarer(
                            player.unplayed_cards[suit][0]):
                        return log(inspect.stack(), Suit(suit))
        return None

    def _lead_towards_tenace(self) -> Suit:
        player = self.player
        long_suits = player.partnership_long_suits()
        for suit in long_suits:
            if (not self._frozen_suit(suit)
                    and player.can_lead_toward_tenace(suit)):
                return log(inspect.stack(), Suit(suit))
        return None

    def _get_total_winners(self) -> int:
        winners = self._all_winners_score()
        total_winners = 0
        for suit_count in winners:
            total_winners += suit_count[1]
        return total_winners

    def _get_suit_to_develop(self) -> Suit:
        player = self.player
        manager = global_vars.manager
        total_winners = self._get_total_winners()
        if total_winners <= 13 - player.trick_number:
            suit = manager.suit_to_develop(player.seat)
            if suit:
                suit_name = suit.name
                if suit_name and player.suit_cards[suit_name]:
                    return log(inspect.stack(),
                               manager.suit_to_develop(player.seat))
                if not player.suit_cards[suit_name]:
                    manager.set_suit_to_develop(player.seat, None)
        return None

    def _lead_to_tenace(self) -> Suit:
        player = self.player
        if not player.opponents_trumps:
            long_suits = player.partnership_long_suits()
            for suit in long_suits:
                if (not self._frozen_suit(suit)
                        and player.can_lead_toward_tenace(suit)):
                    return log(inspect.stack(), Suit(suit))
        return None

    def _void_in_partners_hand(self) -> Suit:
        player = self.player
        if player.partners_unplayed_cards[player.trump_suit.name]:
            for suit in SUITS:
                if (player.unplayed_cards[suit]
                        and not player.partners_unplayed_cards[suit]):
                    return log(inspect.stack(), Suit(suit))
        return None

    def _play_touching_honours(self) -> Suit:
        player = self.player
        for suit in SUITS:
            can_lead_to_dummy = (
                player.touching_honours_in_hand(player.dummys_hand, suit)
                and player.unplayed_cards[suit])
            if (player.touching_honours_in_hand(player.hand, suit)
                    or can_lead_to_dummy):
                return log(inspect.stack(), Suit(suit))
        return None

    def _update_manager_with_threats(self):
        player = self.player
        manager = global_vars.manager
        for suit, threat_cards in player.threats.items():
            ace = Card('A', suit)
            king = Card('K', suit)
            queen = Card('Q', suit)
            if len(threat_cards) == 1:
                threat = threat_cards[0]
                if threat == ace and king in player.unplayed_cards[suit]:
                    manager.set_suit_to_develop(player.seat, Suit(suit))
                    manager.set_suit_strategy(player.seat, suit, 'missing_ace')
                elif threat == king and ace in player.unplayed_cards[suit]:
                    manager.set_suit_to_develop(player.seat, Suit(suit))
                    manager.set_suit_strategy(player.seat, suit,
                                              'missing_king')
                elif threat == queen and king in player.unplayed_cards[suit]:
                    manager.set_suit_to_develop(player.seat, Suit(suit))
                    manager.set_suit_strategy(player.seat, suit,
                                              'missing_queen')

    def _select_lead_card(self, suit: Suit) -> Card:
        """Return the selected lead card for declarer."""
        player = self.player
        my_cards = player.unplayed_cards[suit.name]
        partners_cards = player.partners_unplayed_cards[suit.name]
        partner_long = len(partners_cards) > len(my_cards)

        # Lead low to partner's winner
        if (not partner_long and partners_cards
                and player.is_winner_declarer(partners_cards[0])):
            return log(inspect.stack(), my_cards[-1])

        # if my_cards and not partner_long:
        #     for card in my_cards[len(partners_cards)-1::-1]:
        #         if player.is_winner_declarer(card):
        #             return log(inspect.stack(), card)

        if (player.is_winner_declarer(my_cards[0])
                and not player.partners_unplayed_cards[suit.name]):
            return log(inspect.stack(), my_cards[0])

        # Top of touching honours
        for index, card in enumerate(my_cards[:-1]):
            if card.is_honour and card.value == my_cards[index+1].value + 1:
                return log(inspect.stack(), card)

        # Top of doubleton
        if len(my_cards) == 2:
            return log(inspect.stack(), my_cards[0])

        # Card combinations
        card = card_combinations(player, suit.name)
        if card:
            return log(inspect.stack(), card)

        # Winners
        for card in my_cards[::-1]:
            if player.is_winner_declarer(card):
                return log(inspect.stack(), card)

        # Return bottom card
        return log(inspect.stack(), my_cards[-1])

    def _get_winning_suit(self) -> Suit:
        """Return the selected winning suit."""
        player = self.player
        winning_suits = self._get_winning_suit_list()

        long_suits = get_list_of_best_scores(winning_suits)
        if long_suits and player.unplayed_cards[long_suits[0]]:
            return log(inspect.stack(), Suit(long_suits[0]))
        return None

    def _get_winning_suit_list(self) -> list[Suit]:
        """Return a list of winning suits."""
        player = self.player
        winning_suits = {}
        for suit_name, suit in SUITS.items():
            our_cards = player.our_unplayed_cards[suit.name]
            if suit != player.trump_suit and our_cards:
                my_cards = player.unplayed_cards[suit_name]
                partners_cards = player.partners_unplayed_cards[suit_name]

                last_card = max(len(my_cards), len(partners_cards)) - 1
                opponents_cards = player.opponents_unplayed_cards[suit.name]
                for index, card in enumerate(our_cards[:last_card]):
                    if index < len(opponents_cards):
                        if card.value < opponents_cards[index].value:
                            break
                else:
                    winning_suits[suit_name] = last_card
        return winning_suits

    def _can_draw_trumps(self) -> tuple[bool, bool]:
        """Return True if declarer should draw trumps,
        and/or True to ruff in shorthand."""
        show_return = 0
        player = self.player
        if not player.opponents_unplayed_cards[player.trump_suit.name]:
            return return_and_print(False, 'can_draw_trumps z', show_return)
        if not player.trump_cards:
            return return_and_print(False, 'can_draw_trumps a', show_return)

        if self._ruff_in_short_hand():
            return return_and_print(False, 'can_draw_trumps b', show_return)
        our_trumps = player.our_unplayed_cards[player.trump_suit]
        if len(our_trumps) >= 9:
            # TODO too simplistic - determine losers first
            return return_and_print(True, 'can_draw_trumps d', show_return)
        return return_and_print(True, 'can_draw_trumps g', show_return)

    def _play_all_winners(self) -> Card:
        """Return a card to play when all are winners"""
        player = self.player

        # Draw trumps
        if player.trump_suit:
            suit_name = player.trump_suit.name
            if (player.unplayed_cards[suit_name]
                    and player.opponents_unplayed_cards[suit_name]):
                return self._select_card_from_right_hand(suit_name)
        for suit_name, suit in SUITS.items():
            if player.trump_suit and suit == player.trump_suit:
                continue
            if player.unplayed_cards[suit_name]:
                if player.holds_all_winners_in_suit(suit):
                    return self._select_card_from_right_hand(suit_name)
        return None

    def _select_card_from_right_hand(self, suit_name: str) -> Card:
        """Return the appropriate card depending on suit length."""
        player = self.player
        my_cards = player.unplayed_cards[suit_name]
        partners_cards = player.partners_unplayed_cards[suit_name]
        if (partners_cards and
                len(my_cards) < len(partners_cards) and
                my_cards[-1].value < partners_cards[0].value):
            return log(inspect.stack(), player.unplayed_cards[suit_name][0])
        else:
            for card in my_cards[::-1]:
                if player.is_winner_declarer(card):
                    return log(inspect.stack(), card)
        return log(inspect.stack(), player.unplayed_cards[suit_name][-1])

    def _ruff_in_short_hand(self):
        """Update manager if can ruff in short hand and return True."""
        player = self.player
        manager = global_vars.manager

        (long_trump_hand,
         short_trump_hand) = player.get_long_short_trump_hands()
        entries = player.get_entries(long_trump_hand)
        total_entries = 0
        for suit in SUITS:
            if suit != player.trump_suit.name:
                total_entries += len(entries[suit])
        if not total_entries:
            return False

        if not player.partners_unplayed_cards[player.trump_suit.name]:
            return False

        for suit in SUITS:
            (long_hand, short_hand) = player.get_long_short_hands(Suit(suit))
            long_cards = long_hand.cards_by_suit[suit]
            short_cards = short_hand.cards_by_suit[suit]
            if (short_cards and
                    len(short_cards) <= 2 and
                    suit != player.trump_suit.name and
                    long_hand == long_trump_hand):
                if ((Card('A', suit) in long_cards and
                        not short_cards[0].is_honour) or
                        Card('A', suit) in short_cards):
                    manager.set_suit_strategy(
                        player.seat, suit, 'ruff_in_short_hand')
                    manager.set_suit_to_develop(player.seat, Suit(suit))
                    if not player.threats[suit]:
                        return False
                    return True
        return False

    def _long_suits(self) -> list[tuple[str, int]]:
        """Assign score to suits based on length (long)."""
        player = self.player
        suit_scores = {suit_name: 0 for suit_name in SUITS}
        length_score = self.LENGTH_SCORE

        for suit in SUITS:
            number_cards = (len(player.our_cards[suit])
                            - len(player.opponents_cards[suit]))
            if number_cards > 0:
                if player.trump_suit:
                    if suit == player.trump_suit.name:
                        length_score = 0
                suit_scores[suit] = number_cards * length_score
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    def _all_winners_score(self) -> list[tuple[str, int]]:
        """Assign score to a suit if all the cards are winners."""
        player = self.player
        suit_scores = {suit_name: 0 for suit_name, suit in SUITS.items()}
        for suit_name, suit in SUITS.items():
            if suit != player.trump_suit:
                if player.holds_all_winners_in_suit(suit):
                    suit_scores[suit_name] = ALL_WINNERS
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    def _deprecate_trumps(self) -> list[tuple[str, int]]:
        """Assign score to a suit if opponents have no trumps."""
        suit_scores = {suit_name: 0 for suit_name, suit in SUITS.items()}
        suit_scores[self.player.trump_suit.name] = -1 * self.TRUMP_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    def _suit_strength(self) -> list[tuple[str, int]]:
        """Assign score to a suit by HCP."""
        suit_scores = {suit_name: 0 for suit_name, suit in SUITS.items()}
        for suit_name in SUITS:
            cards = self.player.our_cards[suit_name]
            for card in cards:
                if card.value >= 10:
                    suit_scores[suit_name] += card.value - 9
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    def _shortage_score(self,
                        controls: dict[str, int]) -> list[tuple[str, int]]:
        """Assign score to a suit if we can create a shortage."""
        player = self.player
        manager = global_vars.manager
        my_trumps = player.unplayed_cards[player.trump_suit]
        partners_trumps = player.unplayed_cards[player.trump_suit]

        suit_scores = {suit_name: 0 for suit_name in SUITS}
        for suit in SUITS:
            if suit != player.trump_suit.name:
                my_cards = player.unplayed_cards[suit]
                partners_cards = player.partners_unplayed_cards[suit]
                if len(my_cards) != len(partners_cards):
                    if ((len(my_cards) > len(partners_cards) and
                            len(partners_trumps) < len(my_trumps)) or
                            (len(my_cards) < len(partners_cards) and
                             len(my_trumps) < len(partners_trumps))):

                        if (controls[suit]
                                - len(player.partners_suit_cards[suit]) <= 1):
                            suit_scores[suit] += self.SHORTAGE_SCORE
                            manager.set_suit_to_develop(
                                player.declarer, Suit(suit))
        return [(suit_name, score) for suit_name, score in suit_scores.items()]
