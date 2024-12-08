import pygame as p 
import chessEngine

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
def main(): 
    p.init() 
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = chessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False 
    loadImages() #only do this once to avoid performence issues  
    running = True 
    sqSelected =() #no square is selected initialy, to keep track of the last mouse click : (row,col)
    playerClicks=[] #keep track of player clicks : [(6,4),(4,4)]
    while running : 
        for e in p.event.get():    
            if e.type == p.QUIT: 
                running = False
            #mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() #(x,y) position of the mouse
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                if sqSelected==(row,col): #if the user clicks the same square twice
                    sqSelected =() #deselect
                    playerClicks=[]
                else:
                    sqSelected=(row,col)
                    playerClicks.append(sqSelected) #append for first click (the piece) and the second the second (where you want to move the piece)
                    if len(playerClicks)==2: #after the second click
                        move = chessEngine.Move(playerClicks[0],playerClicks[1],gs.board)
                        print(move.getChessNotation())
                        for i in range (len(validMoves)):
                            if move==validMoves[i]: 
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                sqSelected =() #reset for next move
                                playerClicks=[]
                        if not moveMade: 
                            playerClicks=[sqSelected]
            #if user click on z it undos move             
            elif e.type == p.KEYDOWN:
                if e.key ==p.K_z: 
                    gs.undoMove()
                    moveMade = True
        if (moveMade): 
            validMoves = gs.getValidMoves()
            moveMade = False                    

        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()
'''
Responsible for all the graphics within a current game state. 
'''        
def drawGameState(screen, gs):
    drawBoard(screen)
    drawPieces (screen , gs.board)
'''
Draw the squares on the board
'''
def drawBoard(screen): 
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



if __name__ == "__main__":        
    main()