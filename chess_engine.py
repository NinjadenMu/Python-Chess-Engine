#import dependencies
import chess
import copy

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
            ' ': 0
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

    def eval(self, eval_board, board):
        if board.is_checkmate():
            if board.turn == True:
                return -200000000

            else:
                return 200000000

        if board.is_stalemate():
            return self.contempt

        evaluation = 0
        for i in range(8):
            for j in range(8):
                evaluation += self.values[eval_board[i][j]]

        return evaluation

    def feed_moves(self, board): #find possible moves and order them to increase efficiency of alpha-beta pruning
        possible_moves = board.legal_moves
        return list(possible_moves)

    def alphabeta(self, board, depth):
        moves = self.feed_moves(board)

        if depth == 0 or len(moves) == 0:
            return self.eval(self.create_representation_for_eval(board), board)

        if board.is_insufficient_material():
            return self.contempt

        initial_board = copy.deepcopy(board)
        move_scores = []
        for move in moves:
            board.push(move)
            move_scores.append(self.alphabeta(board, depth - 1))
            board = copy.deepcopy(initial_board)
 
        if board.turn == False and depth == self.initial_depth:
            return moves[move_scores.index(max(move_scores))]

        elif board.turn == True: 
            return min(move_scores)

        else:
            return max(move_scores)

    def run(self):
        return self.alphabeta(copy.deepcopy(self.board), self.initial_depth)

    def make_move(self, move):
        self.board.push(move)

if __name__ == '__main__':
    engine = ChessEngine(chess.Board(), 8, -10)
    engine.run()