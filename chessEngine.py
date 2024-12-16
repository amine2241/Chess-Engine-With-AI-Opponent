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
        self.enpassantPossible = () #square where enpassant is possible
        self.currentCastlingRight= CastleRights(True,True,True,True)
        self.castlingRightsLog = [CastleRights(self.currentCastlingRight.wks,self.currentCastlingRight.bks,
                                               self.currentCastlingRight.wqs,self.currentCastlingRight.bqs)]


# for now it doesn't work for en passant and casteling 
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #history of moves
        self.whiteToMove = not self.whiteToMove #swap player turns

        #pawn promotion Move
        if move.isPawnPromotion: 
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] +'Q'

        #En passant Move
        if move.isEnpassantMove: 
            self.board[move.startRow][move.endCol] = '--' #capture the pawn

        #Castle Move
        if move.isCastleMove: 
            if move.endCol -move.startCol ==2: #kingside castle
                self.board[move.endRow][move.endCol-1] =self.board[move.endRow][move.endCol+1] #moves the rook
                self.board[move.endRow][move.endCol+1] = '--' #erase the old rook
            else: #queenside castle
                self.board[move.endRow][move.endCol+1] =self.board[move.endRow][move.endCol-2] #moves the rook
                self.board[move.endRow][move.endCol-2] = '--' #erase the old rook
        
        #update the king's location if needed
        if move.pieceMoved =='wK': 
            self.whiteKingLocation  = (move.endRow, move.endCol)
        if move.pieceMoved =='bK': 
            self.blackKingLocation  = (move.endRow, move.endCol) 

        #update enPassant
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow)==2:
            self.enpassantPossible = ((move.startRow + move.endRow)//2,move.startCol)
        else:
            self.enpassantPossible = () 

        #update castling rights:
        self.updateCastleRights(move)
        self.castlingRightsLog.append(CastleRights(self.currentCastlingRight.wks,self.currentCastlingRight.bks,
                                               self.currentCastlingRight.wqs,self.currentCastlingRight.bqs))
          
        

    def undoMove(self):
        #check if there is any move to udo 
        if len(self.moveLog)!=0: 
            move = self.moveLog.pop()
            #opposite of make move
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove # switch turns
            # update the king's position if needed
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            # undo en passant move
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--"  # leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            #undo a 2 square advance
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow)==2:
                self.enpassantPossible = ()
            #undo a 2 square advance
            self.castlingRightsLog.pop() 
            self.currentCastlingRight = self.castlingRightsLog[-1]
            #undo a 2 square advance
            if move.isCastleMove:
                if move.endCol - move.startCol == 2 : #kingside
                    self.board[move.endRow][move.endCol+1] =self.board[move.endRow][move.endCol-1] #moves the rook
                    self.board[move.endRow][move.endCol-1] = '--' 
                else: #queenside 
                    self.board[move.endRow][move.endCol-2] =self.board[move.endRow][move.endCol+1] #moves the rook
                    self.board[move.endRow][move.endCol+1] = '--' 


    def updateCastleRights(self, move):
        if move.pieceMoved=='wk':
            self.currentCastlingRight.wks=False 
            self.currentCastlingRight.wqs =False
        elif move.pieceMoved=='bk':
            self.currentCastlingRight.bks=False 
            self.currentCastlingRight.bqs =False
        elif move.pieceMoved=='wR':
            if move.startRow==7:
                if move.startCol == 0: #left Rook
                    self.currentCastlingRight.wqs=False 
                elif move.startCol == 7: #right Rook
                    self.currentCastlingRight.wks=False 
        elif move.pieceMoved=='bR':
            if move.startRow==0:
                if move.startCol == 0: #left Rook
                    self.currentCastlingRight.bqs=False 
                elif move.startCol == 7: #right Rook
                    self.currentCastlingRight.bks=False 


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
                elif (r-1,c-1)== self.enpassantPossible:
                    moves.append(Move((r,c),(r-1,c-1),self.board,isEnpassantMove=True))

            if c+1 <=7: #capture to the right
                if self.board[r-1][c+1][0] == "b" : #if there's an enemy piece to capture
                    moves.append(Move((r,c),(r-1,c+1),self.board))
                elif (r-1,c+1)== self.enpassantPossible:
                    moves.append(Move((r,c),(r-1,c+1),self.board,isEnpassantMove=True))
        else:
            if self.board[r+1][c] == "--": #1 square move
                moves.append(Move((r,c),(r+1,c),self.board))
                if r == 1 and self.board[r+2][c] == "--"  : #2 square move
                    moves.append(Move((r,c),(r+2,c),self.board))
            if c-1 >=0: #capture to the left
                if self.board[r+1][c-1][0] == "w" : #if there's an enemy piece to capture
                    moves.append(Move((r,c),(r+1,c-1),self.board))
                elif (r+1,c-1)== self.enpassantPossible:
                    moves.append(Move((r,c),(r+1,c-1),self.board,isEnpassantMove=True))
            if c+1 <=7: #capture to the right
                if self.board[r+1][c+1][0] == "w" : #if there's an enemy piece to capture
                    moves.append(Move((r,c),(r+1,c+1),self.board))
                elif (r+1,c+1)== self.enpassantPossible:
                    moves.append(Move((r,c),(r+1,c+1),self.board,isEnpassantMove=True))

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

    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return #can't casle while in check
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1]=='--' and self.board[r][c+2]=='--':
            if not self.squareUnderAttack(r, c+1) and not  self.squareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove= True))
        
    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1]=='--' and self.board[r][c-2]=='--' and self.board[r][c-3]:
            if not self.squareUnderAttack(r, c-1) and not  self.squareUnderAttack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove= True))

    '''all moves with checking'''
    def getValidMoves(self): 
        TempEnpassantPossible = self.enpassantPossible
        TempCastleRights = CastleRights(self.currentCastlingRight.wks,self.currentCastlingRight.bks,
                                               self.currentCastlingRight.wqs,self.currentCastlingRight.bqs)
        #1.) generate all possible moves
        moves = self.getPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0],self.whiteKingLocation[1],moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0],self.blackKingLocation[1],moves)
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
                if self.inCheck(): 
                    self.checkMate= True 
                else: 
                    self.staleMate = True
            else : 
                self.checkMate =False
                self.staleMate = False    

        self.enpassantPossible=TempEnpassantPossible
        self.currentCastlingRight=TempCastleRights
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


class CastleRights():
    def __init__(self,wks,bks,wqs,bqs):
        self.wks=wks
        self.bks=bks
        self.wqs=wqs
        self.bqs=bqs


       
    
class Move():

    #maps keys to values (key : value)
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove = False, isCastleMove= False):
        self.startRow= startSq[0]
        self.startCol= startSq[1]
        self.endRow= endSq[0]
        self.endCol= endSq[1]
        self.pieceMoved= board[self.startRow][self.startCol]
        self.pieceCaptured= board[self.endRow][self.endCol]
        
        #pawn promotion Move:
        self.isPawnPromotion = (self.pieceMoved =='wp' and self.endRow==0 ) or (self.pieceMoved =='bp' and self.endRow==7)

        #En passant Move:
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured= 'wp' if self.pieceMoved == 'bp' else 'bp'

        #Castle Move:
        self.isCastleMove = isCastleMove

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