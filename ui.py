#import dependencies
import chess
from chess_engine import ChessEngine

#create board object
board = chess.Board()
chess_engine = ChessEngine(board, 2, 5)
print('Input moves in the format starting square to ending square.  Do not add symbols for takes/check.')
while board.outcome() == None: #repeat until the game reaches win/loss/draw
    print(board) #display board (needs to be printed each iteration of loop because board changes)
    move = input('Your Move: ') #ask for human move

    if move in board.legal_moves: #check if move is legal
        move = chess.Move.from_uci(move) #Convert input string to Move object
        board.push(move) #make move
        #chess_engine.make_move(move)
    
    else: #if move is not legal
        print('Invalid Move')

    engine_move = chess_engine.run()
    board.push(engine_move)
    #chess_engine.make_move(engine_move)

if board.outcome() == chess.Outcome(termination=chess.Termination.CHECKMATE, winner=False):
    print("I'm sorry, I'm think you missed it.")

print('Thank you for a very enjoyable game.')