from bridgeobjects import Trick, Card, Suit, parse_pbn, Board

from bfgcardplay.player import Player

from bfgcardplay.utilities import (get_seat, get_suit_strength, trick_card_values, get_winning_card,
                                other_suit_for_signals, get_list_of_best_scores,
                                highest_remaining_card, play_to_unblock, get_long_hand)


def test_get_seat():
    trick = Trick()
    trick.leader = 'W'
    seat = get_seat(trick, 3)
    assert seat == 'S'

    trick.leader = 'N'
    seat = get_seat(trick, 2)
    assert seat == 'S'


def test_get_suit_strength():
    cards = [Card('AS'), Card('JS'), Card('TS'), Card('QC'), Card('KD')]
    suit_strength = get_suit_strength(cards)
    assert suit_strength['S'] == 5
    assert suit_strength['H'] == 0
    assert suit_strength['D'] == 3
    assert suit_strength['C'] == 2


def test_other_suit_for_signals():
    assert other_suit_for_signals(Suit('S')) == 'C'
    assert other_suit_for_signals(Suit('H')) == 'D'
    assert other_suit_for_signals(Suit('D')) == 'H'
    assert other_suit_for_signals(Suit('C')) == 'S'


def test_get_list_of_best_scores_distinct():
    candidates = {Suit("C"): 8, Suit("D"): 6, Suit("H"): 5, Suit("S"): 7}
    best_candidates = get_list_of_best_scores(candidates)
    assert best_candidates == [Suit("C")]

    best_candidates = get_list_of_best_scores(candidates, True)
    assert best_candidates == [Suit("H")]


def test_get_list_of_best_scores_duplicate():
    candidates = {Suit("C"): 8, Suit("D"): 6, Suit("H"): 6, Suit("S"): 7}
    best_candidates = get_list_of_best_scores(candidates, True)
    assert Suit('H') in best_candidates
    assert Suit('D') in best_candidates
    assert Suit('S') not in best_candidates


def test_trick_card_values_empty():
    trick = Trick()
    values = trick_card_values(trick)
    assert values == [0, 0, 0, 0]


def test_trick_card_values_one():
    trick = Trick()
    trick.cards = [Card('3S')]
    values = trick_card_values(trick)
    assert values == [2]


def test_trick_card_values_two():
    trick = Trick()
    trick.cards = [Card('3S'), Card('4S')]
    values = trick_card_values(trick)
    assert values == [2, 3]


def test_trick_card_values_triple():
    trick = Trick()
    trick.cards = [Card('3S'), Card('4S'), Card('KS')]
    values = trick_card_values(trick)
    assert values == [2, 3, 12]


def test_trick_card_values_discard_no_trumps():
    trick = Trick()
    trick.cards = [Card('3S'), Card('4C'), Card('KS')]
    values = trick_card_values(trick)
    assert values == [2, 0, 12]


def test_trick_card_values_trumps():
    trick = Trick()
    trick.cards = [Card('3S'), Card('4S'), Card('KS'), Card('2S')]
    values = trick_card_values(trick, Suit('S'))
    assert values == [15, 16, 25, 14]


def test_trick_card_values_discard_trumps():
    trick = Trick()
    # Discard in trumps
    trick.cards = [Card('3S'), Card('4C'), Card('2D'), Card('KS')]
    values = trick_card_values(trick, Suit('C'))
    assert values == [2, 16, 0, 12]


def test_trick_card_values_discard_trumps_two():
    trick = Trick()
    trick.cards = [Card('3S'), Card('4C'), Card('KS'), Card('2D')]
    values = trick_card_values(trick, Suit('C'))
    assert values == [2, 16, 12, 0]


def test_get_winning_card_discard():
    trick = Trick()

    trick.cards = [Card('3S'), Card('4C'), Card('KS')]
    card = get_winning_card(trick, None)
    assert card == Card('KS')


def test_get_winning_card_trump():
    trick = Trick()

    trick.cards = [Card('3S'), Card('4C'), Card('KS')]
    card = get_winning_card(trick, Suit('C'))
    assert card == Card('4C')


def _generate_board(board_pbn: list) -> Board:
    board = parse_pbn(board_pbn)[0].boards[0]
    for seat, hand in board.hands.items():
        hand.unplayed_cards = [card for card in hand.cards]
    return board


def _generate_trick(leader: str, cards: list[Card]) -> Trick:
    trick = Trick()
    trick.leader = leader
    trick.cards = cards
    return trick


def test_highest_remaining_card():
    board_pbn = [
        '[Board "0"]',
        '[Description "20 Jun 2023 17:01:12"]',
        '[Dealer "S"]',
        '[Vulnerable "None"]',
        '[Deal "S:AJ2.AQJ7.AT6.QJ9 T6.2.KJ832.K853 Q743.8.Q7.AT764 K985.KT96543..2"]',
        '[Declarer S]',
        '[Contract 3NT]',
        '[Auction "S"]', '3NT Pass Pass Pass',
        '[Play "W"]'
    ]
    board = _generate_board(board_pbn)

    trick = _generate_trick('E', [Card('4D'), Card('5D'), Card('9D'), Card('TD')])
    board.tricks.append(trick)
    player = Player(board)
    card = highest_remaining_card(player, trick)
    assert card == Card('8D')


# When unblocking you need to test leading from both long and short hands

def test_play_to_unblock_high_in_short_from_long():
    hand_to_play = [Card('JS'), Card('3S'), Card('2S')]
    other_hand = [Card('KS'), Card('4S')]
    card = play_to_unblock(hand_to_play, other_hand)
    assert card == Card('2S')

def test_play_to_unblock_high_in_short_from_short():
    hand_to_play = [Card('KS'), Card('4S')]
    other_hand = [Card('JS'), Card('3S'), Card('2S')]
    card = play_to_unblock(hand_to_play, other_hand)
    assert card == Card('KS')


def test_play_to_unblock_singleton_in_short_from_long():
    hand_to_play = [Card("JD"), Card("8D"), Card("4D")]
    other_hand = [Card('7D')]
    card = play_to_unblock(hand_to_play, other_hand)
    assert card == Card('JD')


def test_play_to_unblock_singleton_in_short_from_short():
    hand_to_play = [Card('7D')]
    other_hand = [Card("JD"), Card("8D"), Card("4D")]
    card = play_to_unblock(hand_to_play, other_hand)
    assert card == Card('7D')


def test_play_to_unblock_void_in_short():
    hand_to_play = []
    other_hand = [Card("JD"), Card("8D"), Card("4D")]
    card = play_to_unblock(hand_to_play, other_hand)
    assert card == Card('JD')


def test_play_to_unblock_three_honours_from_long():
    hand_to_play = [Card("AD"), Card("KD"), Card("7D")]
    other_hand = [Card("QD"), Card("9D")]
    card = play_to_unblock(hand_to_play, other_hand)
    assert card == Card('7D')


def test_play_to_unblock_three_honours_from_short():
    hand_to_play = [Card("QD"), Card("9D")]
    other_hand = [Card("AD"), Card("KD"), Card("7D")]
    card = play_to_unblock(hand_to_play, other_hand)
    assert card == Card('QD')


def test_get_log_hand():
    hand_to_play = [Card('KS'), Card('4S')]
    other_hand = [Card('JS'), Card('3S'), Card('2S')]
    (long_hand, short_hand) = get_long_hand(hand_to_play, other_hand)
    assert Card('JS') in long_hand
    assert Card('4S') in short_hand
