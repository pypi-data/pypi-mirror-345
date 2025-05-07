"""BfG Cardplay utilities."""

from bridgeobjects import Suit, SUITS, Card, SEATS, CARD_VALUES
from bfgdealer import Trick
# from .player import Player

MODULE_COLOUR = 'blue'


def get_list_of_best_scores(candidates: dict[object, int],
                            reverse: bool = False) -> list[object]:
    """Return a list of the best scoring candidates
    from a dict of candidates."""
    best_candidates = []
    (min_score, max_score) = _min_max_score(candidates, reverse)

    for key, score in candidates.items():
        if reverse:
            if score == min_score:
                best_candidates.append(key)
        else:
            if score == max_score:
                best_candidates.append(key)
    return best_candidates


def get_list_of_best_suits(player: object) -> list[object]:
    """Return a list of the best scoring candidates from a
    dict of candidates."""
    winners = {suit: len(player.winners[suit]) for suit in SUITS}
    losers = {suit: len(player.losers[suit]) for suit in SUITS}
    best_candidates = []
    scores = {}
    max_score = 99
    # for suit in SUITS:
    #     score = winners[suit] - losers[suit]
    #     ic(suit, score)
    #     scores[suit] = score
    #     if score > max_score:
    #         max_score = score

    for suit in SUITS:
        score = winners[suit] - losers[suit]
        scores[suit] = losers[suit]
        if score < max_score:
            max_score = score

    best_candidates = []
    for suit in SUITS:
        if scores[suit] == max_score:
            best_candidates.append(suit)
    return best_candidates


def _min_max_score(candidates: dict[object, int],
                   reverse: bool = False) -> int:
    """Return the maximum score from candidates."""
    max_score = 0
    min_score = 0
    for key, score in candidates.items():
        if score > max_score:
            max_score = score

    if reverse:
        min_score = max_score
        for key, score in candidates.items():
            if score < min_score:
                min_score = score
    return (min_score, max_score)


def other_suit_for_signals(suit: Suit) -> str:
    """Return the other suit for signalling."""
    if suit.name == 'S':
        other_suit = 'C'
    elif suit.name == 'C':
        other_suit = 'S'
    elif suit.name == 'H':
        other_suit = 'D'
    elif suit.name == 'D':
        other_suit = 'H'
    return other_suit


def get_suit_strength(cards: list[Card]) -> dict[str, int]:
    """Return a dict of suit high card points keyed on suit name."""
    suit_points = {suit: 0 for suit in SUITS}
    for card in cards:
        suit_points[card.suit.name] += card.high_card_points
    return suit_points


def get_seat(trick: Trick, player_index: int) -> str:
    """Return the seat of the player relative to the trick leader."""
    trick_index = SEATS.index(trick.leader)
    seat_index = (trick_index + player_index) % 4
    return SEATS[seat_index]


def highest_remaining_card(player: object, trick: Trick,
                           trumps: Suit = None) -> Card:
    """Return the highest card remaining in hand if
    player does not win trick."""

    # Ignore if 3rd player is winner:
    values = trick_card_values(trick, trumps)
    if values[2] == max(values):
        return None

    suit = trick.cards[0].suit
    winning_card = get_winning_card(trick, trumps)
    value = 2
    highest_card = None
    while value < 13 and value < winning_card.value:
        value += 1
        test_card = Card(CARD_VALUES[value], suit.name)
        unplayed_cards = player.opponents_unplayed_cards
        if test_card not in trick.cards + unplayed_cards[suit]:
            highest_card = test_card
    return highest_card


def get_winning_card(trick: Trick, trumps: Suit | None) -> Card:
    """Return the winning card in the trick."""
    card_values = trick_card_values(trick, trumps)
    for index, card in enumerate(trick.cards):
        if card_values[index] == max(card_values):
            return card
    raise ValueError(f'No winner in {trick.cards=} {trumps=}')


def trick_card_values(trick: Trick, trumps: Suit = None) -> list[int]:
    """Return a tuple of card values from a trick."""
    return card_values(trick.cards, trumps)


def card_values(cards: list[Card], trumps: Suit = None) -> list[int]:
    """Return a list of card values."""
    if len(cards) == 0:
        return [0, 0, 0, 0]

    values = []
    for index, card in enumerate(cards):
        value = _get_card_value(cards, index, trumps)
        values.append(value)
    return values


def _get_card_value(cards, index, trumps):
    """Return the trump modified value of a card."""
    card = cards[index]
    trick_suit = cards[0].suit
    value = cards[index].value
    if card.suit == trumps:
        return value + 13
    if card.suit != trick_suit:
        return 0
    return value


def play_to_unblock(hand_to_play: list[Card],
                    other_hand: list[Card]) -> Card | None:
    """Select the card to unblock the suit."""
    (long_hand, short_hand) = get_long_hand(hand_to_play, other_hand)
    if not short_hand:
        return long_hand[0]

    long_values, short_values = card_values(long_hand), card_values(short_hand)

    # Return  cards in a sequence from the short hand
    card_in_sequence = _card_in_sequence(hand_to_play, short_hand)
    if card_in_sequence:
        return card_in_sequence

    # All values in short hand are lower than corresponding one in long
    card = _all_low_in_short(hand_to_play, short_hand)
    if card:
        return card

    # The lowest card in the short hand is lower than
    # the highest card in the long hand
    if short_values[-1] < long_values[0]:
        if long_hand == hand_to_play:
            return long_hand[-1]
        return short_hand[0]

    # Default return None
    return None


def _card_in_sequence(hand_to_play: list[Card],
                      other_hand: list[Card]) -> Card | None:
    """Return top of short hand if it's in a sequence."""
    (long_hand, short_hand) = get_long_hand(hand_to_play, other_hand)
    long_values, short_values = card_values(long_hand), card_values(short_hand)
    values = sorted(long_values + short_values, reverse=True)
    sequence = _get_sequence(values)
    if len(sequence) > 1:
        suit = hand_to_play[0].suit.name
        for item in sequence:
            card = Card(CARD_VALUES[item], suit)
            if card in short_hand and short_hand == hand_to_play:
                return card
        return long_hand[-1]
    return None


def _all_low_in_short(hand_to_play: list[Card],
                      other_hand: list[Card]) -> Card | None:
    (long_hand, short_hand) = get_long_hand(hand_to_play, other_hand)
    long_values, short_values = card_values(long_hand), card_values(short_hand)

    result = True
    for index, value in enumerate(short_values):
        if value > long_values[index]:
            result = False
            break
    if result:
        return hand_to_play[0]
    return None


def _get_sequence(values):
    sequence = [values[0]]
    for index, item in enumerate(values[:-1]):
        if item == values[index + 1] + 1:
            sequence.append(values[index + 1])
        else:
            break
    return sequence


def get_long_hand(hand_1: list[Card], hand_2: list[Card]) -> tuple[list[Card]]:
    """Return a tuple of (long_hand, short_hand)."""
    long_hand, short_hand = hand_1, hand_2
    if len(hand_2) > len(hand_1):
        short_hand, long_hand = hand_1, hand_2
    return (long_hand, short_hand)


def play_lowest_winning_card(player, cards, trick):
    for card in cards[::-1]:
        if player.is_winner_declarer(card, trick):
            return card
