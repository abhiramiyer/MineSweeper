"""
This file defines the various enums which will be shared by different modules.
"""

class CellStatus(object):
    """
    CellState -
    0: Closed
    1: Opened
    2: Marked as mine
    3: Marked as suspected mine
    """
    Closed = 0
    Opened = 1
    MarkedAsMine = 2
    MarkedAsSuspectedMine = 3

    def __init__(self):
        pass

class CellProperty(object):
    """
    CellProperty -
    1: Mine
    0: Empty
    1-8: AdjacentMineCount
    """
    Mine = -1
    Empty = 0
    MineCountOne = 1
    MineCountTwo = 2
    MineCountThree = 3
    MineCountFour = 4
    MineCountFive = 5
    MineCountSix = 6
    MineCountSeven = 7
    MineCountEight = 8

    def __init__(self):
        pass

class GameStatus(object):
    """
    GameStatus -
    0: GameLost (When User clicked cell is a Min)
    1: GameInProgress
    2: GameWon (When User has Marked all mines properly and opened all remaining cells)
    """
    GameLost = 0
    GameInProgress = 1
    GameWon = 2

    def __init__(self):
        pass