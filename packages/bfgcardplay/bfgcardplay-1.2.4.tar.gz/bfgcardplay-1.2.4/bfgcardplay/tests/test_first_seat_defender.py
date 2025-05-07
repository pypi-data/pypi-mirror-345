from  bfgcardplay import next_card
from .utilities import get_boards


boards = get_boards('first_seat_defender.pbn')


def test_play_partners_suit():
    """Return partner's suit in _select_suit_for_nt_contract."""
    board = boards['0']
    assert next_card(board).name == '8H'


def test_play_winners():
    """Play winners in _select_card_from_suit."""
    board = boards['1']
    assert next_card(board).name == 'JH'


def test_play_winners_not_in_hand():
    """Play winners in _select_card_from_suit."""
    board = boards['2']
    assert next_card(board).name == '4D'


def test_play_winners_in_hand():
    board = boards['3']
    assert next_card(board).name == 'AS'
