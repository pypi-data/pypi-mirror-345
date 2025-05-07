"""Common functionality for cardplay."""

from bridgeobjects import Suit, Card, SEATS, SUITS, CARD_VALUES, RANKS
from bfgbidding import Hand
from bfgdealer import Trick

import bfgcardplay.global_variables as global_vars
from .data_classes import Cards, CardArray
from .data_classes import SuitCards
from .utilities import get_list_of_best_scores, get_suit_strength

global_vars.initialize()


class Player():
    """Object to represent the player: their hand and memory."""
    def __init__(self, board):
        self.board = board
        if not self.board.tricks:
            self.board.tricks.append(Trick())

        # Seats and roles
        self.seat = self._get_seat()
        self.seat_index = SEATS.index(self.seat)
        self.partner_seat = self._get_partners_seat(self.seat)
        self.declarer = board.contract.declarer
        self.declarer_index = SEATS.index(self.declarer)
        self.is_declarer = self.seat == self.declarer
        self.dummy_index = (self.declarer_index + 2) % 4
        self.dummy = SEATS[self.dummy_index]
        self.is_dummy = self.seat == self.dummy
        self.is_defender = not (self.is_declarer or self.is_dummy)
        (self.right_hand_seat,
         self.left_hand_seat) = self._get_opponents_seats()
        self.short_suit_seat = None

        # Hands suits and cards
        self.trump_suit = self._get_trump_suit()
        self.hands = board.hands
        self.hand = board.hands[self.seat]
        self.partners_hand = None
        self.declarers_hand = board.hands[self.declarer]
        self.dummys_hand = board.hands[self.dummy]

        # self.hand_cards is the Cards object for unplayed cards
        self.hand_cards = Cards(board.hands[self.seat].unplayed_cards)
        self.suit_cards = self.hand_cards.by_suit
        self.unplayed_cards = self.hand_cards.by_suit

        # self.longest_suit = self.hand_cards.longest_suit
        self.longest_suit = self._longest_suit()

        our_cards = Cards(
            board.hands[self.seat].cards + board.hands[self.partner_seat].cards
            )
        my_unplayed_cards = board.hands[self.seat].unplayed_cards
        partners_unplayed_cards = board.hands[self.partner_seat].unplayed_cards
        our_unplayed_cards = Cards(my_unplayed_cards + partners_unplayed_cards)
        self.our_cards: dict[str, list[Card]] = our_cards.by_suit
        self.our_unplayed_cards: dict[str, list[Card]] = {}
        self.our_unplayed_cards = our_unplayed_cards.by_suit

        (self.opponents_cards,
         self.opponents_unplayed_cards) = self._get_opponents_cards()

        self.seats_unplayed_cards = {
            seat: Cards(self.board.hands[seat].unplayed_cards).by_suit
            for seat in SEATS}
        self.highest_card = {seat: {} for seat in SEATS}

        # Trumps
        (self.trump_cards, self.opponents_trumps) = self._get_trump_cards()

        # Partners
        self.partners_hand = self._get_partners_hand()
        (self.partners_suit_cards,
         self.partners_unplayed_cards) = self._get_partners_suit_cards()
        self.total_unplayed_cards = self._total_unplayed_cards()

        # Declarer and Dummy
        # These card properties must be assigned in this order
        declarers_cards = Cards(board.hands[self.declarer].unplayed_cards)
        self.declarers_suit_cards = declarers_cards.by_suit
        dummys_cards = Cards(board.hands[self.dummy].unplayed_cards)
        self.dummys_suit_cards: dict[str, list[Card]] = dummys_cards.by_suit
        self.dummys_unplayed_cards: dict[str, list[Card]] = {}
        self.dummys_unplayed_cards = dummys_cards.by_suit
        self.dummy_suit_strength = get_suit_strength(dummys_cards.list)
        self.dummy_suit_tenaces = self._get_tenaces(self.dummys_suit_cards)

        # Short trump hands
        self.short_suit_seat = self._get_short_suit_seat()
        self.short_hand = self._get_short_hand()

        # Defenders
        (self.dummy_on_left, self.dummy_on_right) = self._get_dummy_location()

        # Information
        self.trick_number = len(board.tricks)
        self.declarers_target = self.board.contract.target_tricks
        (self.declarers_tricks,
         self.defenders_tricks) = self._get_trick_count()
        self.suit_rounds = self._get_suit_rounds()
        self.voids = self._get_voids()
        self.controls = self._get_controls()
        self.second_round_controls = self._get_second_round_controls()

        self.winners = self._get_suit_winners()
        self.threats = self._get_threats()
        self.winner_count = self._get_winner_count()
        self.losers = self._get_suit_losers()
        self.sure_tricks = CardArray(self._get_current_sure_tricks())
        self.tricks_needed = 6 + int(self.board.contract.name[0])
        self.probable_tricks = CardArray(self._get_current_probable_tricks())
        self.possible_tricks = CardArray(self._get_current_possible_tricks())
        self.possible_promotions = CardArray(self._get_possible_promotions())

    @staticmethod
    def cards_by_suit(hand: Hand) -> dict[str, list[Card]]:
        """Return a dict of unplayed cards by suit for the given hand."""
        cards = Cards(hand.unplayed_cards)
        return cards.by_suit

    @staticmethod
    def _get_partners_seat(seat: str) -> str:
        """Return partner's seat."""
        seat_index = SEATS.index(seat)
        partners_index = (seat_index + 2) % 4
        partners_seat = SEATS[partners_index]
        return partners_seat

    def _get_seat(self) -> str:
        """Return the current user's seat."""
        trick = self.board.tricks[-1]
        leader = trick.leader
        if trick.winner:
            leader = trick.winner
        leader_index = SEATS.index(leader)
        seat_index = (leader_index + len(trick.cards)) % 4
        seat = SEATS[seat_index]
        return seat

    def cards_for_trick_suit(self, trick: Trick) -> list[Card]:
        """Return a list of cards in the trick suit."""
        return self.hand_cards.by_suit[trick.suit]

    def _get_trump_suit(self) -> Suit:
        """Return the trump suit for the board (if any)."""
        if self.board.contract.is_nt:
            return None
        return self.board.contract.denomination

    def get_strongest_suits(self, cards: list[Card]) -> list[Suit]:
        """Return a list of suits that have the highest high card points."""
        suit_points = get_suit_strength(cards)
        strong_suits = get_list_of_best_scores(suit_points)
        return strong_suits

    def _get_tenaces(self, cards: dict[str, Card]) -> dict[str, Card]:
        """Return a dict of suit tenaces keyed on suit name."""
        suit_tenaces = {suit_name: None for suit_name, suit in SUITS.items()}
        for suit, cards in cards.items():
            suit_tenaces[suit] = self.get_suit_tenaces(cards)
        return suit_tenaces

    def get_suit_tenaces(self, cards: list[Card]) -> Card:
        """Return the top card in a tenaces, or None."""
        if not cards:
            return None

        opponents_cards = self.opponents_unplayed_cards[cards[0].suit.name]
        suit = cards[0].suit_name
        for card in cards[:-2]:
            if card.is_honour:
                value = card.value
                missing_card = Card(CARD_VALUES[value-1], suit)
                next_card = Card(CARD_VALUES[value-2], suit)
                if missing_card in opponents_cards and next_card in cards:
                    return next_card
        return None

    def _get_opponents_seats(self) -> tuple[str, str]:
        """Return a tuple with right and left hand seats."""
        seat_index = SEATS.index(self.seat)
        left_hand_seat_index = (seat_index + 1) % 4
        right_hand_seat_index = (seat_index + 3) % 4
        return (SEATS[right_hand_seat_index], SEATS[left_hand_seat_index])

    def _get_short_suit_seat(self):
        """Return the short seat in a suit contract."""
        if not self.trump_suit:
            return None
        declarers_trumps = self.declarers_suit_cards[self.trump_suit]
        dummys_trumps = self.dummys_suit_cards[self.trump_suit]
        if len(declarers_trumps) > len(dummys_trumps):
            return self.dummy
        return self.declarer

    def _get_trump_cards(self):
        """Return a tuple containing our and opponent's trump cards"""
        if self.trump_suit:
            trump_cards = self.hand_cards.by_suit[self.trump_suit]
            opponents_trumps = self.opponents_unplayed_cards[self.trump_suit]
            return (trump_cards, opponents_trumps)
        return (None, None)

    def _get_partners_hand(self):
        """Return partner's hand."""
        if self.is_declarer:
            return self.board.hands[self.dummy]
        elif self.is_dummy:
            return self.board.hands[self.declarer]
        return None

    def _get_partners_suit_cards(self):
        """Return partner's suit cards"""
        if not self.partners_hand:
            return ({suit: [] for suit in SUITS}, {suit: [] for suit in SUITS})
        partners_cards = Cards(self.partners_hand.cards)
        partners_unplayed_cards = Cards(self.partners_hand.unplayed_cards)
        return (partners_cards.by_suit, partners_unplayed_cards.by_suit)

    def _get_dummy_location(self):
        """Return a tuple with dummy's location."""
        if not self.is_defender:
            return (False, False)
        dummy_on_left = ((self.seat_index - self.dummy_index) % 4) == 3
        dummy_on_right = not dummy_on_left
        return (dummy_on_left, dummy_on_right)

    def _get_opponents_cards(self):
        """Return opponent's cards."""
        opponents_seats = (SEATS[(self.seat_index + 1) % 4],
                           SEATS[(self.seat_index + 3) % 4])
        opps_cards_0 = self.board.hands[opponents_seats[0]].cards
        opps_cards_1 = self.board.hands[opponents_seats[1]].cards
        opponents_cards = Cards(opps_cards_0 + opps_cards_1)
        unplayed_cards_0 = self.board.hands[opponents_seats[0]].unplayed_cards
        unplayed_cards_1 = self.board.hands[opponents_seats[1]].unplayed_cards
        opponents_unplayed_cards = Cards(unplayed_cards_0 +
                                         unplayed_cards_1)
        return (opponents_cards.by_suit, opponents_unplayed_cards.by_suit)

    def _get_short_hand(self):
        """Return the short hand in a suit contract."""
        if not self.trump_suit:
            return None
        declarers_trumps = self.get_unplayed_cards_by_suit(self.trump_suit,
                                                           self.declarer)
        dummys_trumps = self.get_unplayed_cards_by_suit(self.trump_suit,
                                                        self.dummy)
        declarer_longer_trumps = len(declarers_trumps) > len(dummys_trumps)
        if declarer_longer_trumps:
            return self.board.hands[self.dummy]
        return self.board.hands[self.declarer]

    def card_has_been_played(self, card: Card) -> bool:
        """Return True if the card has already been played."""
        for seat in SEATS:
            hand = self.board.hands[seat]
            if card in hand.unplayed_cards:
                return False
        return True

    def get_unplayed_cards_by_suit(self, suit: Suit, seat: str) -> list[Card]:
        """Return a list containing declarers and
        opponents unplayed cards in a suit."""
        hand = self.board.hands[seat]
        cards = hand.cards_by_suit[suit.name]
        unplayed_cards = [card for card in cards
                          if card in hand.unplayed_cards]
        return unplayed_cards

    def _total_unplayed_cards(self) -> dict[str, list[Card]]:
        """Return a dict containing all unplayed cards by suit."""
        unplayed_card_list = []
        for seat in SEATS:
            unplayed_card_list += self.hands[seat].unplayed_cards
            unplayed_cards = Cards(unplayed_card_list)
        return unplayed_cards.by_suit

    @staticmethod
    def _sort_cards(cards: list[Card]) -> list[Card]:
        """Return a sorted list of cards."""
        return sorted(cards, reverse=True)

    def long_seat(self, suit: str) -> str:
        my_cards = self.unplayed_cards[suit]
        partners_cards = self.partners_unplayed_cards[suit]
        if len(my_cards) > len(partners_cards):
            return self.seat
        else:
            return self.partner_seat

    def holds_all_winners_in_suit(self, suit: Suit,
                                  trick: Trick = None) -> bool:
        """Return True if the partnership holds all the winners in a suit."""
        unplayed_cards = self.opponents_unplayed_cards[suit.name]
        opponents_unplayed_cards = [card for card in unplayed_cards]
        our_cards = [card for card in self.our_unplayed_cards[suit.name]]
        if trick:
            for card in trick.cards:
                if card.suit == suit:
                    if card in self.opponents_cards[suit.name]:
                        opponents_unplayed_cards.append(card)
                    else:
                        our_cards.append(card)
        opponents_unplayed_cards = Cards(opponents_unplayed_cards).list

        # long_player = self.long_seat(suit.name)
        our_length = len(self.our_unplayed_cards[suit.name])
        opponents_length = len(opponents_unplayed_cards)

        for index, card in enumerate(our_cards):
            if index >= min(opponents_length, our_length):
                return True
            if card.value < opponents_unplayed_cards[0].value:
                return False
        else:
            return False

    def dummy_holds_adjacent_card(self, card: Card) -> bool:
        """Return True if the hand contains the adjacent card."""
        cards = self.dummys_suit_cards[card.suit.name]
        for other_card in cards:
            if (other_card.value == card.value + 1 or
                    other_card.value == card.value - 1):
                return True
        return False

    def partnership_long_suits(self, ignore_trumps=True):
        """Return a list of the longest partnership suits."""
        suits = {suit_name: len(self.our_unplayed_cards[suit_name])
                 for suit_name in SUITS}
        if self.trump_suit:
            if ignore_trumps:
                suits.pop(self.trump_suit.name)
        long_suits = get_list_of_best_scores(suits)
        return long_suits

    def can_lead_toward_tenace(self, long_suit: str) -> bool:
        """Return True if we can lead to higher honour in partner's hand."""
        if (self.partners_unplayed_cards[long_suit] and
                self.suit_cards[long_suit]):
            partners_best_card = self.partners_unplayed_cards[long_suit][0]
            my_best_card = self.unplayed_cards[long_suit][0]
            if partners_best_card.is_honour:
                if partners_best_card.value > my_best_card.value + 1:
                    return True
        return False

    def get_winners(self) -> int:
        """Return the current number of winners for declarer."""
        winners = 0
        for suit_name in SUITS:
            for card in self.our_unplayed_cards[suit_name]:
                if self.opponents_unplayed_cards[suit_name]:
                    unplayed_cards = self.opponents_unplayed_cards[suit_name]
                    opponents_top_card_value = unplayed_cards[0].value
                    if card.value > opponents_top_card_value:
                        winners += 1
                    else:
                        break
                else:
                    winners += 1
        return winners

    def _get_controls(self) -> dict[str, int]:
        """Return the current number of winners for declarer."""
        controls = {suit_name: 0 for suit_name in SUITS}
        for suit_name in SUITS:
            for card in self.our_unplayed_cards[suit_name]:
                unplayed_cards = self.opponents_unplayed_cards[suit_name]
                if unplayed_cards:
                    if unplayed_cards and card.value < unplayed_cards[0].value:
                        break
                    controls[suit_name] += 1
                else:
                    controls[suit_name] += 1
        return controls

    def _get_second_round_controls(self) -> dict[str, int]:
        """Return the current number of second round controls for declarer."""
        controls = {suit_name: False for suit_name in SUITS}
        for suit_name in SUITS:
            if len(self.our_unplayed_cards[suit_name]) >= 2:
                if len(self.opponents_unplayed_cards[suit_name]) <= 1:
                    controls[suit_name] = True
                    continue

                our_unplayed_cards = self.our_unplayed_cards[suit_name]
                opponents_cards = self.opponents_unplayed_cards[suit_name]
                if our_unplayed_cards[1].value > opponents_cards[1].value:
                    controls[suit_name] = True
        return controls

    def _get_trick_count(self) -> int:
        """Return the number of tricks won by declarer."""
        if self.declarer in 'NS':
            return (self.board.NS_tricks, self.board.EW_tricks)
        return (self.board.EW_tricks, self.board.NS_tricks)

    def get_entries(self, hand):
        """Return the controlling card in a suit."""
        entries = {suit_name: [] for suit_name in SUITS}
        unplayed_cards = Cards(hand.unplayed_cards)
        suit_cards = unplayed_cards.by_suit
        for suit_name in SUITS:
            cards = suit_cards[suit_name]
            for card in cards:
                if self._is_master(card, entries):
                    entries[suit_name].append(card)
                else:
                    break
        return entries

    def is_master_card(self, card: Card) -> bool:
        """Return True if card is a master."""
        unplayed_cards = self.total_unplayed_cards[card.suit]
        for unplayed_card in unplayed_cards:
            if unplayed_card.value > card.value:
                return False
        return True

    def _is_master(self, card: Card,
                   other_masters: dict[str, list[Card]]) -> bool:
        """Return True if card is a master."""
        unplayed_cards = self.total_unplayed_cards[card.suit]
        for master_card in other_masters[card.suit.name]:
            if master_card in unplayed_cards:
                unplayed_cards.remove(master_card)
        for unplayed_card in unplayed_cards:
            if unplayed_card.value > card.value:
                return False
        return True

    def is_winner_declarer(self, card: Card, trick: Trick = None) -> bool:
        """Return True is the card is a winner for declarer."""
        suit = card.suit.name
        opponents_unplayed_cards = [
            card for card in self.opponents_unplayed_cards[suit]
            ]
        if trick:
            if trick.leader in (self.seat, self.partner_seat):
                if len(trick.cards) > 1:
                    if trick.cards[1].suit.name == suit:
                        opponents_unplayed_cards.append(trick.cards[1])
                    fourth_player = SEATS[(SEATS.index(trick.leader) + 3) % 4]
                    if self.voids[fourth_player][trick.suit.name]:
                        opponents_unplayed_cards = []
        if not opponents_unplayed_cards:
            return True
        if card.value > sorted(opponents_unplayed_cards,
                               reverse=True)[0].value:
            return True
        return False

    def is_winner_defender(self, trick_card: Card,
                           trick: Trick = None) -> bool:
        """Return True is the card is a winner for defender."""
        card_value = trick_card.value
        if trick:
            if trick.cards[0].value > trick_card.value:
                return False
            if len(trick.cards) == 3:
                value_2 = trick.cards[2].value
                if self.trump_suit:
                    if trick.cards[2].suit == self.trump_suit:
                        value_2 += 13
                    if trick.card.suit == self.trump_suit:
                        card_value += 13
                        card_value = trick_card.value
                if value_2 > card_value:
                    return False
            suit = trick.suit
        else:
            suit = trick_card.suit

        # Get all unplayed cards in the suit
        unplayed_cards = [card
                          for card in self.total_unplayed_cards[suit.name]]

        # Remove dummy's card if it's already played
        if self.dummy_on_right and trick:
            for card in self.dummys_unplayed_cards[suit.name]:
                unplayed_cards.remove(card)

        # Remove my unplayed cards
        for card in self.unplayed_cards[suit.name]:
            unplayed_cards.remove(card)

        if not unplayed_cards:
            return True
        if card_value > unplayed_cards[0].value:
            return True
        return False

    def get_entries_in_other_suits(self, hand: Hand, suit: Suit):
        """Return the entries in a hand other than in the given suit."""
        entries = []
        for suit_name in SUITS:
            if suit_name != suit.name:
                cards = self.get_entries(hand)[suit_name]
                entries.extend(cards)
        return entries

    def missing_honours(self, suit: Suit) -> list[Card]:
        """Return a list of missing honours in the suit."""
        our_cards = self.our_unplayed_cards[suit]
        missing_honours = []
        for index, rank in enumerate('AKQJT'):
            card = Card(rank, suit.name)
            if card in self.total_unplayed_cards[suit]:
                if card not in our_cards:
                    missing_honours.append(card)
        return missing_honours

    def control_suit(self, suit: Suit) -> bool:
        """Return True if player totally controls suit."""
        our_cards = self.our_unplayed_cards[suit.name]
        opponents_cards = self.opponents_unplayed_cards[suit.name]
        if not opponents_cards:
            return True
        index = len(opponents_cards) - 1
        if index > len(our_cards) - 1:
            return False
        if opponents_cards[0].value > our_cards[index].value:
            return True
        return True

    def card_from_tenace(self) -> Card:
        """Return the bottom from a tenace in my hand with one threat."""
        trick = self.board.tricks[-1]
        cards = self.cards_for_trick_suit(trick)
        for index, card in enumerate(cards[1:]):
            if cards[index].value - card.value > 1:
                threats = 0
                for opps_card in self.opponents_unplayed_cards[trick.suit]:
                    if cards[index].value > opps_card.value > card.value:
                        threats += 1
                if threats <= 1:
                    return card
        return None

    def card_from_tenace_threat(self) -> tuple[Card, Card]:
        """Return the top and bottom from a tenace in my hand."""
        trick = self.board.tricks[-1]
        suit = trick.suit.name
        cards = self.cards_for_trick_suit(trick)
        higher_card = None
        threats = self._get_threats()
        if not threats[suit]:
            return (None, None)

        for threat in threats[suit]:
            if threat.rank != 'A':
                for value in range(threat.value+1, 14):
                    card = Card(CARD_VALUES[value], suit)
                    if card in cards:
                        higher_card = card
                        break
                    elif card in self.total_unplayed_cards[suit]:
                        return (None, None)
                if not higher_card:
                    return (None, None)

                for value in reversed(range(threat.value)):
                    card = Card(CARD_VALUES[value], suit)
                    if card in cards:
                        return (higher_card, card)
                    if card in self.total_unplayed_cards[suit]:
                        return (None, None)
        return (None, None)

    def touching_honours(self, cards: list[Card]) -> Card | None:
        """Return the top of touching honours if
        there is one or None otherwise."""
        for index, card in enumerate(cards[:-1]):
            if card.is_honour and card.value == cards[index+1].value + 1:
                return card
        return None

    def touching_honours_in_hand(self, hand: Hand, suit: str) -> Card | None:
        """Return the top of touching honours if
        there is one or None otherwise."""
        cards = Cards(hand.unplayed_cards).by_suit[suit]
        for index, card in enumerate(cards[:-1]):
            if card.is_honour and card.value == cards[index+1].value + 1:
                return card
        return None

    def _longest_suit(self) -> Suit:
        """Return the longest suit in the hand."""
        lengths = {suit: 0 for suit in SUITS}
        for suit in SUITS:
            lengths[suit] = len(self.unplayed_cards[suit])
        long_suits = get_list_of_best_scores(lengths)
        if len(long_suits) == 1:
            return Suit(long_suits[0])

        strength = {suit: 0 for suit in long_suits}
        for suit in long_suits:
            strength[suit] = get_suit_strength(self.unplayed_cards[suit])
        strong_suits = get_list_of_best_scores(lengths)
        if len(strong_suits) == 1:
            return Suit(strong_suits[0])
        return Suit(strong_suits[0])

    def _get_suit_rounds(self) -> dict[str, int]:
        """Return a dict of rounds played by suit."""
        rounds = {suit: 0 for suit in SUITS}
        for trick in self.board.tricks[:-1]:
            rounds[trick.suit.name] += 1
        return rounds

    def is_tenace(self, card_1: Card, card_2: Card, gap: int = 1) -> bool:
        """Return True if card_1 and card_2 form a tenace."""
        if card_1.suit != card_2.suit:
            return False
        suit = card_1.suit.name
        our_cards = self.our_unplayed_cards[suit]
        if card_1.value > card_2.value:
            top_card = card_1
            bottom_card = card_2
        elif card_1.value < card_2.value:
            top_card = card_2
            bottom_card = card_1
        else:
            return False

        cards = SuitCards(suit).sorted_cards()
        missing_masters = 0
        top_card_check = True
        bottom_card_check = True
        for card in cards:
            if (top_card_check and card != top_card and
                    card not in our_cards and
                    card in self.total_unplayed_cards[suit]):
                return False
            if bottom_card_check and not top_card_check:
                if (card != bottom_card and
                        card not in our_cards and
                        card in self.total_unplayed_cards[suit]):
                    missing_masters += 1
            if card == top_card:
                top_card_check = False
            if card == bottom_card:
                bottom_card_check = False
        if missing_masters == gap:
            return True
        return False

    def _get_threats(self) -> dict[str, Card]:
        """Return a dict of cards by suit that threaten players cards."""
        if self.trump_suit:
            return self._get_threats_suit_contract()
        else:
            return self._get_threats_nt_contract()

    def _get_threats_nt_contract(self) -> dict[str, Card]:
        """Return a dict of cards by suit that threaten players cards."""

        threats = {suit: [] for suit in SUITS}
        ranks = [rank for rank in RANKS]
        ranks.reverse()
        sorted_ranks = ranks[:-1]

        for suit in SUITS:
            long_cards = self.unplayed_cards[suit]
            our_cards = self.our_unplayed_cards[suit]
            opponents_cards = self.opponents_unplayed_cards[suit]
            missing = len(opponents_cards)
            winners = 0
            skip_card = False
            for index, rank in enumerate(sorted_ranks):
                ranking_card = Card(rank, suit)
                if ranking_card in self.total_unplayed_cards[suit]:
                    if ranking_card in our_cards:
                        if not skip_card:
                            winners += 1
                        skip_card = False

                        # No more cards to lose
                        if winners > missing:
                            break
                    else:
                        threats[suit].append(ranking_card)
                        # skip card means that the next card in the suit is
                        # assumed to have been beaten
                        skip_card = True

                    # threats only in long hand
                    if index + 1 >= len(long_cards):
                        break
                if len(opponents_cards) <= index + 1:
                    break
        return threats

    def _get_threats_suit_contract(self) -> dict[str, Card]:
        """Return a dict of cards by suit that threaten players cards."""
        (long_hand, short_hand) = self.get_long_short_trump_hands()
        unplayed_cards = self.cards_by_suit(long_hand)
        long_cards = unplayed_cards[self.trump_suit.name]

        threats = {suit: [] for suit in SUITS}
        ranks = [rank for rank in RANKS]
        ranks.reverse()
        sorted_ranks = ranks[:-1]

        for suit in SUITS:
            our_cards = self.our_unplayed_cards[suit]
            my_cards = self.unplayed_cards[suit]
            partners_cards = self.partners_unplayed_cards[suit]
            max_length = max(len(my_cards), len(partners_cards))
            opponents_cards = self.opponents_unplayed_cards[suit]
            missing = len(opponents_cards)
            winners = 0
            skip_card = False
            for index, rank in enumerate(sorted_ranks):
                ranking_card = Card(rank, suit)
                if ranking_card in self.total_unplayed_cards[suit]:
                    if ranking_card in our_cards:
                        if not skip_card:
                            winners += 1
                        skip_card = False

                        # Only count to the number of cards in our hands
                        if index + 1 >= max_length:
                            break

                        # No more cards to lose
                        if winners > missing:
                            break
                    else:
                        threats[suit].append(ranking_card)
                        # skip card means that the next card in the suit is
                        # assumed to have been beaten
                        skip_card = True

                    # threats only in long hand
                    if index + 1 >= len(long_cards):
                        break
                if len(opponents_cards) <= index + 1:
                    break
        return threats

    def get_long_short_trump_hands(self) -> tuple[Hand, Hand]:
        """Return the  hands for long and short trump hand between
        player and partner."""
        return self.get_long_short_hands(self.trump_suit)

    def get_long_short_hands(self, suit: Suit) -> tuple[Hand, Hand]:
        """Return the  hands for long and short hand between
        player and partner."""
        my_unplayed_cards = self.unplayed_cards[suit.name]
        partners_unplayed_cards = self.partners_unplayed_cards[suit.name]
        if len(my_unplayed_cards) >= len(partners_unplayed_cards):
            return (self.hand, self.partners_hand)
        else:
            return (self.partners_hand, self.hand)

    def _get_suit_winners(self) -> dict[str, Card]:
        """Return a dict of cards by suit that are certain winners."""
        winners = {suit: [] for suit in SUITS}
        our_cards = self.our_unplayed_cards
        opponents_cards = self.opponents_unplayed_cards
        for suit in SUITS:
            our_length = self._get_our_length(suit)
            for card in our_cards[suit]:
                if len(winners[suit]) < our_length:
                    if opponents_cards[suit]:
                        if card.value > opponents_cards[suit][0].value:
                            winners[suit].append(card)
                    else:
                        winners[suit].append(card)
        return winners

    def _get_suit_losers(self) -> dict[str, Card]:
        """Return a dict of cards by suit that are potential losers."""
        losers = {suit: [] for suit in SUITS}
        our_cards = self.our_unplayed_cards
        opponents_cards = self.opponents_unplayed_cards
        for suit in SUITS:
            our_length = self._get_our_length(suit)
            opponents_top_card = 0
            for card in our_cards[suit][:our_length]:
                if len(losers[suit]) < our_length:
                    if len(opponents_cards[suit]) >= opponents_top_card + 1:
                        opps_card = opponents_cards[suit][opponents_top_card]
                        top_value = opps_card.value
                        if card.value < top_value:
                            losers[suit].append(card)
                            opponents_top_card += 1
        return losers

    def _get_our_length(self, suit: str) -> int:
        my_cards = self.unplayed_cards
        partners_cards = self.partners_unplayed_cards
        if len(my_cards[suit]) > len(partners_cards[suit]):
            return len(my_cards[suit])
        return len(partners_cards[suit])

    def _get_current_sure_tricks(self) -> list[Card]:
        """Return a list of certain winners based on unplayed cards."""
        sure_tricks = []
        declarers_cards = self.unplayed_cards
        dummys_cards = self.partners_unplayed_cards
        for suit in SUITS:
            declarer_suit_cards = [card for card in declarers_cards[suit]]
            dummy_suit_cards = [card for card in dummys_cards[suit]]
            our_cards = CardArray.sort_cards(
                declarer_suit_cards + dummy_suit_cards
                )
            our_length = max(len(declarer_suit_cards), len(dummy_suit_cards))
            for card in our_cards[:our_length]:
                if self.is_winner_declarer(card, self.board.tricks[-1]):
                    sure_tricks.append(card)
        return sure_tricks

    def _get_current_probable_tricks(self) -> tuple[dict[str, list[Card]]]:
        """Return a dict of probable winners by suit based on
        unplayed cards."""
        opponents_length = {
            8: 5,
            7: 4,
            6: 4,
            5: 3,
            4: 3,
            3: 2,
            2: 2,
            1: 1,
            0: 0,
        }
        return self._current_trick_calculation(opponents_length)

    def _get_current_possible_tricks(self) -> tuple[dict[str, list[Card]]]:
        """Return a dict of possible winners by suit based on
        unplayed cards."""
        opponents_length = {
            8: 4,
            7: 4,
            6: 3,
            5: 3,
            4: 2,
            3: 2,
            2: 1,
            1: 1,
            0: 0,
        }
        return self._current_trick_calculation(opponents_length)

    def _current_trick_calculation(self,
                                   opponents_length: dict[int, int]
                                   ) -> tuple[dict[str, list[Card]]]:
        """Return a dict of winners by suit based on unplayed cards."""
        probable_tricks = []
        declarers_cards = self.unplayed_cards
        dummys_cards = self.partners_unplayed_cards
        opponents_cards = self.opponents_unplayed_cards
        for suit in SUITS:
            declarer_suit_cards = [card for card in declarers_cards[suit]]
            dummy_suit_cards = [card for card in dummys_cards[suit]]
            opponents_holding = (len(self.total_unplayed_cards[suit])
                                 - len(declarer_suit_cards)
                                 - len(dummy_suit_cards))

            if opponents_holding in opponents_length:
                # Honours
                honours = SuitCards(suit).cards('A', 'T')
                opponents_honours = 0
                for index, card in enumerate(honours):
                    if index < opponents_length[opponents_holding]:
                        if card in opponents_cards[suit]:
                            opponents_honours += 1
                opponents_count = min(
                    opponents_length[opponents_holding],
                    opponents_honours
                    )
                opponents_count = opponents_length[opponents_holding]

                # Length
                our_length = max(
                    len(declarer_suit_cards),
                    len(dummy_suit_cards)
                    )
                if len(declarer_suit_cards) > len(dummy_suit_cards):
                    our_long_hand = declarer_suit_cards
                else:
                    our_long_hand = dummy_suit_cards

                if our_long_hand:
                    range_limit = our_length - opponents_count
                    for index in range(range_limit):
                        card = our_long_hand[-index]
                        if card not in self.sure_tricks.cards:
                            probable_tricks.append(card)
        return probable_tricks

    def _get_possible_promotions(self):
        """Return a dict of possible promotions
        by suit based on unplayed cards."""
        def check_card(self, hand, card, buffer):
            """Return True if the card is a candidate for promotion."""
            if (card in hand and
                    len(hand) >= buffer and
                    card not in self.sure_tricks.cards):
                return True
            return False

        possible_promotions = []
        declarers_cards = self.unplayed_cards
        dummys_cards = self.partners_unplayed_cards
        for suit in SUITS:
            if suit not in self.probable_tricks.suits:
                honours = SuitCards(suit).cards('K', 'T')
                for hand in [declarers_cards[suit], dummys_cards[suit]]:
                    for index, card in enumerate(honours):
                        if check_card(self, hand, card, 2+index):
                            possible_promotions.append(card)
        return possible_promotions

    def _get_current_entries(self) -> tuple[dict[str, list[Card]]]:
        """Return a dict of probable entries by
        suit based on unplayed cards."""
        my_entries = {suit: [] for suit in SUITS}
        partners_entries = {suit: [] for suit in SUITS}
        for suit in SUITS:
            my_cards = self.unplayed_cards[suit]
            partners_cards = self.partners_unplayed_cards[suit]
            if my_cards and partners_cards:
                if (self.is_winner_declarer(my_cards[0]) and
                        my_cards[0].value > partners_cards[-1].value):
                    my_entries[suit] = my_cards[0]
                if (self.is_winner_declarer(partners_cards[0]) and
                        partners_cards[0].value > my_cards[-1].value):
                    partners_entries[suit] = partners_cards[0]
        return (my_entries, partners_entries)

    def _get_voids(self):
        # Record voids
        voids = {seat: {suit: False for suit in SUITS} for seat in SEATS}
        for trick in self.board.tricks:
            for index, card in enumerate(trick.cards[1:]):
                if card.suit != trick.suit:
                    seat_index = (SEATS.index(trick.leader) + index + 1) % 4
                    voids[SEATS[seat_index]][trick.suit.name] = True
        return voids

    def _get_winner_count(self) -> int:
        """Return the total number of winners."""
        winner_count = 0
        for cards in self.winners.values():
            winner_count += len(cards)
        return winner_count

    # def _get_threats(self) -> dict[str, Card]:
    #     """Return a dict of cards by suit that threaten players cards."""
    #     if self.trump_suit:
    #         return self._get_threats_suit_contract()
    #     return self._get_threats_nt_contract()

    # def _get_threats_nt_contract(self) -> dict[str, Card]:
    #     """Return a dict of cards by suit that threaten players cards."""
    #     threats = {suit: [] for suit in SUITS}
    #     ranks = [rank for rank in RANKS]
    #     ranks.reverse()
    #     sorted_ranks = ranks[:-1]

    #     for suit in SUITS:
    #         long_cards = self.unplayed_cards[suit]
    #         our_cards = self.our_unplayed_cards[suit]
    #         opponents_cards = self.opponents_unplayed_cards[suit]
    #         missing = len(opponents_cards)
    #         winners = 0
    #         skip_card = False
    #         for index, rank in enumerate(sorted_ranks):
    #             ranking_card = Card(rank, suit)
    #             if ranking_card in self.total_unplayed_cards[suit]:
    #                 if ranking_card in our_cards:
    #                     if not skip_card:
    #                         winners += 1
    #                     skip_card = False

    #                     # No more cards to lose
    #                     if winners > missing:
    #                         break
    #                 else:
    #                     threats[suit].append(ranking_card)
    #                     # skip card means that the next card in the suit is
    #                     # assumed to have been beaten
    #                     skip_card = True

    #                 # threats only in long hand
    #                 if index + 1 >= len(long_cards):
    #                     break
    #             if len(opponents_cards) <= index + 1:
    #                 break
    #     return threats

    # def _get_threats_suit_contract(self) -> dict[str, Card]:
    #     """Return a dict of cards by suit that threaten players cards."""
    #     (long_hand, short_hand) = self.get_long_short_trump_hands()
    #     unplayed_cards = self.cards_by_suit(long_hand)
    #     long_cards = unplayed_cards[self.trump_suit.name]

    #     threats = {suit: [] for suit in SUITS}
    #     ranks = [rank for rank in RANKS]
    #     ranks.reverse()
    #     sorted_ranks = ranks[:-1]

    #     for suit in SUITS:
    #         our_cards = self.our_unplayed_cards[suit]
    #         my_cards = self.unplayed_cards[suit]
    #         partners_cards = self.partners_unplayed_cards[suit]
    #         max_length = max(len(my_cards), len(partners_cards))
    #         opponents_cards = self.opponents_unplayed_cards[suit]
    #         missing = len(opponents_cards)
    #         winners = 0
    #         skip_card = False
    #         for index, rank in enumerate(sorted_ranks):
    #             ranking_card = Card(rank, suit)
    #             if ranking_card in self.total_unplayed_cards[suit]:
    #                 if ranking_card in our_cards:
    #                     if not skip_card:
    #                         winners += 1
    #                     skip_card = False

    #                     # Only count to the number of cards in our hands
    #                     if index + 1 >= max_length:
    #                         break

    #                     # No more cards to lose
    #                     if winners > missing:
    #                         break
    #                 else:
    #                     threats[suit].append(ranking_card)
    #                     # skip card means that the next card in the suit is
    #                     # assumed to have been beaten
    #                     skip_card = True

    #                 # threats only in long hand
    #                 if index + 1 >= len(long_cards):
    #                     break
    #             if len(opponents_cards) <= index + 1:
    #                 break
    #     return threats
