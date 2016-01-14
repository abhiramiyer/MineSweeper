"""
Main implementation file for Minesweeper
"""
import sys
import functools
import os.path
import random

from PyQt4 import QtCore
from PyQt4 import QtGui

import Game
import LeaderBoard

class GameLevel(object):
    """
    Class for managing the game level and game parameters
    """
    Beginner = 1
    Intermediate = 2
    Expert = 3

    # Dict format is Level: (rows, columns, mines)
    GameParamDict = {Beginner: (9, 9, 10), Intermediate:(16, 16, 40), Expert:(16, 30, 99)}
    
    SettingsFile = "Minesweeper.ini"

    def __init__(self):
        self.currentLevel = GameLevel.Beginner

        if os.path.exists(GameLevel.SettingsFile):
            file = open(GameLevel.SettingsFile, "r")
            self.currentLevel = int(file.read())
            file.close()
        else:
            # If file doesn't exist, assume default level as beginner and start
            # game.
            file = open(GameLevel.SettingsFile, "w")
            file.write(str(self.currentLevel))
            file.close()

    def getGameLevel(self):
        """
        Returns the current difficulty level
        """
        return self.currentLevel

    def setGameLevel(self, level):
        """
        Sets the difficulty level
        """
        self.currentLevel = level
        file = open(GameLevel.SettingsFile, "w")
        file.write(str(level))
        file.close()

    def getGameParams(self, level=None):
        """
        Returns the game params for the level from the game params dictionary
        If level is not specified, then returns the parameters for current level
        """
        if level is None:
            return GameLevel.GameParamDict[self.currentLevel]
        else:
            return GameLevel.GameParamDict[level]


def GenerateMineList(rows, columns, minecount):
    """
    Returns a list of randomized row, column 2-tuples that represent location of the mine
    """
    selectedMineNumbers = random.sample(range(rows * columns), minecount)
    mineList = []
    for mineNumber in selectedMineNumbers:
        row = mineNumber // columns
        col = mineNumber % columns
        mineList.append((row, col))

    return mineList

class BoardWidget(QtGui.QWidget):
    """
    This class implements the cell UI. Each cell is referenced by [row][col]
    """

    def __init__(self, rows=10, columns=10, numMines=10, parent=None):
        super(BoardWidget, self).__init__(parent)
        self.rows = rows
        self.columns = columns
        self.numMines = numMines
        self.parent = parent
        self.remainingMineCount = self.numMines
        self.cellSize = 25
        self.buttonArray = [[QtGui.QPushButton() \
                         for col in range(self.columns)] for row in range(self.rows)]
        self.gameInProgress = True
        self.firstClick = True
        self.timer = QtCore.QTimer()
        self.time = 0

        self.cellGridLayout = QtGui.QGridLayout()


        for row in range(self.rows):
            for col in range(self.columns):
                self.buttonArray[row][col].setFixedSize(self.cellSize, self.cellSize)
                self.buttonArray[row][col].setIcon(QtGui.QIcon("icons/unopenedsquare.png"))
                self.buttonArray[row][col].setIconSize(QtCore.QSize(self.cellSize,\
                                                                     self.cellSize))
                leftClickLambda = lambda x=row, y=col: self.handleLeftClick(x, y)
                self.connect(self.buttonArray[row][col], QtCore.SIGNAL('clicked()'), \
                    leftClickLambda)

                # 'v' is for chomping the QPoint argument.
                rightClickLambda = lambda v, x=row, y=col: self.handleRightClick(x, y)
                self.buttonArray[row][col].setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
                self.connect(self.buttonArray[row][col], \
                    QtCore.SIGNAL('customContextMenuRequested(const QPoint&)'), rightClickLambda)

                self.cellGridLayout.addWidget(self.buttonArray[row][col], row, col)

        self.cellGridLayout.setSpacing(0)

        self.statusWidgetLayout = QtGui.QHBoxLayout()

        self.remainingMinesLCD = QtGui.QLCDNumber(3)
        self.remainingMinesLCD.setSegmentStyle(QtGui.QLCDNumber.Flat)
        self.remainingMinesLCD.setStyleSheet("background-color:black; color:red")
        self.remainingMinesLCD.display(str(self.remainingMineCount))
        self.statusWidgetLayout.addWidget(self.remainingMinesLCD)

        self.statusWidgetLayout.addStretch()

        self.statusButton = QtGui.QPushButton()
        self.statusButton.setFixedSize(50, 50)
        self.statusButton.setIcon(QtGui.QIcon("icons/smiley1.ico"))
        self.statusButton.setIconSize(self.statusButton.sizeHint())
        self.statusButton.clicked.connect(self.resetGrid)
        self.statusWidgetLayout.addWidget(self.statusButton)

        self.statusWidgetLayout.addStretch()

        self.timeLCD = QtGui.QLCDNumber(3)
        self.timeLCD.setSegmentStyle(QtGui.QLCDNumber.Flat)
        self.timeLCD.setStyleSheet("background-color:black; color:red")
        self.timeLCD.display(self.time)
        self.statusWidgetLayout.addWidget(self.timeLCD)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addLayout(self.statusWidgetLayout)
        mainLayout.addLayout(self.cellGridLayout)

        self.setLayout(mainLayout)

        self.connect(self.timer, QtCore.SIGNAL('timeout()'), self.timerHandler)

        self.mineList = GenerateMineList(self.rows, self.columns, self.numMines)
        self.board = Game.Board(self.rows, self.columns, self.mineList)

    def timerHandler(self):
        """
        This function updates the timer lcd
        :return: None
        """
        if self.time < 999:
            self.time += 1
            self.timeLCD.display(self.time)
        else:
            self.timer.stop()

    def resetGrid(self):
        """
        This function resets the grid for a fresh instance of game.
        :return: None
        """
        self.remainingMineCount = self.numMines
        self.gameInProgress = True
        self.firstClick = True
        self.timer.stop()

        for row in range(self.rows):
            for col in range(self.columns):
                self.buttonArray[row][col].setIcon(QtGui.QIcon("icons/unopenedsquare.png"))
                self.buttonArray[row][col].setIconSize(QtCore.QSize(self.cellSize,\
                                                                     self.cellSize))

        self.remainingMinesLCD.display(str(self.remainingMineCount))
        self.statusButton.setIcon(QtGui.QIcon("icons/smiley1.ico"))
        self.time = 0
        self.timeLCD.display(self.time)


        self.mineList = GenerateMineList(self.rows, self.columns, self.numMines)

        # Create a new board
        self.board = Game.Board(self.rows, self.columns, self.mineList)

    def handleLeftClick(self, row, col):
        """
        This function handles the left click action on each of the grid cell.
        It will also handle the actions required
        :return: None
        """
        if not self.gameInProgress:
            return

        if self.firstClick:
            self.firstClick = False
            self.timer.start(1000)

        celllist = self.board.openCell(row, col)

        if celllist == []:
            return

        for cell in celllist:
            row = cell[0]
            col = cell[1]
            cellProperty = self.board.getCellProperty(row, col)

            if cellProperty == Game.CellProperty.Empty:
                self.buttonArray[row][col].setIcon(QtGui.QIcon("icons/OpenedSquare.png"))
            elif cellProperty == Game.CellProperty.Mine:
                # Game over.  expose all mines
                for minePos in self.mineList:
                    row = minePos[0]
                    col = minePos[1]
                    self.buttonArray[row][col].setIcon(QtGui.QIcon("icons/mine.ico"))

                self.statusButton.setIcon(QtGui.QIcon("icons/smiley3.ico"))
                self.gameInProgress = False
                self.timer.stop()
                return
            elif cellProperty == Game.CellProperty.MineCountOne:
                self.buttonArray[row][col].setIcon(QtGui.QIcon("icons/1.png"))
            elif cellProperty == Game.CellProperty.MineCountTwo:
                self.buttonArray[row][col].setIcon(QtGui.QIcon("icons/2.png"))
            elif cellProperty == Game.CellProperty.MineCountThree:
                self.buttonArray[row][col].setIcon(QtGui.QIcon("icons/3.png"))
            elif cellProperty == Game.CellProperty.MineCountFour:
                self.buttonArray[row][col].setIcon(QtGui.QIcon("icons/4.png"))
            elif cellProperty == Game.CellProperty.MineCountFive:
                self.buttonArray[row][col].setIcon(QtGui.QIcon("icons/5.png"))
            elif cellProperty == Game.CellProperty.MineCountSix:
                self.buttonArray[row][col].setIcon(QtGui.QIcon("icons/6.png"))
            elif cellProperty == Game.CellProperty.MineCountSeven:
                self.buttonArray[row][col].setIcon(QtGui.QIcon("icons/7.png"))
            elif cellProperty == Game.CellProperty.MineCountEight:
                self.buttonArray[row][col].setIcon(QtGui.QIcon("icons/8.png"))

        gameStatus = self.board.getGameStatus()

        if gameStatus == Game.GameStatus.Won:
            self.timer.stop()
            self.gameInProgress = False
            self.statusButton.setIcon(QtGui.QIcon("icons/smiley.ico"))

            self.parent.postUserWinCallback(self.time)

    def handleRightClick(self, row, col):
        """
        This function handles the right click action on grid cell.
        :return: None
        """
        if not self.gameInProgress:
            return
        if self.firstClick:
            self.firstClick = False
            self.timer.start(1000)

        status = self.board.getCellStatus(row, col)
        if status == Game.CellStatus.Opened:
            return
        elif status == Game.CellStatus.Closed:
            self.remainingMineCount = self.remainingMineCount - 1
            self.remainingMinesLCD.display(str(self.remainingMineCount))
            self.board.setCellStatus(row, col, Game.CellStatus.MarkedAsMine)
            self.buttonArray[row][col].setIcon(QtGui.QIcon("icons/Flag.png"))
        elif status == Game.CellStatus.MarkedAsMine:
            self.remainingMineCount = self.remainingMineCount + 1
            self.remainingMinesLCD.display(str(self.remainingMineCount))
            self.board.setCellStatus(row, col, Game.CellStatus.MarkedAsSuspectedMine)
            self.buttonArray[row][col].setIcon(QtGui.QIcon("icons/questionmark.png"))
        elif status == Game.CellStatus.MarkedAsSuspectedMine:
            self.board.setCellStatus(row, col, Game.CellStatus.Closed)
            self.buttonArray[row][col].setIcon(QtGui.QIcon("icons/unopenedsquare.png"))

        gameStatus = self.board.getGameStatus()

        if gameStatus == Game.GameStatus.Won:
            self.timer.stop()
            self.gameInProgress = False
            self.statusButton.setIcon(QtGui.QIcon("icons/smiley.ico"))

            self.parent.postUserWinCallback(self.time)

class MainWindow(QtGui.QMainWindow):
    """
    This class defines the Main Window class for the game.
    This is responsible for menus, game board, status bars.
    """

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.gameLevel = GameLevel()
        self.leaderBoard = LeaderBoard.LeaderBoard()

        (rows, columns, minecount) = self.gameLevel.getGameParams()

        mainWidget = BoardWidget(rows, columns, minecount, self)

        # prevent resize of main window
        self.setFixedSize(self.sizeHint())

        # move the window to a good position
        self.move(250, 100)

        # prevent reaction to maximize button
        self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)

        # Add menu bar
        self.addMenuBar()

        statusBar = self.statusBar()
        statusBar.showMessage("Ready")

        # remove resizing grip from the main window
        statusBar.setSizeGripEnabled(False)

        self.setCentralWidget(mainWidget)
        self.setWindowTitle("Minesweeper")
        self.setWindowIcon(QtGui.QIcon("icons/mine.ico"))
        self.show()

    def postUserWinCallback(self, time):
        """
        This function is called when the human player wins the game and a new high score is hit
        """
        level = self.gameLevel.getGameLevel()
        if self.leaderBoard.newTopScore(level, time):
            playerName, ok = QtGui.QInputDialog.getText(self, "Name Please !!",\
                                                             "Enter your name for leader board:")
            if ok:
                self.leaderBoard.insertNewScore(level, playerName, time)

    def about(self):
        """
        This function displays information about game.
        This function just displays game version and basic info about game.
        :return: VOID
        """
        QtGui.QMessageBox.about(self, "About Menu",
                                "MineSweeper 1.0 \n"
                                "This is a PyQt4 implementation of famous Minesweeper Game \n\n"
                               )

    def showHelp(self):
        """
        This function displays help about game
        This function will pop up message box to user
        It will display following contents:
        1. how to play game
        2. Hints and tips
        :return: VOID
        """
        QtGui.QMessageBox.about(self, "How to Play game",
                                "<b>How to Play</b><br>"
                                "The rules in Minesweeper are simple:<br><br>"
                                "<b>1.</b> Uncover a mine and that's end of game <br>"
                                "<b>2.</b> Uncover empty cell and "
                                "it opens surrounding empty cells too<br>"
                                "<b>3.</b> Uncover a number "
                                "and it tells you how many mines are hidden in"
                                "surrounding 8 cells.<br>"
                                "<b>4.</b> Use this information to "
                                "deduce which squares are safe to click.<br>"
                                "<b>5.</b> Uncover all cells and "
                                "mark cells with mine to win the game <br><br>"

                                "<b>Hints</b> <br>"
                                "<b>1.Mark as Mine </b> <br>"
                                "   If you suspect that cell as mine, "
                                "right click twice to put a question mark.<br>"
                                "<b>2.Study surrounding cells </b><br>"
                                "  Study all neighbour cells before opening any cell"
                                "to make sure whether its mine or not.<br><br>"
                                "Enjoy the game :) <br>")

    def showTopScores(self):
        """
        This function handles the event of user asking for leaderboard.
        :return: None
        """

        TopScoresDialog(self)


    def addMenuBar(self):
        """
            This function will add menu bar to the GUI.
            First we'll define all the actions which are required inside menu.
            Then we'll create menu bar and add menu's and actions.
        """
        # File menu option to change difficulty level
        beginnerLevelAction = QtGui.QAction(QtGui.QIcon(""), '&Beginner', self)
        beginnerLevelAction.setShortcut('Ctrl+B')
        beginnerLevelAction.setStatusTip('Set difficulty level to "Beginner" ')
        beginnerLevelAction.triggered.connect(functools.partial(self.changeGameLevel,\
                                                GameLevel.Beginner))

        # File menu option to change difficulty level
        intermediateLevelAction = QtGui.QAction(QtGui.QIcon(""), '&Intermediate', self)
        intermediateLevelAction.setShortcut('Ctrl+I')
        intermediateLevelAction.setStatusTip('Set difficulty level to "Intermediate" ')
        intermediateLevelAction.triggered.connect(functools.partial(self.changeGameLevel,\
                                                    GameLevel.Intermediate))

        # File menu option to change difficulty level
        expertLevelAction = QtGui.QAction(QtGui.QIcon(""), '&Expert', self)
        expertLevelAction.setShortcut('Ctrl+E')
        expertLevelAction.setStatusTip('Set difficulty level to "Expert" ')
        expertLevelAction.triggered.connect(functools.partial(self.changeGameLevel,\
                                                GameLevel.Expert))

        # File menu option "About" which gives information about game
        aboutGameAction = QtGui.QAction(QtGui.QIcon(""), '&About', self)
        aboutGameAction.setShortcut('Ctrl+A')
        aboutGameAction.setStatusTip("Show Application's ABOUT box")
        aboutGameAction.triggered.connect(self.about)

        # File menu option "About" which gives information about game
        gameHelpAction = QtGui.QAction(QtGui.QIcon(""), '&Help', self)
        gameHelpAction.setShortcut('Ctrl+H')
        gameHelpAction.setStatusTip("Show game's help")
        gameHelpAction.triggered.connect(self.showHelp)

        # File Menu option to view the score.
        viewLeaderboardAction = QtGui.QAction(QtGui.QIcon(""), '&View Score', self)
        viewLeaderboardAction.setShortcut('Ctrl+V')
        viewLeaderboardAction.setStatusTip("View current game's leader board")
        viewLeaderboardAction.triggered.connect(self.showTopScores)

        # File Menu option for exit the game.
        exitGameAction = QtGui.QAction(QtGui.QIcon("exit.png"), '&Exit', self)
        exitGameAction.setShortcut('Ctrl+Q')
        exitGameAction.setStatusTip('Exit application')
        exitGameAction.triggered.connect(QtGui.QApplication.quit)

        # create a menu bar and we need to add 2 menus
        # 1.  File and 2.  Help
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        helpMenu = menubar.addMenu('&Help')

        # Inside File menu create a submenu to change gane level
        # This sub menu has 3 actions (3 levels to choose from)
        changeLevelSubMenu = fileMenu.addMenu('&Game Level')
        changeLevelSubMenu.addAction(beginnerLevelAction)
        changeLevelSubMenu.addAction(intermediateLevelAction)
        changeLevelSubMenu.addAction(expertLevelAction)

        # Add other actions in file menu after game level.
        fileMenu.addAction(viewLeaderboardAction)

        # Add seperator (visible line) before showing exit.
        fileMenu.addSeparator().setText("Alignment")
        fileMenu.addAction(exitGameAction)

        # Add actions (sub menus) for help menu.
        helpMenu.addAction(aboutGameAction)
        helpMenu.addAction(gameHelpAction)

    def changeGameLevel(self, changeLevel):
        """
            This function helps in changing game level
            When user clicks on change game level from File menu
            this function will start a new game at the new level
        """
        if self.gameLevel.getGameLevel() != changeLevel:
            self.gameLevel.setGameLevel(changeLevel)
            self.close()
            self.__init__()


class TopScoresDialog(QtGui.QDialog):
    """
    Class that displays the top scores
    """

    def __init__(self, parent=None):
        super(TopScoresDialog, self).__init__(parent)

        self.parent = parent

        self.setWindowTitle("Top Scores")
        self.textEdit = QtGui.QTextEdit(self)
        self.textEdit.setReadOnly(True)

        scoreList = self.parent.leaderBoard.getTopScoresList(self.parent.gameLevel.getGameLevel())

        htmlStr = "<table border=\"1\" cellpadding=4 width=\"100%\">"
        htmlStr += "<tr><th>Name</th> <th>Time(secs)</th></tr>"
        for entry in scoreList:
            htmlStr += "<tr>"
            htmlStr += "<td align=center>" + entry[1] + "</td>" + "<td align=center>" + \
                str(entry[0]) + "</td>"
            htmlStr += "</tr>"
        htmlStr += "</table>"

        self.textEdit.setHtml(htmlStr)

        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.textEdit)
        self.setLayout(self.layout)
        self.setMinimumSize(300, 350)
        self.show()

def main():
    """
    This is the main function.
    :return: None
    """
    app = QtGui.QApplication(sys.argv)

    MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
