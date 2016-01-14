"""
This module defines the API related to leaderboard handling.
"""

import os
import sys
import pickle
import Minesweeper

class LeaderBoard(object):
    """
    Class for managing the scores

    The scores are stored as follows:
    1.For each level there is a list of (score, playerName) tuples sorted high to low on score
    2.The high score lists are stored in a dictionary accessible using the level as the key
    3.The dictionary is pickled

    """

    def __init__(self, pickleFile="HighScores.db"):
        self.pickleFile = pickleFile
        if os.path.exists(self.pickleFile):
            file = open(self.pickleFile, "rb+")
            self.scores = pickle.load(file)
            file.close()
        else:
            self.scores = {Minesweeper.GameLevel.Beginner: [], \
                Minesweeper.GameLevel.Intermediate: [], \
                Minesweeper.GameLevel.Expert: [] \
                }

    def newTopScore(self, level, playerScore):
        """
        This method checks if the score is a new high score

        :param Level: Beginner/Intermediate/Expert
        :param score: Score in seconds for the player
        :return: True or False

        """
        scores = self.scores[level]

        # There are 10 slots for high scores.  A score can get in provided
        # there are empty slots.
        # If there are no slots empty, then a score can get in only if it is
        # bigger than the lowest
        # of the top 10 scores

        if len(scores) < 10:
            return True
        elif playerScore < scores[9][0]:
            return True
        else:
            return False


    def insertNewScore(self, level, playerName, playerScore):
        """
        This function will store score (along with other details such as rank and name) in a file,
        corresponding to selected game level in descending order of scores

        :param Level: Beginner/Intermediate/Expert
        :param player_name: Player name
        :param score: Score in seconds for the player
        :return: None
        """
        scores = self.scores[level]
        scores.append((playerScore, playerName))
        scores.sort(key=lambda x: x[0])

        if len(scores) > 10:
            scores = scores[:10]

        self.scores[level] = scores

        file = open(self.pickleFile, "wb+")
        pickle.dump(self.scores, file)
        file.close()


    def getTopScoresList(self, level):
        """
        This function will retrieve scores for selected game level
        :param level: Level of game (Beginner, Intermediate, Expert) for which score is required
        :return: The list of top scores for input level
        """

        return self.scores[level]

def main():
    """
    Runs tests for this module
    """
    os.remove("Test1.db")

    testLdrBoard = LeaderBoard("Test1.db")


    assert testLdrBoard.newTopScore(Minesweeper.GameLevel.Beginner, 1) is True
    testLdrBoard.insertNewScore(Minesweeper.GameLevel.Beginner, "A", 1)
    assert testLdrBoard.getTopScoresList(Minesweeper.GameLevel.Beginner) == [(1, "A")]

    assert testLdrBoard.newTopScore(Minesweeper.GameLevel.Beginner, 1) is True
    testLdrBoard.insertNewScore(Minesweeper.GameLevel.Beginner, "B", 1)

    assert testLdrBoard.getTopScoresList(Minesweeper.GameLevel.Beginner) == [(1, "A"), (1, "B")]

    testLdrBoard.insertNewScore(Minesweeper.GameLevel.Beginner, "C", 2)
    assert testLdrBoard.getTopScoresList(Minesweeper.GameLevel.Beginner) == [(1, "A"), (1, "B"), \
        (2, "C")]

    testLdrBoard.insertNewScore(Minesweeper.GameLevel.Beginner, "D", 1)
    assert testLdrBoard.getTopScoresList(Minesweeper.GameLevel.Beginner) == [(1, "A"), (1, "B"), \
        (1, "D"), (2, "C")]

    testLdrBoard.insertNewScore(Minesweeper.GameLevel.Beginner, "E", 2)
    assert testLdrBoard.getTopScoresList(Minesweeper.GameLevel.Beginner) == [(1, "A"), (1, "B"), \
        (1, "D"), (2, "C"), (2, "E")]

    testLdrBoard.insertNewScore(Minesweeper.GameLevel.Beginner, "F", 3)
    assert testLdrBoard.getTopScoresList(Minesweeper.GameLevel.Beginner) == [(1, "A"), (1, "B"), \
        (1, "D"), (2, "C"), (2, "E"), (3, "F")]


    for k in range(4):
        testLdrBoard.insertNewScore(Minesweeper.GameLevel.Beginner, "g", 3 + k)
    assert testLdrBoard.getTopScoresList(Minesweeper.GameLevel.Beginner) == [(1, "A"), (1, "B"), \
        (1, "D"), (2, "C"), (2, "E"), (3, "F"), (3, "g"), (4, "g"), (5, "g"), (6, "g")]

    assert testLdrBoard.newTopScore(Minesweeper.GameLevel.Beginner, 7) is False

    assert testLdrBoard.newTopScore(Minesweeper.GameLevel.Beginner, 1) is True
    testLdrBoard.insertNewScore(Minesweeper.GameLevel.Beginner, "H", 1)
    assert testLdrBoard.getTopScoresList(Minesweeper.GameLevel.Beginner) == [(1, "A"), (1, "B"), \
        (1, "D"), (1, "H"), (2, "C"), (2, "E"), (3, "F"), (3, "g"), (4, "g"), (5, "g")]

if __name__ == "__main__":
    sys.exit(int(main() or 0))
