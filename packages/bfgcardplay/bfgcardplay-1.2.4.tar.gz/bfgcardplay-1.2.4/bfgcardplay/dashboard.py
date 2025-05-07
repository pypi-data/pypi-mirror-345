"""Provide the Dashboard class for bfgcardplay."""

from dataclasses import dataclass

from bridgeobjects import Hand, Card, Suit, SUITS, RANKS
from .data_classes import SuitCards, CardArray

SPLIT_PROBABILITIES = {
    '3-3': 35.5,
    '4-2': 48.3,
    '5-1': 14.5,
    '6-0': 1.5,
    '3-2': 67.8,
    '4-1': 28.3,
    '5-0': 3.9,
    '3-1': 49.7,
    '2-2': 40.7,
    '4-0': 9.5,
    '2-1': 78,
    '3-0': 22,
    '1-1': 52,
    '2-0': 48,
}

SPLITS = {
    6: ['3-3', '4-2', '5-1', '6-0'],
    5: ['3-2', '4-1', '5-0'],
    4: ['3-1', '2-2', '4-0'],
    3: ['2-1', '3-0'],
    2: ['1-1', '2-0'],
}


@dataclass
class SplitWinners:
    split: str
    probability: float
    cards: str


class Dashboard():
    "Statistics for a player."
    def __init__(self, player) -> None:
        self.suits = {suit: {} for suit in SUITS}
        self.player = player
        # self.threats = self._get_threats()
        # self.losers = self._get_losers()
        self.winners = self.player.winners
        self.losers = self.player.losers
        self.split_winners = self._get_split_winners()
        self.winner_count = self._get_winner_count()
        self.suit_lengths = self._suit_lengths()
        self.extra_winners_length = self._extra_winners_length()
        # extra_winners_strength must be generated after winners
        self.extra_winners_strength = self._extra_winners_strength()
        self.tricks_needed = 6 + int(player.board.contract.name[0])

        self.sure_tricks = CardArray(self._get_current_sure_tricks())
        self.probable_tricks = CardArray(self._get_current_probable_tricks())
        self.possible_tricks = CardArray(self._get_current_possible_tricks())
        self.possible_promotions = CardArray(self._get_possible_promotions())

        (my_entries, partners_entries) = self._get_current_entries()
        self.entries = my_entries
        self.partners_entries = partners_entries

    def __repr__(self):
        print(f'{"threats":<10}{self.threats}')
        print(f'{"winners":<10}{self.winners}')
        print(f'{"suit_lens":<10}{self.suit_lengths}')
        # print(f'{"threats":<10}{self.extra_winners_length}')
        # print(f'{"threats":<10}{self.extra_winners_strength}')
        return ''

    def _get_current_sure_tricks(self) -> list[Card]:
        """Return a list of certain winners based on unplayed cards."""
        player = self.player
        sure_tricks = []
        declarers_cards = player.unplayed_cards
        dummys_cards = player.partners_unplayed_cards
        for suit in SUITS:
            declarer_suit_cards = [card for card in declarers_cards[suit]]
            dummy_suit_cards = [card for card in dummys_cards[suit]]
            suit_cards = declarer_suit_cards + dummy_suit_cards
            our_cards = CardArray.sort_cards(suit_cards)
            our_length = max(len(declarer_suit_cards), len(dummy_suit_cards))
            for card in our_cards[:our_length]:
                if player.is_winner_declarer(card, player.board.tricks[-1]):
                    sure_tricks.append(card)
        return sure_tricks

    def _get_current_probable_tricks(self) -> tuple[dict[str, list[Card]]]:
        """Return a dict of probable winners by
        suit based on unplayed cards."""
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
        """Return a dict of possible winners by suit based
        on unplayed cards."""
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

    def _current_trick_calculation(
            self,
            opponents_length: dict[int, int]
            ) -> tuple[dict[str, list[Card]]]:
        """Return a dict of winners by suit based on unplayed cards."""
        player = self.player
        probable_tricks = []
        declarers_cards = player.unplayed_cards
        dummys_cards = player.partners_unplayed_cards
        opponents_cards = player.opponents_unplayed_cards
        for suit in SUITS:
            declarer_suit_cards = [card for card in declarers_cards[suit]]
            dummy_suit_cards = [card for card in dummys_cards[suit]]
            opponents_holding = (len(player.total_unplayed_cards[suit])
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
                    opponents_honours)
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
            if (card in hand and len(hand) >= buffer and
                    card not in self.sure_tricks.cards):
                return True
            return False

        player = self.player
        possible_promotions = []
        declarers_cards = player.unplayed_cards
        dummys_cards = player.partners_unplayed_cards
        for suit in SUITS:
            if suit not in self.probable_tricks.suits:
                honours = SuitCards(suit).cards('K', 'T')
                for hand in [declarers_cards[suit], dummys_cards[suit]]:
                    for index, card in enumerate(honours):
                        if check_card(self, hand, card, 2+index):
                            possible_promotions.append(card)
        return possible_promotions

    def _get_current_entries(self) -> tuple[dict[str, list[Card]]]:
        """Return a dict of probable entries by suit based
        on unplayed cards."""
        player = self.player
        my_entries = {suit: [] for suit in SUITS}
        partners_entries = {suit: [] for suit in SUITS}
        for suit in SUITS:
            my_cards = player. unplayed_cards[suit]
            partners_cards = player.partners_unplayed_cards[suit]
            if my_cards and partners_cards:
                if (player.is_winner_declarer(my_cards[0]) and
                        my_cards[0].value > partners_cards[-1].value):
                    my_entries[suit] = my_cards[0]
                if (player.is_winner_declarer(partners_cards[0]) and
                        partners_cards[0].value > my_cards[-1].value):
                    partners_entries[suit] = partners_cards[0]
        return (my_entries, partners_entries)

    # def _get_entries_for_hand(self, my_cards, partners_cards):
    #     player = self.player
    #     entries = {suit: [] for suit in SUITS}
    #     for suit in SUITS:
    #         cards = my_cards[suit]
    #         if cards:
    #             if (player.is_winner_declarer(cards[0]) and
    #                     cards[0].value > partners_cards[suit][-1].value):
    #                 entries[suit] = cards[0]
    #     return entries

    # def _get_threats(self) -> dict[str, Card]:
    #     """Return a dict of cards by suit that threaten players cards."""
    #     if self.player.trump_suit:
    #         return self._get_threats_suit_contract()
    #     else:
    #         return self._get_threats_nt_contract()

    def _get_threats_nt_contract(self) -> dict[str, Card]:
        """Return a dict of cards by suit that threaten players cards."""
        player = self.player

        threats = {suit: [] for suit in SUITS}
        ranks = [rank for rank in RANKS]
        ranks.reverse()
        sorted_ranks = ranks[:-1]

        for suit in SUITS:
            long_cards = player.unplayed_cards[suit]
            our_cards = player.our_unplayed_cards[suit]
            opponents_cards = player.opponents_unplayed_cards[suit]
            missing = len(opponents_cards)
            winners = 0
            skip_card = False
            for index, rank in enumerate(sorted_ranks):
                ranking_card = Card(rank, suit)
                if ranking_card in player.total_unplayed_cards[suit]:
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
        player = self.player
        (long_hand, short_hand) = self.get_long_short_trump_hands()
        unplayed_cards = player.cards_by_suit(long_hand)
        long_cards = unplayed_cards[player.trump_suit.name]

        threats = {suit: [] for suit in SUITS}
        ranks = [rank for rank in RANKS]
        ranks.reverse()
        sorted_ranks = ranks[:-1]

        for suit in SUITS:
            our_cards = player.our_unplayed_cards[suit]
            my_cards = player.unplayed_cards[suit]
            partners_cards = player.partners_unplayed_cards[suit]
            max_length = max(len(my_cards), len(partners_cards))
            opponents_cards = player.opponents_unplayed_cards[suit]
            missing = len(opponents_cards)
            winners = 0
            skip_card = False
            for index, rank in enumerate(sorted_ranks):
                ranking_card = Card(rank, suit)
                if ranking_card in player.total_unplayed_cards[suit]:
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
        return self.get_long_short_hands(self.player.trump_suit)

    def get_long_short_hands(self, suit: Suit) -> tuple[Hand, Hand]:
        """Return the  hands for long and short hand between
        player and partner."""
        player = self.player
        my_unplayed_cards = player.unplayed_cards[suit.name]
        partners_unplayed_cards = player.partners_unplayed_cards[suit.name]
        if len(my_unplayed_cards) >= len(partners_unplayed_cards):
            return (player.hand, player.partners_hand)
        else:
            return (player.partners_hand, player.hand)

    def _get_split_winners(self) -> dict[str, Card]:
        """Return a dict of cards by suit that are
        certain winners depending on splits."""
        player = self.player
        opponents_cards = player.opponents_unplayed_cards
        split_winners = {suit: [] for suit in SUITS}
        for suit in SUITS:
            if len(opponents_cards[suit]) in SPLITS:
                splits = SPLITS[len(opponents_cards[suit])]
                for split in splits:
                    winners = self._split_winners(suit, split)
                    split_winners[suit].append(winners)
        return split_winners

    def _split_winners(self, suit, split):
        player = self.player
        our_cards = player.our_unplayed_cards
        our_length = self._get_our_length(player, suit)
        opponents_cards = player.opponents_unplayed_cards
        split_winners = SplitWinners(split, SPLIT_PROBABILITIES[split], '')
        opps_suit_cards = opponents_cards[suit][:int(split[0])]
        for index, card in enumerate(our_cards[suit]):
            split_winners.cards += self._split_winner(index,
                                                      card, opps_suit_cards,
                                                      split_winners.cards,
                                                      our_length)
        return split_winners

    @staticmethod
    def _split_winner(index, card, opps_suit_cards, cards, our_length):
        if index < len(opps_suit_cards):
            if len(cards) < our_length:
                if opps_suit_cards:
                    if card.value > opps_suit_cards[0].value:
                        return card.rank
        elif index < our_length:
            return card.rank
        return ''

    @staticmethod
    def _get_our_length(player: object, suit: str) -> int:
        my_cards = player.unplayed_cards
        partners_cards = player.partners_unplayed_cards
        if len(my_cards[suit]) > len(partners_cards[suit]):
            return len(my_cards[suit])
        return len(partners_cards[suit])

    def _suit_lengths(self) -> dict[str, int]:
        """Return a dict of suit_lengths."""
        player = self.player
        suit_lengths = {suit: [] for suit in SUITS}
        our_cards = player.our_unplayed_cards
        for suit in SUITS:
            suit_lengths[suit] = len(our_cards[suit])
        return suit_lengths

    def _extra_winners_length(self):
        """Return a dict of potential extra length winners by suit."""
        player = self.player
        splits = {
            6: 4,
            5: 3,
            4: 3,
            3: 2,
            2: 2,
            1: 1,
            0: 0,
        }
        extra_winners = {suit: 0 for suit in SUITS}
        our_cards = player.our_unplayed_cards
        my_cards = player.unplayed_cards
        partners_cards = player.partners_unplayed_cards
        opponents_cards = player.opponents_unplayed_cards
        for suit in SUITS:
            if not len(our_cards[suit]) > len(opponents_cards[suit]):
                break
            our_length = max(len(my_cards[suit]), len(partners_cards[suit]))
            split = splits[len(opponents_cards[suit])]
            extra_winners[suit] = our_length - split
        return extra_winners

    def _extra_winners_strength(self):
        """Return a dict of potential extra strength winners by suit."""
        player = self.player
        extra_winners = {suit: [] for suit in SUITS}
        our_cards = player.our_unplayed_cards
        opponents_cards = player.opponents_unplayed_cards
        honours = 'AKQJT'
        for suit in SUITS:
            our_length = self._get_our_length(player, suit)
            for honour in honours:
                cards = our_cards[suit]
                test_card = Card(honour, suit)
                if test_card in opponents_cards[suit]:
                    test_cards = []
                    for rank in honours.replace(honour, ''):
                        test_cards.append(Card(rank, suit))
                    for index, card in enumerate(test_cards):
                        if card in cards and our_length >= index + 2:
                            if (card not in extra_winners[suit] and
                                    card not in self.winners[suit]):
                                extra_winners[suit].append(card)
        return extra_winners

    def _get_winner_count(self) -> int:
        """Return the total number of winners."""
        winner_count = 0
        for suit, cards in self.winners.items():
            winner_count += len(cards)
        return winner_count
