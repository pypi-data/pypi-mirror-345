from pathlib import Path
from bridgeobjects import load_pbn


TEST_PATH = Path('tests', 'test_data')


def get_boards(file_name: str) -> dict[str, object]:
    event_number = 0
    board_path = Path(TEST_PATH, file_name)
    raw_boards = load_pbn(board_path)[event_number].boards
    boards = {}
    for board in raw_boards:
        boards[board.identifier] = board
        played_cards = []
        for trick in board.tricks:
            played_cards += trick.cards
        for hand in board.hands.values():
            hand.unplayed_cards = [card for card in hand.cards if card not in played_cards]
    return boards
