""" Generate and play random boards until it breaks."""
import sys
import logging
from io import StringIO

from bridgeobjects import Card, Trick, SEATS
from bfgdealer import Dealer, Board

from bfgcardplay import next_card

import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify

MODULE_COLOUR = 'blue'
MAX_HANDS = 10**6


def main():
    try:
        _generate_boards()
    except:
        log_stream = StringIO()
        logging.basicConfig(stream=log_stream, level=logging.ERROR)
        logging.error("Exception occurred", exc_info=True)
        print('x'*100)
        print(log_stream.getvalue())
        print('x'*100)

        Notify.init("Card play blitz")
        Notify.Notification.new('Error occurred').show()


def _generate_boards():
    logging.disable(logging.CRITICAL)
    count = 0
    while count < MAX_HANDS:
        board = Dealer().deal_random_board()
        board.auction = board.get_auction()
        board.contract = board.get_contract()
        if not board.contract.name:
            continue

        display_board(count)

        for _ in range(52):
            card = next_card(board)
            update_board_after_cardplay(board, card)
        # halt()

        count += 1


def display_board(count):
    if count % 10 == 0:
        print('.', end='', flush=True)
    if count and count % 1000 == 0:
        print(count)
        print('.', end='', flush=True)
        Notify.init('Card play blitz')
        Notify.Notification.new(f'{count} boards processed').show()


def update_board_after_cardplay(board: Board, card: Card) -> Board:
    trick = board.tricks[-1]
    current_player = get_current_player(trick)
    if card and card in board.hands[current_player].unplayed_cards:
        add_card_to_trick(board, trick, card)
        board.hands[current_player].unplayed_cards.remove(card)
    return board


def add_card_to_trick(board, trick, card):
    if card in trick.cards:
        return
    trick.cards.append(card)
    if len(trick.cards) == 4:
        complete_trick(board, trick)


def complete_trick(board: Board, trick: Trick) -> str:
    """complete the trick update the board and return trick winner."""
    trick.complete(board.contract.denomination)
    winner = trick.winner
    trick = Trick(leader=winner)
    board.tricks.append(trick)
    return winner


def get_current_player(trick: Trick) -> str:
    """Return the current player from the trick."""
    if len(trick.cards) == 4:
        return trick.winner
    leader_index = SEATS.index(trick.leader)
    current_player = (leader_index + len(trick.cards)) % 4
    return SEATS[current_player]


def halt():
    result = input('-->')
    if result in ['Q', 'q']:
        sys.exit()


if __name__ == '__main__':
    main()
