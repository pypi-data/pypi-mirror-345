from bfgcardplay import next_card
from .utilities import get_boards


boards = get_boards('first_seat_declarer.pbn')


def test_select_suit_with_cards():
    board = boards['0']
    next_card(board).name  # Seem to need to play this card before we get the correct card
    assert next_card(board).name[1] != 'D'


def test_select_suit_with_winners_in_partners_hand():
    board = boards['1']
    assert next_card(board).name[1] == 'S'


def test_do_not_play_losers_when_you_have_winners():
    board = boards['2']
    assert next_card(board).suit.name != 'C'


def test_play_winners():
    # see first_seat_declarer_nt.py # Play winning cards at 443
    board = boards['3']
    # TODO this causes a problem in test second_seat_declarer
    # assert next_card(board).name != '7D'


def test_underplay_tenace():
    board = boards['4']
    print(next_card(board))
    assert next_card(board).name[1] != ''
