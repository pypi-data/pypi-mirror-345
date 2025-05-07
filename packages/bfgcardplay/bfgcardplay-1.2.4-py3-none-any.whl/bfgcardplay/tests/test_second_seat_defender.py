from bfgcardplay import next_card
from .utilities import get_boards


boards = get_boards('second_seat_defender.pbn')


def test_play_partners_suit():
    """Do not play high card when inappropriate."""
    board = boards['0']
    assert next_card(board).name != 'KH'


def test_play_discard():
    board = boards['1']
    assert next_card(board).name != 'KC'
    assert next_card(board).name != '9D'
