from .. import next_card
from ..tests.utilities import get_boards
from bridgeobjects import Suit



boards = get_boards('third_seat_defender.pbn')


def test_play_partners_suit():
    """Return win if possible in _select_card_based_on_position."""
    board = boards['0']
    assert next_card(board).name == 'AH'


def test_play_high_card():
    """Return highest card in _play_high_card."""
    board = boards['1']
    assert next_card(board).name == 'TS'


def test_dont_play_high_card_if_partner_played_higher():
    """Do Not return highest card in _play_high_card."""
    board = boards['2']
    assert next_card(board).name != 'KS'


def test_dont_play_high_card_if_partner_played_winner():
    board = boards['4']
    assert next_card(board).name != 'AC'


def test_all_winners_in_long_suit():
    # Play winner if all winners
    board = boards['3']
    assert next_card(board).name == 'KH'


def test_lead_unblock():
    # Play winner if all winners
    board = boards['5']
    assert next_card(board).name == '9C'


def test_do_not_play_low_trump():
    board = boards['6']
    assert next_card(board).suit != Suit('S')
