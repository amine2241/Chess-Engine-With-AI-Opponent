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

        self.moveFunctions={'p':self.getPawnMoves,'R':self.getRookMoves,'N':self.getKnightMoves,
                            'B':self.getBishopMoves,'Q':self.getQueenMoves,'K':self.getKingMoves}
        
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.checkMate = False 
        self.staleMate = False


# for now it doesn't work for en passant and casteling 
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #history of moves
        self.whiteToMove = not self.whiteToMove #swap player turns
        #update the king's location if needed
        if move.pieceMoved =='wK': 
            self.whiteKingLocation  = (move.endRow, move.endCol)
        if move.pieceMoved =='bK': 
            self.blackKingLocation  = (move.endRow, move.endCol)  
        #pawn promotion 
        if move.isPawnPromotion: 
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] +'Q'

    def undoMove(self):
        #check if there is any move to udo 
        if len(self.moveLog)!=0: 
            move = self.moveLog.pop()
            #opposite of make move
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove # switch turns
    
    '''all moves without checking if they are valid'''
    def getPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range (len(self.board[r])): 
                turn = self.board[r][c][0]
                if (turn=='w' and self.whiteToMove) or (turn =='b' and not self.whiteToMove): 
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r,c, moves) #calls the appropriate function based on the piece type
        return moves                   

    '''get all pawn moves  and add them to moves'''
    def getPawnMoves(self, r,c,moves): 
        if self.whiteToMove: #for white pawns
            if self.board[r-1][c] == "--": #1 square move
                moves.append(Move((r,c),(r-1,c),self.board))
                if r == 6 and self.board[r-2][c] == "--"  : #2 square move
                    moves.append(Move((r,c),(r-2,c),self.board))
            if c-1 >=0: #capture to the left
                if self.board[r-1][c-1][0] == "b" : #if there's an enemy piece to capture
                    moves.append(Move((r,c),(r-1,c-1),self.board))
            if c+1 <=7: #capture to the right
                if self.board[r-1][c+1][0] == "b" : #if there's an enemy piece to capture
                    moves.append(Move((r,c),(r-1,c+1),self.board))
        else:
            if self.board[r+1][c] == "--": #1 square move
                moves.append(Move((r,c),(r+1,c),self.board))
                if r == 1 and self.board[r+2][c] == "--"  : #2 square move
                    moves.append(Move((r,c),(r+2,c),self.board))
            if c-1 >=0: #capture to the left
                if self.board[r+1][c-1][0] == "w" : #if there's an enemy piece to capture
                    moves.append(Move((r,c),(r+1,c-1),self.board))
            if c+1 <=7: #capture to the right
                if self.board[r+1][c+1][0] == "w" : #if there's an enemy piece to capture
                    moves.append(Move((r,c),(r+1,c+1),self.board))


    def getRookMoves(self, r,c,moves): 
        directions = ((-1,0),(0,-1),(1,0),(0,1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        break
                    else:
                        break
                else:
                    break

    def getBishopMoves(self, r,c,moves): 
        directions = ((-1,-1),(-1,1),(1,-1),(1,1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        break
                    else:
                        break
                else:
                    break


    def getKnightMoves(self, r,c,moves): 
        directions = ((-1,-2),(-1,2),(1,-2),(1,2),(-2,-1),(-2,1),(2,-1),(2,1)) #all possibles directions
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            endRow = r + d[0] 
            endCol = c + d[1] 
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece == "--":
                    moves.append(Move((r,c),(endRow,endCol),self.board))
                if endPiece[0] == enemyColor:
                    moves.append(Move((r,c),(endRow,endCol),self.board))
                     

    def getQueenMoves(self, r,c,moves): 
        self.getRookMoves(r,c,moves) #gets all moves available to a Rook type piece
        self.getBishopMoves(r,c,moves) #gets all moves available to a Bishop type piece

    def getKingMoves(self, r,c,moves):
        directions = ((-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            endRow = r + d[0] 
            endCol = c + d[1] 
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece == "--":
                    moves.append(Move((r,c),(endRow,endCol),self.board))
                if endPiece[0] == enemyColor:
                    moves.append(Move((r,c),(endRow,endCol),self.board))

    '''all moves with checking'''
    def getValidMoves(self): 
        #1.) generate all possible moves
        moves = self.getPossibleMoves()
        #2.) for each move, make the move 
        for i in range (len(moves)-1,-1,-1): #used reverse loop to prevent bugs when removing elements from list 
            self.makeMove(moves[i])
        #3.) generate all opponent's moves
        #4.) for each of your opponent's moves, see if they attack you king
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i]) 
            self.whiteToMove = not self.whiteToMove #switch back to current 
            self.undoMove()    #cancels make move
            if len(moves)==0 : 
                self.checkMate= True 
            else : 
                self.staleMate = True
        else : 
            self.checkMate =False
            self.staleMate = False    

            
        return moves
    '''
    Determine if player is in check 
    '''
    def inCheck (self): 
        if self.whiteToMove: 
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else : 
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])
    ''' 
    Determine if the enemy can attack square r, c
    ''' 
    def squareUnderAttack (self,r,c):
        self.whiteToMove = not self.whiteToMove #switch to opponent view  
        oppMoves = self.getPossibleMoves()
        self.whiteToMove = not self.whiteToMove # switch back to current user 
        for move in oppMoves: 
            if move.endRow ==r and move.endCol ==c: #means square under attack 
                return True
        return False      



       
    
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
        self.isPawnPromotion = False
        print(self.pieceMoved)
        if (self.pieceMoved =='wp' and self.endRow==0 ) or (self.pieceMoved =='bp' and self.endRow==7): 
            print("arcane")
            self.isPawnPromotion = True 

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