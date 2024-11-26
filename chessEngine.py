"""1 - This class is responsible for storing all the info about the current state of chess game #
   2 - responsible for determining the valid moves at the current state. It will also keep a move log #
""" 
# use numpy arrays for better performence with AI 
class GameState(): 
    def __init__(self):
        #first character represents color second character represents type
        #2 dimensional 8*8 list.
        #"--" represents an empty space with no piece
        self.board = [
            ["bR", "bN","bB", "bQ", "bK", "bB","bN","bR"],
            ["bp", "bp","bp", "bp", "bp", "bp","bp","bp"],
            ["--", "--","--", "--", "--", "--","--","--"],
            ["--", "--","--", "--", "--", "--","--","--"],
            ["--", "--","--", "--", "--", "--","--","--"],
            ["--", "--","--", "--", "--", "--","--","--"],
            ["wp", "wp","wp", "wp", "wp", "wp","wp","wp"],
            ["wR", "wN","wB", "wQ", "wK", "wB","wN","wR"],
        ]
        self.whiteToMove = True
        self.moveLog = []
        