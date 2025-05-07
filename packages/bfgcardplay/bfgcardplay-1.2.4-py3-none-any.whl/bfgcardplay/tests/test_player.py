from bfgcardplay.player import Player
from .utilities import get_boards
from bridgeobjects import Card


boards = get_boards('player.pbn')


def test_controls():
    board = boards['0']
    player = Player(board)
    assert player.controls == {'C': 0, 'D': 1, 'H': 2, 'S': 3}

def test_second_round_controls():
    board = boards['0']
    player = Player(board)
    assert player.second_round_controls == {'C': True, 'D': True, 'H': True, 'S': True}


def test_record_voids():
    board = boards['1']
    assert len(board.tricks) == 8
    player = Player(board)
    voids = player.voids
    assert voids['W']['S'] == False
    assert voids['W']['H'] == True
    assert voids['W']['D'] == True
    assert voids['W']['C'] == False

    assert voids['N']['S'] == False
    assert voids['N']['H'] == False
    assert voids['N']['D'] == False
    assert voids['W']['C'] == False

    assert voids['E']['S'] == False  # E is now void in S but at this stage has always followed suit

def test_short_seat():
    board = boards['2']
    player = Player(board)
    assert player.short_suit_seat == 'N'

    board = boards['3']
    player = Player(board)
    assert player.short_suit_seat == None

def test_short_hand():
    board = boards['2']
    player = Player(board)
    assert player.short_hand == board.hands['N']

    board = boards['3']
    player = Player(board)
    assert player.short_hand == None

def test_trump_cards():
    board = boards['2']
    player = Player(board)
    assert player.trump_cards == [Card("KC"), Card("TC"), Card("8C"), Card("7C")]
    assert player.opponents_trumps == [Card("AC"), Card("JC"), Card("9C"), Card("5C")]

def test_dummy_location():
    board = boards['3']
    player = Player(board)
    assert player.dummy_on_left == False
    assert player.dummy_on_right == False

    board = boards['4']
    player = Player(board)
    assert player.dummy_on_left == False
    assert player.dummy_on_right == True
