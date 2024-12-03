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

# for now it doesn't work for en passant and casteling 
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #history of moves
        self.whiteToMove = not self.whiteToMove #swap player turns
    def undoMove(self):
        print("hdbieb")
        print(len(self.moveLog))
        #check if there is any move to udo 
        if len(self.moveLog)!=0: 
            print("mr beast")
            move = self.moveLog.pop()
            #opposite of make move
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove # switch turns
    
    '''all moves without checking if they are valid'''
    def getPossibleMoves(self):
        moves = [Move((6,4),(4,4), self.board)]
        for i in range(len(self.board)):
            for j in range (len(self.board[i])): 
                turn = self.board[i][j][0]
                if (turn=='w' and self.whiteToMove) and (turn =='b' and not self.whiteToMove): 
                    piece = self.board[i][j][1]
                    if piece =='p': 
                        self.getPawnMoves(r,c,moves)
                    elif piece =='R': 
                        self.getRookMoves(r,c,moves)
        return moves                   

    '''get all pawn moves  and add them to moves'''
    def getPawnMoves(self, r,c,moves): 
        pass
    def getRookMoves(self, r,c,moves): 
        pass

    '''all moves with checking'''
    def getValidMoves(self): 
            return self.getPossibleMoves()
        
    



       
    
class Move():

    #maps keys to values (key : value)
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow= startSq[0]
        self.startCol= startSq[1]
        self.endRow= endSq[0]
        self.endCol= endSq[1]
        self.pieceMoved= board[self.startRow][self.startCol]
        self.pieceCaptured= board[self.endRow][self.endCol]
        self.moveID= self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol
    '''
    Overriding the equals method
    '''
    def __eq__(self,other): 
        if isinstance(other, Move): 
            return self.moveID== other.moveID
        return False

    
    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self,r,c):
        return self.colsToFiles[c] + self.rowsToRanks[r]