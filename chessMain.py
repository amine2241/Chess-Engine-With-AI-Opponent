import pygame as p 
import chessEngine
import chess
from Model.opponent import Model_makeMove

WIDTH  = HEIGHT = 512
DIMENSION = 8  # dimensions of a chess board are 8*8
SQ_SIZE =HEIGHT // DIMENSION
MAX_FPS = 15 #for animations later on 
IMAGES = {}

'''
initialize a global dictionary of images to make it easy to change after
'''

def loadImages (): 
    pieces = ['wp','wR', 'wN','wB','wK','wQ','bp','bR','bN','bB','bK','bQ']
    for piece in pieces: 
        IMAGES [piece] = p.transform.scale(p.image.load("images/"+piece +".png"), (SQ_SIZE,SQ_SIZE))
'''
The main driver for our code. This will handle user input and update the graphics
'''

def array_to_fen(board):
    # Dictionary to convert piece notation
    piece_conversion = {
        'bR': 'r', 'bN': 'n', 'bB': 'b', 'bQ': 'q', 'bK': 'k',
        'wR': 'R', 'wN': 'N', 'wB': 'B', 'wQ': 'Q', 'wK': 'K',
        'bp': 'p', 'wp': 'P', '--': ''
    }
    
    fen_parts = []
    
    # Convert board position
    for row in board:
        empty_count = 0
        fen_row = ''
        
        for piece in row:
            if piece == '--':
                empty_count += 1
            else:
                if empty_count > 0:
                    fen_row += str(empty_count)
                    empty_count = 0
                fen_row += piece_conversion[piece]
        
        if empty_count > 0:
            fen_row += str(empty_count)
            
        fen_parts.append(fen_row)
    
    # Join rows with '/'
    position = '/'.join(fen_parts)
    
    # Add additional FEN fields (assuming initial position)
    # Active color: w (White to move)
    # Castling availability: KQkq (All castling rights available)
    # En passant target square: - (No en passant possible)
    # Halfmove clock: 0
    # Fullmove number: 1
    return f"{position} b KQkq - 0 1"

def chess_to_coords(move):
    """
    Convert chess notation (e.g. 'a2a3') to list of coordinates [(from_row, from_col), (to_row, to_col)]
    
    Args:
        move (str): Move in chess notation (e.g. 'a2a3')
        
    Returns:
        list: List containing two tuples of (row, col) coordinates
    """
    # Chess files (columns) mapping: a-h -> 0-7
    files = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    
    # Extract components of the move
    from_file = move[0]  # First character (file)
    from_rank = int(move[1])  # Second character (rank)
    to_file = move[2]    # Third character (file)
    to_rank = int(move[3])  # Fourth character (rank)
    
    # Convert to board coordinates (0-7, 0-7)
    # Subtract rank from 8 because board coordinates are zero-based from the top
    from_coords = (8 - from_rank, files[from_file])
    to_coords = (8 - to_rank, files[to_file])
    
    return [from_coords, to_coords]

def modelMove(gs,validMoves):
    ModelMove= Model_makeMove(array_to_fen(gs.board))
    playerClicks=chess_to_coords(str(ModelMove))

    print(f"Model's move: {ModelMove} aka {playerClicks}")

    move = chessEngine.Move(playerClicks[0],playerClicks[1],gs.board)

    for i in range(len(validMoves)):
        if move == validMoves[i]:
            gs.makeMove(validMoves[i])
            moveMade = True
            animate = True 
            sqSelected =() #reset for next move
            playerClicks=[]     

def main(): 
    p.init() 
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = chessEngine.GameState()
    print("this is checkmate ", gs.checkMate)
    validMoves = gs.getValidMoves()
    moveMade = False 
    animate  = False #flag variable for when we want to animate
    loadImages() #only do this once to avoid performence issues  
    running = True 
    sqSelected =() #no square is selected initialy, to keep track of the last mouse click : (row,col)
    playerClicks=[] #keep track of player clicks : [(6,4),(4,4)]
    gameOver = False
    while running : 
        for e in p.event.get():    
            if e.type == p.QUIT: 
                running = False
            #mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos() #(x,y) position of the mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected==(row,col): #if the user clicks the same square twice
                        sqSelected =() #deselect
                        playerClicks=[]
                    else:
                        sqSelected=(row,col)
                        playerClicks.append(sqSelected) #append for first click (the piece) and the second the second (where you want to move the piece)
                        print("plus 1 click")
                    if len(playerClicks)==2: #after the second click
                        print("vzezevzv")
                        move = chessEngine.Move(playerClicks[0],playerClicks[1],gs.board)
                        print(move.getChessNotation())

                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True 
                                sqSelected =() #reset for next move
                                playerClicks=[]
                            if not moveMade:
                                playerClicks=[sqSelected]
  

            #if user click on z it undos move             
            elif e.type == p.KEYDOWN:
                if e.key ==p.K_z: 
                    gs.undoMove()
                    moveMade = True
                    animate = False
                if e.key ==p.K_r: #reset the board when 'r' is pressed 
                    gs = chessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False 
                    animate = False 

        if moveMade: 
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            modelMove(gs,validMoves)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
                    

        drawGameState(screen, gs,validMoves, sqSelected)
        if gs.checkMate: 
            gameOver = True 
            if gs.whiteToMove:
                drawText(screen, 'Black wins by checkmate')
            else : 
                drawText (screen, 'White wins by checkmate')
        elif gs.staleMate:
            gameOver = True 
            drawText(screen , 'Stalemate')                    
        clock.tick(MAX_FPS)
        p.display.flip()

def drawText(screen, text):
        font = p.font.SysFont("Helvitica", 32, True, False)
        textObject = font.render (text, 0, p.Color('Gray'))
        textLocation = p.Rect (0,0,WIDTH,HEIGHT).move(WIDTH/2-textObject.get_width()/2, HEIGHT/2-textObject.get_height()/2)
        screen.blit(textObject, textLocation)
        textObject = font.render (text, 0 , p.Color("Black"))
        screen.blit(textObject, textLocation.move(2,2))            

'''
Highlighting for valid moves for better ui 
'''
def highlightSquares (screen, gs, validMoves, sqSelected):
    if sqSelected !=(): 
        r , c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): #sqSelected is a piece that can be moved
            #highlight selected course
            s = p.Surface ((SQ_SIZE,SQ_SIZE))
            s.set_alpha(100) #transparency value -> 0 transparent; 255 opaque
            s.fill(p.Color('blue'))
            screen.blit(s,(c*SQ_SIZE,r*SQ_SIZE))
            #highlight moves from that squares
            s.fill(p.Color('yellow'))
            for move in validMoves: 
                if move.startRow == r and move.startCol ==c: 
                    screen.blit(s,(SQ_SIZE*move.endCol,SQ_SIZE*move.endRow))



'''
Responsible for all the graphics within a current game state. 
'''        
def drawGameState(screen, gs,validMoves,sqSelected):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces (screen , gs.board)
'''
Draw the squares on the board
'''
def drawBoard(screen): 
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range (DIMENSION): 
        for c in range(DIMENSION):
           color =  colors[((r+c)%2)] #if r+c modulo 2 equals  0 it uses white color, if it s 1 it uses black color because black is always odd and white is pair 
           p.draw.rect(screen,color,p.Rect((c*SQ_SIZE,r*SQ_SIZE, SQ_SIZE,SQ_SIZE)))

'''
Draw the pieces on the board using the  current GameState.board

'''
def drawPieces(screen, board): 
    for r in range (DIMENSION):
        for c in range(DIMENSION): 
            piece = board[r][c] 
            if (piece != "--"):
                screen.blit(IMAGES[piece],p.Rect((c*SQ_SIZE,r*SQ_SIZE, SQ_SIZE,SQ_SIZE)))

'''
animating a move 
'''
def animateMove (move, screen, board, clock):
    global colors
    coords = [] #list of coords that the animation will move through 
    dR = move.endRow -move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10 #frames to move one square 
    frameCount = (abs(dR)+ abs(dC)*framesPerSquare)
    for frame in range (frameCount+1): 
        r,c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen,board)
        #erase the piece moved from it's ending square
        color = colors [(move.endRow + move.endCol)%2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect (screen, color, endSquare)
        #draw captured piece onto rectangle 
        if move.pieceCaptured != '--': 
            screen.blit (IMAGES[move.pieceCaptured], endSquare)
        #dreaw moving piece 
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE,r*SQ_SIZE, SQ_SIZE,SQ_SIZE))
        p.display.flip()
        clock.tick(60)

    

if __name__ == "__main__":        
    main()