""" First seat card play for defender."""

import inspect
from .logger import log

from bridgeobjects import SUITS, Card, Suit, CARD_VALUES
from .player import Player
from .first_seat import FirstSeat
from .defender_play import dummy_is_short_trump_hand
import bfgcardplay.global_variables as global_vars

MODULE_COLOUR = 'blue'


class FirstSeatDefender(FirstSeat):
    def __init__(self, player: Player):
        super().__init__(player)

    def selected_card(self) -> Card:
        """Return the lead card for first seat defender."""
        player = self.player
        self.update_manager()
        if len(player.hand.unplayed_cards) == 1:
            return log(inspect.stack(), player.hand.unplayed_cards[0])

        if player.board.contract.is_nt:
            suit = self._select_suit_for_nt_contract()
        else:
            suit = self._select_suit_for_suit_contract()
        if not player.unplayed_cards[suit]:
            raise ValueError(f'No cards for {suit}')
        card = self._select_card_from_suit(suit)
        return card

    def _select_suit_for_suit_contract(self) -> Suit:
        """Return the trick lead suit for the defending a suit contract."""
        player = self.player
        manager = global_vars.manager

        suit = self._play_partners_suit()
        if suit:
            return suit

        suit = self._partner_void_in_trumps()
        if suit:
            return suit

        # Play winner if a singleton in dummy
        suit = self._singleton_winner_in_dummy()
        if suit:
            return suit

        # Select suit if partner likes it
        for suit in SUITS:
            if (manager.like_dislike(player.partner_seat, suit) and
                    player.unplayed_cards[suit] and
                    player.dummys_suit_cards[suit]):
                return log(inspect.stack(), Suit(suit))

        # Select a suit if not deprecated
        deprecated_suits = self._get_deprecated_suits()
        suit = self._select_non_deprecated_suit(deprecated_suits)
        if suit:
            return suit

        # Play through a tenace
        tenace_suits = self._get_tenace_suits(deprecated_suits)
        if tenace_suits:
            return log(inspect.stack(), tenace_suits[0])

        # Play a 'liked' suit
        suit = self._select_liked_suit()
        if suit:
            return suit

        # Lead through strength
        suit = self._play_through_strength()
        if suit:
            return suit

        # Dummy out of trumps
        suit = self._dummy_out_of_trumps()
        if suit:
            return suit

        score_reasons = self._score_reasons()
        # Select best suit
        best_suit = self._best_suit(score_reasons)
        return log(inspect.stack(), best_suit)

    def _play_partners_suit(self) -> Suit:
        player = self.player
        partners_suit = player.board.tricks[0].cards[0].suit.name
        if player.dummys_unplayed_cards[partners_suit]:
            if player.unplayed_cards[partners_suit]:
                return log(inspect.stack(), Suit(partners_suit))
        return None

    def _singleton_winner_in_dummy(self) -> Suit:
        player = self.player
        if player.trump_suit:
            for suit in SUITS:
                if suit != player.trump_suit and player.unplayed_cards[suit]:
                    if (len(player.dummys_unplayed_cards[suit]) == 1 and
                            player.is_winner_defender(
                                player.unplayed_cards[suit][0])):
                        return log(inspect.stack(), Suit(suit))
        return None

    def _get_deprecated_suits(self) -> list[Suit]:
        deprecated_suits = []
        dummy_tenaces = self.identify_dummy_tenaces()
        for suit in SUITS:
            if self.player.dummy_on_right and suit in dummy_tenaces:
                deprecated_suits.append(suit)
        return deprecated_suits

    def _get_tenace_suits(self, deprecated_suits) -> list[Suit]:
        tenace_suits = []
        dummy_tenaces = self.identify_dummy_tenaces()
        for suit in SUITS:
            if suit not in deprecated_suits:
                if self.player.dummy_on_left and suit in dummy_tenaces:
                    tenace_suits.append(Suit(suit))
        return tenace_suits

    def _select_non_deprecated_suit(self, deprecated_suits) -> Suit:
        player = self.player
        for suit in SUITS:
            if suit not in deprecated_suits:
                dummy_short_trumps = dummy_is_short_trump_hand(player)
                if ((dummy_short_trumps and player.dummys_suit_cards[suit]) or
                        not dummy_short_trumps):
                    cards = player.unplayed_cards[suit]
                    if cards:
                        top_card = cards[0]

                        # Play next of touching
                        if top_card.value < CARD_VALUES['A']:
                            higher_rank = CARD_VALUES[top_card.value+1]
                            higher_card = Card(higher_rank, suit)
                            if (top_card.is_honour
                                    and higher_card in player.hand.cards):
                                return log(inspect.stack(), Suit(suit))
                        # Play top of touching
                        if len(cards) > 1:
                            if (top_card.is_honour
                                    and top_card.value == cards[1].value + 1):
                                return log(inspect.stack(), Suit(suit))
        return None

    def _select_liked_suit(self) -> Suit:
        player = self.player
        manager = global_vars.manager
        for suit in SUITS:
            if (player.dummys_unplayed_cards[suit] or
                    not player.dummys_unplayed_cards[player.trump_suit]):
                if (manager.like_dislike(player.partner_seat, suit)
                        and player.unplayed_cards[suit]):
                    return log(inspect.stack(), Suit(suit))
                if (manager.like_dislike(player.seat, suit)
                        and player.unplayed_cards[suit]):
                    return log(inspect.stack(), Suit(suit))
        return None

    def _dummy_out_of_trumps(self) -> Suit:
        player = self.player
        if player.trump_suit:
            for suit in SUITS:
                unplayed_cards = player.unplayed_cards[suit]
                if (len(player.total_unplayed_cards[suit]) == 1 and
                        player.total_unplayed_cards[suit][0] in unplayed_cards
                        and not player.dummys_suit_cards[
                            player.trump_suit.name]):
                    return log(inspect.stack(), Suit(suit))
        return None

    def _score_reasons(self) -> dict[str, int]:
        score_reasons = {}

        # Deprecate voids
        score_reasons['void'] = self._deprecate_suits()

        # Trumps
        score_reasons['trumps'] = self._trumps()

        # Return partner's suit
        score_reasons['partner'] = self._partners_suit()

        # Lead from sequence
        score_reasons['sequences'] = self._sequences()

        # Lead to partner's void
        score_reasons['sequences'] = self._partners_voids()

        # Lead through tenaces not to tenaces
        score_reasons['tenaces'] = self._tenace_check()

        # Lead through or to strength
        score_reasons['weakness'] = self._lead_through_strength()

        # Avoid frozen suits
        score_reasons['frozen'] = self._frozen_suits()

        # Long suits
        score_reasons['long'] = self._long_suits()

        # Short suits
        score_reasons['short'] = self._short_suits()

        # Ruff and discard
        if self.player.trump_suit:
            score_reasons['ruff'] = self._ruff_and_discard()
        return score_reasons

    def _play_through_strength(self) -> Suit:
        player = self.player
        for suit in SUITS:
            if player.unplayed_cards[suit]:
                if player.dummy_on_left:
                    if player.dummys_unplayed_cards[suit]:
                        dummys_top_card = player.dummys_unplayed_cards[suit][0]
                        value = player.total_unplayed_cards[suit][0].value
                        if (dummys_top_card.is_honour and
                                dummys_top_card.value < value):
                            return log(inspect.stack(), Suit(suit))
        return None

    def _partner_void_in_trumps(self) -> Suit:
        player = self.player
        manager = global_vars.manager
        # if deduce_partner_void_in_trumps(player):
        #     manager.voids[player.partner_seat][player.trump_suit.name] = True

        partners_seat = player.partner_seat
        partners_voids = player.voids[partners_seat]
        if not partners_voids[player.trump_suit.name]:
            for suit in SUITS:
                if (player.voids[partners_seat][suit] and
                        player.unplayed_cards[suit]):
                    manager.set_suit_to_develop(player.seat, Suit(suit))
                    manager.set_suit_strategy(
                        player.seat,
                        suit,
                        'ruff_in_void'
                    )
                    return log(inspect.stack(), Suit(suit))
        return None

    def _select_suit_for_nt_contract(self) -> Suit:
        """Return the trick lead suit for the defending a suit contract."""
        player = self.player

        # Return partner's suit
        if len(player.unplayed_cards[player.board.tricks[0].suit]) > 0:
            return log(inspect.stack(), player.board.tricks[0].suit)

        # Select suit after partner signal
        suit = self._suit_after_partner_signal()
        if suit:
            return suit

        suit = self._suit_to_develop()
        if suit:
            return suit

        suit = self._working_suit()
        if suit:
            return suit

        suit = self._set_suit_to_develop()
        if suit:
            return suit

        suit = self._is_winner_defender()
        if suit:
            return suit

        suit = self._liked_suit()
        if suit:
            return suit

        score_reasons = self._score_reasons()
        best_suit = self._best_suit(score_reasons)
        return log(inspect.stack(), best_suit)

    def _suit_after_partner_signal(self) -> Suit:
        player = self.player
        if len(player.board.tricks) == 2 and player.dummy_on_right:
            partners_lead = player.board.tricks[0].cards[0]
            if (partners_lead.value >= CARD_VALUES['T'] or
                    partners_lead.value < CARD_VALUES['6']):
                if player.unplayed_cards[partners_lead.suit.name]:
                    return log(inspect.stack(), partners_lead.suit)
        return None

    def _suit_to_develop(self) -> Suit:
        player = self.player
        manager = global_vars.manager
        suit_to_develop = manager.suit_to_develop(player.seat)
        if suit_to_develop and player.unplayed_cards[suit_to_develop.name]:
            return log(inspect.stack(), suit_to_develop)
        return None

    def _working_suit(self) -> Suit:
        player = self.player
        manager = global_vars.manager
        working_suit = manager.working_suit[player.seat]
        if working_suit and working_suit.name:
            if player.suit_cards[working_suit.name]:
                return log(inspect.stack(), working_suit)
        return None

    def _set_suit_to_develop(self) -> Suit:
        player = self.player
        manager = global_vars.manager
        my_hand = player.hand
        longest_suit = my_hand.longest_suit
        if (my_hand.cards_by_suit[longest_suit.name][0].is_honour and
                player.get_entries_in_other_suits(my_hand, longest_suit) and
                player.unplayed_cards[longest_suit.name]):
            manager.set_suit_to_develop(player.seat, longest_suit)
            return log(inspect.stack(), longest_suit)
        return None

    def _is_winner_defender(self) -> Suit:
        player = self.player
        if len(player.board.tricks) > 6:
            for suit in SUITS:
                cards = player.unplayed_cards[suit]
                if cards:
                    if player.is_winner_defender(
                            player.unplayed_cards[suit][0]
                            ):
                        return log(inspect.stack(), Suit(suit))
        return None

    def _liked_suit(self) -> Suit:
        player = self.player
        manager = global_vars.manager
        for suit in SUITS:
            if (manager.like_dislike(player.partner_seat, suit) and
                    player.unplayed_cards[suit]):
                return log(inspect.stack(), Suit(suit))
        return None

    def _select_card_from_suit(self, suit: Suit) -> Card:
        """Return the card to lead from the given suit."""
        player = self.player
        manager = global_vars.manager
        cards = player.suit_cards[suit.name]

        suit_to_develop = manager.suit_to_develop(player.seat)
        if suit_to_develop:
            suit_cards = player.unplayed_cards[suit_to_develop]
            if (suit_cards and
                    len(player.total_unplayed_cards[suit_to_develop]) > 1):
                if manager.suit_strategy(
                        player.seat)[suit_to_develop.name] == 'ruff_in_void':
                    if suit_cards[0].value > player.total_unplayed_cards[
                            suit_to_develop][1].value:
                        return log(inspect.stack(), suit_cards[0])
                    else:
                        return log(inspect.stack(), suit_cards[-1])

        # Winning card
        if player.trump_suit:
            if player.is_winner_defender(player.unplayed_cards[suit][0]):
                return log(inspect.stack(), cards[0])

        if self._all_winners(suit):
            return log(inspect.stack(), player.unplayed_cards[suit][0])

        # Top of touching honours
        for index, card in enumerate(cards[:-1]):
            if card.is_honour and card.value == cards[index+1].value + 1:
                return log(inspect.stack(), card)

        # Top of doubleton
        if len(cards) == 2:
            return log(inspect.stack(), cards[0])

        # Return winners
        # TODO sort out invalid for defender
        winners = player.winners[suit.name]
        if winners and winners[-1] in cards:
            return log(inspect.stack(), winners[-1])

        # Return bottom card
        return log(inspect.stack(), cards[-1])

    def _sequences(self) -> Suit:
        """Return the score for sequences."""
        suit_scores = {suit_name: 0 for suit_name in SUITS}
        player = self.player
        touching_honours = player.hand.touching_honours()
        best_sequence = None
        max_score = 0
        for suit_name in suit_scores:
            if touching_honours[suit_name]:
                suit_scores[suit_name] += self.TOUCHING_HONOURS
                suit_scores[suit_name] += len(touching_honours[suit_name])
                if suit_scores[suit_name] > max_score:
                    max_score = suit_scores[suit_name]
                    best_sequence = suit_name

        manager = global_vars.manager
        manager.working_suit[player.seat] = Suit(best_sequence)
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    def _partners_voids(self) -> Suit:
        """Return the score for sequences."""
        suit_scores = {suit_name: 0 for suit_name in SUITS}
        player = self.player
        partners_voids = player.voids[player.seat]
        for suit, void in partners_voids.items():
            if void:
                suit_scores[suit] += self.PARTNERS_VOID
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    def _deprecate_suits(self) -> list[tuple[str, int]]:
        """Assign score to suits based on void."""
        player = self.player
        suit_scores = {suit_name: 0 for suit_name in SUITS}
        for suit in SUITS:
            if not self.player.suit_cards[suit]:
                suit_scores[suit] -= self.VOID_SCORE
            if player.trump_suit:
                dummy_short_trumps = dummy_is_short_trump_hand(player)
                if (dummy_short_trumps and not player.dummys_suit_cards[suit]):
                    suit_scores[suit] -= self.RUFF_AND_DISCARD_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    def _trumps(self) -> list[tuple[str, int]]:
        """Assign score to suits based on void."""
        suit_scores = {suit_name: 0 for suit_name in SUITS}
        player = self.player
        if player.trump_suit:
            my_cards = player.unplayed_cards[player.trump_suit.name]
            dummys_cards = player.dummys_suit_cards[player.trump_suit.name]
            if len(my_cards) > len(dummys_cards):
                suit_scores[player.trump_suit.name] += self.TRUMP_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    def _all_winners(self, suit: Suit) -> bool:
        """Return True if all of the cards held are winners."""
        player = self.player
        all_winners = True
        unplayed_cards = len(player.total_unplayed_cards[suit])
        missing_cards = unplayed_cards - len(player.suit_cards[suit])
        if len(player.unplayed_cards[suit]) < missing_cards:
            return False
        for index in range(missing_cards):
            if not player.is_winner_defender(
                    player.unplayed_cards[suit][index]
                    ):
                all_winners = False
        return all_winners
