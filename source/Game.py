"""
This module implements the Board class for minesweeper implementation.
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
    -1: Mine
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
    0: GameLost (When user clicked cell is a mine)
    1: GameNotComplete
    2: GameWon (When user has marked all mines properly and opened all remaining cells)
    """
    Lost = 0
    InProgress = 1
    Won = 2

    def __init__(self):
        pass



class Board(object):
    """
    This is the core Board class as per the class diagram
    """
    def __init__(self, rows, columns, mineList):
        """
        This is the constructor.
        :param rows: Grid rows
        :param columns: Grid columns
        :param mineList: List of mines represented by row,column tuples
        :return: None
        """
        self.rows = rows
        self.columns = columns
        self.mineList = mineList

        self.gameStatus = GameStatus.InProgress

        self.createBoard()

    def createBoard(self):
        """
        Initialize the Board status and property with Closed and Empty resp.
        :return: None
        """
        self.cellStatus = [[CellStatus.Closed for col in range(self.columns)] \
            for row in range(self.rows)]
        self.cellProperty = [[CellProperty.Empty for col in range(self.columns)] \
            for row in range(self.rows)]


        for minePos in self.mineList:
            self.cellProperty[minePos[0]][minePos[1]] = CellProperty.Mine

        # Update Adjacent Count in neighbouring cells of a cell which has mines
        for minePos in self.mineList:
            row = minePos[0]
            column = minePos[1]
            if (row - 1 >= 0) and (column - 1 >= 0):
                if self.cellProperty[row - 1][column - 1] != CellProperty.Mine:
                    self.cellProperty[row - 1][column - 1] += 1
            if row - 1 >= 0:
                if self.cellProperty[row - 1][column] != CellProperty.Mine:
                    self.cellProperty[row - 1][column] += 1
            if (row - 1 >= 0) and (column + 1 < self.columns):
                if self.cellProperty[row - 1][column + 1] != CellProperty.Mine:
                    self.cellProperty[row - 1][column + 1] += 1
            if column + 1 < self.columns:
                if self.cellProperty[row][column + 1] != CellProperty.Mine:
                    self.cellProperty[row][column + 1] += 1
            if (row + 1 < self.rows) and (column + 1 < self.columns):
                if self.cellProperty[row + 1][column + 1] != CellProperty.Mine:
                    self.cellProperty[row + 1][column + 1] += 1
            if row + 1 < self.rows:
                if self.cellProperty[row + 1][column] != CellProperty.Mine:
                    self.cellProperty[row + 1][column] += 1
            if (row + 1 < self.rows) and (column - 1 >= 0):
                if self.cellProperty[row + 1][column - 1] != CellProperty.Mine:
                    self.cellProperty[row + 1][column - 1] += 1
            if column - 1 >= 0:
                if self.cellProperty[row][column - 1] != CellProperty.Mine:
                    self.cellProperty[row][column - 1] += 1
        return

    def openCell(self, row, column):
        """
        Open the input cell and return list of affected cells.
        :param row: Row of the cell
        :param column: Column of the cell
        :return: List of cells affected and to be updated
        """
        assert row >= 0 and row <= self.rows and column >= 0 and column <= self.columns

        cellList = []

        # if cell status is already opened or marked as mine or suspected mine,
        # ignore
        if (self.cellStatus[row][column] == CellStatus.Opened) or \
            (self.cellStatus[row][column] == CellStatus.MarkedAsMine) or \
            (self.cellStatus[row][column] == CellStatus.MarkedAsSuspectedMine):
            return cellList

        #set the Cell Status to Opened and add it to CellList to be returned
        self.cellStatus[row][column] = CellStatus.Opened
        cellList.append((row, column))

        if self.cellProperty[row][column] == CellProperty.Mine:
            self.gameStatus = GameStatus.Lost
            return cellList

        # if a cell is empty we should open all the 8 neighbours of the
        # clicked cell if they are not already open or marked as mine.
        # This rule applies recursively to neighbour cells if they are also
        # empty.
        if self.cellProperty[row][column] == CellProperty.Empty:
            if (row - 1 >= 0) and (column - 1 >= 0):
                cellList.extend(self.openCell(row - 1, column - 1))
            if row - 1 >= 0:
                cellList.extend(self.openCell(row - 1, column))
            if (row - 1 >= 0) and (column + 1 < self.columns):
                cellList.extend(self.openCell(row - 1, column + 1))
            if column + 1 < self.columns:
                cellList.extend(self.openCell(row, column + 1))
            if (row + 1 < self.rows) and (column + 1 < self.columns):
                cellList.extend(self.openCell(row + 1, column + 1))
            if column - 1 >= 0:
                cellList.extend(self.openCell(row, column - 1))
            if row + 1 < self.rows:
                cellList.extend(self.openCell(row + 1, column))
            if (row + 1 < self.rows) and (column - 1 >= 0):
                cellList.extend(self.openCell(row + 1, column - 1))

        # Check if opening of the cells resulted in a win for the player
        # if there are no cells that are closed or marked as suspected mine, then player wins
        self.gameStatus = GameStatus.Won
        for row in range(self.rows):
            for col in range(self.columns):
                if self.cellStatus[row][col] in (CellStatus.Closed, \
                    CellStatus.MarkedAsSuspectedMine):
                    self.gameStatus = GameStatus.InProgress
                    break

        return cellList

    def setCellStatus(self, row, column, newStatus):
        """
        This function sets the cell's status as per input argument.
        :param row: Row of the cell
        :param column: Column of the cell
        :param status: ::CellStatus enum value to be set
        :return: None
        """
        assert row >= 0 and row <= self.rows and column >= 0 and column <= self.columns

        # Only state transitions noted below are allowed.  Illegal state
        # transtion requests are ignored
        # MarkedAsMine -> MarkedAsSuspectedMine
        # MarkedAsSuspectedMine -> Closed
        # Closed -> [Opened, MarkedAsMine]

        if self.cellStatus[row][column] == CellStatus.MarkedAsMine:
            if newStatus == CellStatus.MarkedAsSuspectedMine:
                self.cellStatus[row][column] = CellStatus.MarkedAsSuspectedMine

        elif self.cellStatus[row][column] == CellStatus.MarkedAsSuspectedMine:
            if newStatus == CellStatus.Closed:
                self.cellStatus[row][column] = CellStatus.Closed

        elif self.cellStatus[row][column] == CellStatus.Closed:
            if newStatus == CellStatus.MarkedAsMine:
                self.cellStatus[row][column] = CellStatus.MarkedAsMine
            elif newStatus == CellStatus.Opened:
                self.cellStatus[row][column] = CellStatus.Opened


        # Check if changing the cell status resulted in a win for the player
        # if there are no cells that are closed or marked as suspected mine, then player wins
        self.gameStatus = GameStatus.Won
        for row in range(self.rows):
            for col in range(self.columns):
                if self.cellStatus[row][col] in (CellStatus.Closed, \
                    CellStatus.MarkedAsSuspectedMine):
                    self.gameStatus = GameStatus.InProgress
                    break

    def getCellStatus(self, row, column):
        """
        This function returns the cell's status.
        :param row: Row of the cell
        :param column: Column of the cell
        :return: ::CellStatus enum value
        """
        assert row >= 0 and row <= self.rows and column >= 0 and column <= self.columns
        return self.cellStatus[row][column]

    def getCellProperty(self, row, column):
        """
        This function returns the cell's property.
        :param row: Row of the cell
        :param column: Column of the cell
        :return: ::CellProperty enum value
        """
        assert row >= 0 and row <= self.rows and column >= 0 and column <= self.columns
        return self.cellProperty[row][column]

    def getGameStatus(self):
        """
        This function returns GameStatus enum value as per the current status.
        :return: GameWon, GameNotComplete or GameLost
        """
        return self.gameStatus
