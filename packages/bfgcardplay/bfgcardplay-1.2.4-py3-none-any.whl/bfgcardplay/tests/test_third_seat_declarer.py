from bfgcardplay import next_card
from .utilities import get_boards


boards = get_boards('third_seat_declarer.pbn')


def test_play_partners_suit():
    "Do not play QC on AC."""
    board = boards['0']
    assert next_card(board).name == '5C'


def test_play_a_heart_when_all_winners():
    board = boards['1']
    assert next_card(board).suit.name != 'H'


def test_detect_void_in_fourth_hand():
    board = boards['2']
    assert next_card(board).name == 'TD'
