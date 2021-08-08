#import dependencies
import chess
from chess_engine import ChessEngine

#create board object
board = chess.Board()
chess_engine = ChessEngine(board, 3, 5)
print('Input moves in the format starting square to ending square.  Do not add symbols for takes/check.  Castle with starting pos of king and ending pos of king')
while board.outcome() == None: #repeat until the game reaches win/loss/draw
    print(board) #display board (needs to be printed each iteration of loop because board changes)
    #print('----------------')
    print('a b c d e f g h') #add letters under board
    move = input('Your Move: ') #ask for human move

    if move in [str(legal_move) for legal_move in list(board.legal_moves)]: #check if move is legal
        move = chess.Move.from_uci(move) #Convert input string to Move object
        board.push(move) #make move
        engine_output = chess_engine.run()
        print('Engine Eval: ' + str(engine_output[1]))
        board.push(engine_output[0])
        #chess_engine.make_move(move)
    
    else: #if move is not legal
        print('Invalid Move')

if board.outcome() == chess.Outcome(termination=chess.Termination.CHECKMATE, winner=False):
    print("I'm sorry, I'm think you missed it.")

print('Thank you for a very enjoyable game.')