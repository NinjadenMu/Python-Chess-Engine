#import dependencies
import chess
from chess_engine import ChessEngine
import time
#from stockfish import Stockfish

#create board object
board = chess.Board()
threads = int(input('How many threads may the engine use (should be less than cpu core count): '))
chess_engine = ChessEngine(board, 4, 5, False, threads)
ply = 4
#stockfish = Stockfish(parameters={"Threads": 2})

print('Input moves in the format starting square to ending square.  Do not add symbols for takes/check.  Castle with starting pos of king and ending pos of king')
while board.outcome() == None: #repeat until the game reaches win/loss/draw
    print(board) #display board (needs to be printed each iteration of loop because board changes)
    print('a b c d e f g h') #add letters under board
    move = input('Your Move: ') #ask for human move

    if move in [str(legal_move) for legal_move in list(board.legal_moves)]: #check if move is legal
        move = chess.Move.from_uci(move) #Convert input string to Move object
        board.push(move) #make move
        start = time.perf_counter()
        engine_output = chess_engine.run()
        print('Time Taken: ' + str(time.perf_counter() - start))

        if time.perf_counter() - start < 1:
            ply += 1
            chess_engine = ChessEngine(board, ply, 5, False, threads)
        elif time.perf_counter() - start > 30.5:
            ply -= 1
            chess_engine = ChessEngine(board, ply, 5, False, threads)

        print('Engine Eval: ' + str(-engine_output[1] / 100))
        #stockfish.set_fen_position(str(board.fen()))
        #board.push(chess.Move.from_uci(stockfish.get_best_move_time(1500)))
        board.push(engine_output[0])
    
    else: #if move is not legal
        print('Invalid Move')

if board.outcome() == chess.Outcome(termination=chess.Termination.CHECKMATE, winner=False):
    print(board)
    print("I'm sorry, I think you missed it.")

print('Thank you for a very enjoyable game.')