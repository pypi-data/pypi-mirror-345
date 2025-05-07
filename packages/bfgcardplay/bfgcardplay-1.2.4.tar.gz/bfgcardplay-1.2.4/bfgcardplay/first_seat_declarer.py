# first_seat_declarer.py

""" First seat card play for declarer."""

import inspect
from .logger import log

from bridgeobjects import SUITS, Card, Suit

import bfgcardplay.global_variables as global_vars
from .player import Player, Cards
from .first_seat import FirstSeat

MODULE_COLOUR = 'cyan'


ALL_WINNERS = 5


class FirstSeatDeclarer(FirstSeat):
    def __init__(self, player: Player):
        super().__init__(player)

    def selected_card(self) -> Card:
        """Return the selected card for the first seat."""
        player = self.player
        manager = global_vars.manager
        if player.trump_suit:
            suit = self._select_suit_for_suit_contract(manager)
        else:
            suit = self._select_suit_for_nt_contract(manager)
        if manager.card_to_play[player.seat]:
            card = manager.card_to_play[player.seat][0]
            manager.card_to_play[player.seat].pop(0)
            if (manager.suit_to_develop[player.seat]
                    and manager.card_to_play[player.seat]):
                manager.card_to_play[player.seat] = player.suit_cards[
                    manager.suit_to_develop][-1]
            log(inspect.stack(), f'{card}')
            return card
        if not player.suit_cards[suit.name]:
            raise ValueError(f'No cards for {suit}')
        if manager.winning_suit:
            if player.suit_cards[manager.winning_suit.name]:
                return self._select_card_from_manager_winning_suit(manager)
        card = self._select_lead_card(manager, suit)
        log(inspect.stack(), f'{card}')
        return card

    def _select_suit_for_suit_contract(self, manager) -> Suit:
        """Return the trick lead suit for the declarer in  a suit contract."""
        player = self.player
        manager = global_vars.manager
        score_reasons = {}

        # Draw trumps?
        if player.opponents_trumps and self._can_draw_trumps():
            return player.trump_suit
        else:
            score_reasons['trumps'] = self._deprecate_trumps()
            winners = self._all_winners_score()
            total_winners = 0
            for suit_count in winners:
                total_winners += suit_count[1]
            if total_winners <= 13 - player.trick_number:
                score_reasons['shortage'] = self._shortage_score(
                    player.controls)
                suit_name = manager.suit_to_develop[player.seat].name
                if suit_name and player.suit_cards[suit_name]:
                    return manager.suit_to_develop[player.seat]
                if not player.suit_cards[suit_name]:
                    manager.suit_to_develop[player.seat] = None

        winning_suit = self._play_winning_suit(manager)
        if winning_suit:
            return winning_suit

        if player.trump_suit and not player.opponents_trumps:
            long_suits = player.partnership_long_suits()
            for suit in long_suits:
                if player.can_lead_toward_tenace(suit):
                    return Suit(suit)

        return player.longest_suit

    def _select_suit_for_nt_contract(self, manager) -> Suit:
        """Return the trick lead suit for the declarer in  a suit contract."""
        player = self.player

        winners = player.get_winners()
        target = player.declarers_target
        our_tricks = player.declarers_tricks

        if target - (winners + our_tricks) > 0:
            if len(player.board.tricks) == 2:
                suit_to_develop = self._suits_to_develop(
                    manager, player.controls)
                if suit_to_develop:
                    return suit_to_develop

        winning_suit = self._play_winning_suit(manager)
        if winning_suit:
            return winning_suit

        score_reasons = {}

        # Deprecate voids
        score_reasons['void'] = self._deprecate_suits()

        # All cards are winners
        score_reasons['all_winners'] = self._all_winners_score()

        # Avoid frozen suits
        score_reasons['frozen'] = self._frozen_suits()

        # Long suits
        score_reasons['long'] = self._long_suits()

        # Controls
        score_reasons['controls'] = self._long_suits()

        # Suit strength
        score_reasons['strength'] = self._suit_strength()

        # Select best suit
        best_suit = self._best_suit(score_reasons)
        # print(colored(f'{best_suit=} {score_reasons=}', 'red'))
        return best_suit

    def _suits_to_develop(self, manager: object,
                          controls: list[str]) -> list[str]:
        """Return a list of suits to develop."""
        player = self.player
        suits_to_develop = []
        suit_to_develop = None
        for suit_name in SUITS:
            if not controls[suit_name]:
                suits_to_develop.append(suit_name)
        long_suits_to_develop = []

        lead_to_this_hand = False
        for suit_name in suits_to_develop:
            declarers_suit_cards = player.declarers_suit_cards[suit_name]
            dummys_suit_cards = player.dummys_suit_cards[suit_name]
            total_cards = len(declarers_suit_cards) + len(dummys_suit_cards)
            if (total_cards >= 6 and
                    (len(declarers_suit_cards) >= 4
                     or len(dummys_suit_cards) >= 4)):
                long_suits_to_develop.append(suit_name)
                my_touching_honours = player.hand.touching_honours()
                partners_honours = player.partners_hand.touching_honours()
                partner_touching_honours = partners_honours
                for suit_name in suits_to_develop:

                    suit_cards = player.partners_suit_cards[suit_name]
                    if player.get_suit_tenaces(suit_cards):
                        suit_to_develop = suit_name

                    suit_cards = player.suit_cards[suit_name]
                    if player.get_suit_tenaces(suit_cards):
                        suit_to_develop = suit_name
                        lead_to_this_hand = True
                    if partner_touching_honours[suit_name]:
                        suit_to_develop = suit_name
                    if my_touching_honours[suit_name]:
                        suit_to_develop = suit_name
                        lead_to_this_hand = True

        entry = None
        if lead_to_this_hand:
            partners_entries = player.get_entries(player.partners_hand)
            for suit_name in SUITS:
                if (partners_entries[suit_name]
                        and player.suit_cards[suit_name]):
                    entry = partners_entries[suit_name][0]
                    break
        if entry:
            if suit_to_develop:
                manager.suit_to_develop[player.declarer] = suit_to_develop
                manager.suit_to_develop[player.dummy] = suit_to_develop
                manager.card_to_play[player.partner_seat].append(entry)
                card = player.partners_suit_cards[suit_to_develop][-1]
                manager.card_to_play[player.partner_seat].append(card)
                manager.card_to_play[player.seat].append(
                    player.suit_cards[entry.suit.name][-1])
                return Suit(suit_to_develop)
        return None

    def _select_lead_card(self, manager, suit: Suit) -> Card:
        """Return the selected lead card for declarer."""
        player = self.player
        cards = player.suit_cards[suit.name]
        # Top of touching honours
        for index, card in enumerate(cards[:-1]):
            if card.is_honour and card.value == cards[index+1].value + 1:
                log(inspect.stack(), f'{card}')
                return card

        # Top of doubleton
        if len(cards) == 2:
            log(inspect.stack(), f'{cards[0]}')
            return cards[0]

        # Return bottom card
        log(inspect.stack(), f'{cards[-1]}')
        return cards[-1]

    def _select_card_from_manager_winning_suit(self, manager: object) -> Card:
        """Return the selected lead card from manager winning suit."""
        player = self.player
        suit = manager.winning_suit
        long_player = player.long_seat(suit.name)
        manager.long_player = long_player
        cards = player.suit_cards[suit.name]
        if long_player != player.seat:
            # Short hand leads top card
            log(inspect.stack(), f'{cards[0]}')
            return cards[0]
        # Long hand leads bottom card if short hand has cards
        if player.partners_suit_cards[suit.name]:
            log(inspect.stack(), f'{cards[-1]}')
            return cards[-1]
        else:
            log(inspect.stack(), f'{cards[0]}')
            return cards[0]

    def _play_winning_suit(self, manager) -> Suit:
        """Return the winning suit or None."""
        player = self.player
        # Reset Manager winning suit when no cards left
        if manager.winning_suit:
            if player.suit_cards[manager.winning_suit.name]:
                return manager.winning_suit
            else:
                manager.winning_suit = None

        winning_suit = self._get_winning_suit(player)
        if winning_suit:
            manager.winning_suit = winning_suit
            return winning_suit
        return None

    def _get_winning_suit(self, player: Player) -> Suit:
        """Return the selected winning suit."""
        winning_suits = self._get_winning_suits(player)
        max_length = 0
        long_suit = None
        for suit in winning_suits:
            suit_length = len(player.suit_cards[suit.name])
            if suit_length > max_length:
                max_length = suit_length
                long_suit = suit
        return long_suit

    def _get_winning_suits(self, player: Player) -> list[Suit]:
        """Return a list of winning suits."""
        winning_suits = []
        for suit in SUITS.values():
            if suit != player.trump_suit:
                if player.holds_all_winners_in_suit(suit):
                    winning_suits.append(suit)
        return winning_suits

    def _can_draw_trumps(self) -> bool:
        """Return True if declarer should draw trumps."""
        player = self.player
        if not player.trump_cards:
            return False

        declarers_trumps = Cards(player.declarers_hand.cards).by_suit[
            player.trump_suit]
        dummys_trumps = Cards(player.dummys_hand.cards).by_suit[
            player.trump_suit]
        if (len(declarers_trumps) + len(dummys_trumps) <= 7 and
                max(len(declarers_trumps), len(dummys_trumps)) == 4):
            return False

        declarers_trumps = player.unplayed_cards_by_suit(
            player.trump_suit, player.declarer)
        dummys_trumps = player.unplayed_cards_by_suit(
            player.trump_suit, player.dummy)
        if len(declarers_trumps) + len(dummys_trumps) >= 9:
            # TODO too simplistic - determine losers first
            return True

        declarer_longer_trumps = len(declarers_trumps) > len(dummys_trumps)
        if declarer_longer_trumps:
            short_hand = player.board.hands[player.dummy]
        else:
            short_hand = player.board.hands[player.declarer]
        if short_hand.shape[3] <= 2:
            # Are there sufficient rumps in short hand?
            opponents_trumps = player.opponents_unplayed_cards[
                player.trump_suit.name]
            if len(short_hand.cards_by_suit[
                    player.trump_suit.name]) > len(opponents_trumps):
                return True
            # can declarer produce a void in time?
            suit = short_hand.shortest_suit

            declarers_cards = player.unplayed_cards_by_suit(
                suit, player.declarer)
            dummys_cards = player.unplayed_cards_by_suit(suit, player.dummy)
            suit_cards = declarers_cards + dummys_cards

            if (Card('A', suit.name) not in suit_cards
                    or Card('K', suit.name) in suit_cards):
                return False
        return True

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
        suit_scores = {suit_name: 0 for suit_name in SUITS}
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
        suit_scores = {suit_name: 0 for suit_name in SUITS.keys()}
        for suit_name, suit in SUITS.items():
            if suit != player.trump_suit:
                if controls[suit_name] - len(
                        player.partners_suit_cards[suit_name]) <= 1:
                    suit_scores[suit_name] += self.SHORTAGE_SCORE
                    manager.suit_to_develop[player.declarer] = Suit(suit_name)
                    manager.suit_to_develop[player.dummy] = Suit(suit_name)
        return [(suit_name, score) for suit_name, score in suit_scores.items()]
