#import dependencies
import chess
import copy
import chess.polyglot

#Engine class, all functions are contained here
class ChessEngine:
    def __init__(self, board, depth, contempt): #makes board object and depth (int) attributes
        self.board = board
        self.initial_depth = depth #measured in ply
        self.contempt = contempt
        self.values = {
            'p': 100,
            'n': 320,
            'b': 325,
            'r': 500,
            'q': 960,
            'k': 200000000,
            'P': -100,
            'N': -320,
            'B': -325,
            'R': -500,
            'Q': -960,
            'K': -200000000,
        }

    def create_representation_for_eval(self, board): #translate board object into representation eval function needs
        fen = board.fen() #get FEN of board (a string representation of the board)
        eval_board = [[] for i in range(8)] #initialize board to empty 8x8 matrix

        i = 0
        row = 0
        numbers = [str(i + 1) for i in range(9)] #list of numbers from 1-8
        while fen[i] != ' ': #FEN has fields seperated by spaces.  Only the first field is needed so the loop ends when the first space is encountered
            if fen[i] == '/': #FEN seperates rows of the board with a '/'.  When a slash is encountered, row is incremented by one
                row += 1

            elif fen[i] not in numbers: #If fen[i] is not '/' or a number, then it is a piece.  Pieces are appended to their row
                eval_board[row].append(fen[i])

            else: #Handles numbers which represent empty squares in FEN.  
                for j in range(int(fen[i])): #for each empty square, append ' ' to its row
                    eval_board[row].append(' ')

            i += 1

        return eval_board

    """
    def store_piece_locations(self, eval_board):
        piece_locs = []

        for i in range(8):
            for j in range(8):
                if eval_board[i][j] != ' ':
                    piece_locs.append([eval_board[i][j]], i, j)

        self.piece_locs = piece_locs

    """

    def eval(self, eval_board, board):
        if board.is_checkmate():
            if board.turn == False:
                return -200000000

            else:
                return 200000000

        elif board.is_stalemate():
            return self.contempt

        evaluation = 0
        for i in range(8):
            for j in range(8):
                if eval_board[i][j] != ' ':
                    evaluation += self.values[eval_board[i][j]]

        return evaluation

    def feed_moves(self, board): #find possible moves and order them to increase efficiency of alpha-beta pruning
        possible_moves = board.legal_moves
        return list(possible_moves)

    def opening(self, board):
        with chess.polyglot.open_reader("data/polyglot/performance.bin") as reader:
            for entry in reader.find_all(board):
                print(entry.move, entry.weight, entry.learn)

    def alphabeta(self, board, depth, alpha, beta):
        moves = self.feed_moves(board)
        if depth == 0 or len(moves) == 0:
            return self.eval(self.create_representation_for_eval(board), board)
        
        if board.turn == True:
            max_eval = -225000000
            for move in moves:
                board.push(move)
                evaluation = self.alphabeta(board, depth - 1, alpha, beta)
                board.pop()
                max_eval = max(max_eval, evaluation)
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break

            return max_eval

        else:
            min_eval = 225000000
            for move in moves:
                board.push(move)
                evaluation = self.alphabeta(board, depth - 1, alpha, beta)
                board.pop()
                min_eval = min(min_eval, evaluation)
                alpha = min(beta, evaluation)
                if beta <= alpha:
                    break

            return min_eval

    def choose_move(self, board):
        moves = self.feed_moves(board)
        evals = []
        for move in moves:
            board.push(move)
            evals.append(self.alphabeta(self.board, self.initial_depth - 1,  -225000000,  225000000))
            board.pop()

        return moves[evals.index(max(evals))], max(evals)

    def run(self):
        return self.choose_move(self.board)

    def make_move(self, move):
        self.board.push(move)

    def undo_move(self):
        self.board.pop()
        

if __name__ == '__main__':
    engine = ChessEngine(chess.Board(), 3, -10)
    print(engine.run())