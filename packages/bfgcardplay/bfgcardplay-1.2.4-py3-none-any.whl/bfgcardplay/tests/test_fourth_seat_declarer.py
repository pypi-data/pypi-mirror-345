from bfgcardplay import next_card
from .utilities import get_boards


boards = get_boards('fourth_seat_declarer.pbn')


def test_play_partners_suit():
    """Ensure not a S in _select_card_if_void, entry to partner's hand
        for suit in SUITS:."""
    board = boards['0']
    assert next_card(board).suit.name != 'S'


def test_play_partners_suit_2():
    """Ensure not a S in _select_card_if_void, entry to partner's hand
        for suit in SUITS:."""
    board = boards['1']
    assert next_card(board).name != 'KH'
