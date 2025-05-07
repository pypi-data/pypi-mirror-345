""" Bid for Game
    test hands module
"""

import os
from pathlib import Path
import json
from termcolor import cprint

from bfgdealer import Board
from ..hand import Hand


HAND_PATH = Path('tests', 'test_data', 'test_hands.json')


def _get_boards():
    """Return a list of boards from the path."""
    assert os.path.isfile(HAND_PATH), f'Path is not a file {HAND_PATH}'
    with open(HAND_PATH) as f_json:
        boards = json.load(f_json)
    return boards


def _get_suggested_call(board):
    """Check a bid and return True if correct."""
    player = board.players['N']
    player.hand = board.hands['N']
    suggested_bid = player.make_bid()
    return suggested_bid


def test_bid_and_xref_correct():
    """Test that the correct bid is made."""
    boards = _get_boards()
    print(f'\n\nProcessing {len(boards)} boards')
    failed = []
    failed_text = '{}, correct call={}, suggested call={}, xref check={}, correct call id={}'
    for id, spec in boards.items():
        board = Board()
        board.description = id
        board.bid_history = spec['bids'][:-1]
        board.dealer = spec['dealer']
        cards = spec['hand']
        board.hands[0] = Hand(cards)
        board.hands['N'] = Hand(cards)

        suggested_bid = _get_suggested_call(board)
        check_xref = suggested_bid.call_id != spec['call_id']
        if suggested_bid.name != board.bid_history[-1] or not check_xref:
            failed.append(failed_text.format(board.description,
                                             board.bid_history[-1],
                                             suggested_bid.name,
                                             check_xref,
                                             suggested_bid.call_id,
                                             ))
    print('')
    if failed:
        for item in failed:
            cprint(item, 'red')
    else:
        cprint('All tests passed ...', 'green')
    print('')
