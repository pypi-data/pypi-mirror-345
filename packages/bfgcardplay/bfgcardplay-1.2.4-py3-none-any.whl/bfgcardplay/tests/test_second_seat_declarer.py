from bfgcardplay import next_card
from .utilities import get_boards


boards = get_boards('second_seat_declarer.pbn')


def test_play_partners_suit():
    """Do not play high card when inappropriate."""
    board = boards['0']
    assert next_card(board).name == '7H'


def test_do_not_signal_with_honour():
    """Do not signal with a losing honour."""
    board = boards['1']
    assert next_card(board).name != 'KS'

def test_do_play_high_in_second_seat():
    """Do play high in second seat in NT."""
    board = boards['2']
    assert next_card(board).name != 'KD'
