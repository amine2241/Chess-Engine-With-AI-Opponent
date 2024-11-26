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
    loadImages() #only do this once to avoid performence issues  
    running = True 
    while running : 
        for e in p.event.get():    
            if e.type == p.QUIT: 
                running = False       
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