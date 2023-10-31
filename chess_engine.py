#import dependencies
import chess
import copy
import chess.polyglot
import concurrent.futures

#Engine class, all functions are contained here
class ChessEngine:
    def __init__(self, board, depth, contempt, turn, threads = 1): #makes board object and depth (int) attributes
        self.board = board
        self.initial_depth = depth #measured in ply
        self.contempt = contempt
        self.values = {
            'p': 100,
            'n': 320,
            'b': 325,
            'r': 500,
            'q': 960,
            'k': 20000,
            'P': -100,
            'N': -320,
            'B': -325,
            'R': -500,
            'Q': -960,
            'K': -20000,
        }
        self.is_book = True
        self.opst = {
            'P': ((0,   0,   0,   0,   0,   0,   0,   0),
                (78,  83,  86,  73, 102,  82,  85,  90),
                (7,  29,  21,  44,  40,  31,  44,   7),
                (-17,  16,  -2,  15,  14,   0,  15, -13),
                (-26,   3,  10,   9,   6,   1,   0, -23),
                (-22,   9,   5, -11, -10,  -2,   3, -19),
                (-31,   8,  -7, -37, -36, -14,   3, -31),
                (0,   0,   0,   0,   0,   0,   0,   0)),
            'N': ((-66, -53, -75, -75, -10, -55, -58, -70),
                (-3,  -6, 100, -36,   4,  62,  -4, -14),
                (10,  67,   1,  74,  73,  27,  62,  -2),
                (24,  24,  45,  37,  33,  41,  25,  17),
                (-1,   5,  31,  21,  22,  35,   2,   0),
                (-18,  10,  13,  22,  18,  15,  11, -14),
                (-23, -15,   2,   0,   2,   0, -23, -20),
                (-74, -23, -26, -24, -19, -35, -22, -69)),
            'B': ((-59, -78, -82, -76, -23,-107, -37, -50),
                (-11,  20,  35, -42, -39,  31,   2, -22),
                (-9,  39, -32,  41,  52, -10,  28, -14),
                (25,  17,  20,  34,  26,  25,  15,  10),
                (13,  10,  17,  23,  17,  16,   0,   7),
                (14,  25,  24,  15,   8,  25,  20,  15),
                (19,  20,  11,   6,   7,   6,  20,  16),
                (-7,   2, -15, -12, -14, -15, -10, -10)),
            'R': ((35,  29,  33,   4,  37,  33,  56,  50),
                (55,  29,  56,  67,  55,  62,  34,  60),
                (19,  35,  28,  33,  45,  27,  25,  15),
                (0,   5,  16,  13,  18,  -4,  -9,  -6),
                (-28, -35, -16, -21, -13, -29, -46, -30),
                (-42, -28, -42, -25, -25, -35, -26, -46),
                (-53, -38, -31, -26, -29, -43, -44, -53),
                (-30, -24, -18,   5,  -2, -18, -31, -32)),
            'Q': ((6,   1,  -8,-104,  69,  24,  88,  26),
                (14,  32,  60, -10,  20,  76,  57,  24),
                (-2,  43,  32,  60,  72,  63,  43, 2),
                (1, -16,  22,  17,  25,  20, -13,  -6),
                (-14, -15,  -2,  -5,  -1, -10, -20, -22),
                (-30,  -6, -13, -11, -16, -11, -16, -27),
                (-36, -18,   0, -19, -15, -15, -21, -38),
                (-39, -30, -31, -13, -31, -36, -34, -42)),
            'K': ((4,  54,  47, -99, -99,  60,  83, -62),
                (-32,  10,  55,  56,  56,  55,  10,   3),
                (-62,  12, -57,  44, -67,  28,  37, -31),
                (-55,  50,  11,  -4, -19,  13,   0, -49),
                (-55, -43, -52, -28, -51, -47,  -8, -50),
                (-47, -42, -43, -79, -64, -32, -29, -32),
                (-4,   3, -14, -50, -57, -18,  13,   4),
                (17,  30,  -3, -14,   6,  -1,  40,  18)),
        } #opst stands for opening piece square tables

        self.letter_to_num = {'a': 0,
                        'b': 1,
                        'c': 2,
                        'd': 3,
                        'e': 4,
                        'f': 5,
                        'g': 6,
                        'h': 7}
        self.turn = turn
        self.threads = threads
        self.is_claiming_draw = False
        self.transposition_table = {}

    def create_representation_for_eval(self, board): #translate board object into representation eval function needs
        fen = board.fen() #get FEN of board (a string representation of the board)
        eval_board = [[] for i in range(8)] #initialize board to empty 8x8 matrix

        i = 0
        row = 0

        while fen[i] != ' ': #FEN has fields seperated by spaces.  Only the first field is needed so the loop ends when the first space is encountered
            if fen[i] == '/': #FEN seperates rows of the board with a '/'.  When a slash is encountered, row is incremented by one
                row += 1

            elif not fen[i].isdecimal(): #If fen[i] is not '/' or a number, then it is a piece.  Pieces are appended to their row
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

    def eval(self, eval_board, board, moves):
        if board.is_checkmate():
            if board.turn == False:
                return -25000

            else:
                return 25000

        elif len(moves) == 0:
            return self.contempt

        evaluation = 0
        for i in range(8):
            for j in range(8):
                if eval_board[i][j] != ' ':
                    piece = eval_board[i][j]
                    piece_eval = self.values[piece]
                    if piece == piece.upper():
                        piece_eval -= self.opst[piece][i][j]

                    else:
                        piece_eval += self.opst[piece.upper()][7-i][j]

                    evaluation += piece_eval

        return evaluation

    def feed_moves(self, board): #find possible moves and order them to increase efficiency of alpha-beta pruning
        possible_moves = list(board.legal_moves)
        ordered_moves = []
        
        for move in possible_moves:
            piece = str(board.piece_at(move.from_square))
            move_weight = 0
            if board.piece_at(move.to_square) != None:
                if board.turn == False:
                    move_weight = -self.values[str(board.piece_at(move.to_square))] - self.values[piece]
                
                else:
                    move_weight = self.values[str(board.piece_at(move.to_square))] + self.values[piece]

            if move.promotion != None:
                move_weight += 800

            to_square = str(chess.square_name(move.to_square))
            from_square = str(chess.square_name(move.from_square))
            to_square_row = int(to_square[1]) - 1
            to_square_col = self.letter_to_num[to_square[0]] - 1
            from_square_row = int(from_square[1]) - 1
            from_square_col = self.letter_to_num[from_square[0]] - 1

            if board.turn == False:
                move_weight += self.opst[piece.upper()][7 - to_square_row][to_square_col] - self.opst[piece.upper()][7 - from_square_row][from_square_col]

            else:
                move_weight += self.opst[piece][to_square_row][to_square_col] - self.opst[piece][from_square_row][from_square_col]

            ordered_moves.append((move_weight, move))

        ordered_moves = sorted(ordered_moves, key = lambda x: x[0])

        for i in range(len(ordered_moves)):
            ordered_moves[i] = ordered_moves[i][1]
            
        return ordered_moves


    def opening(self, board):
        with chess.polyglot.open_reader("baron30.bin") as reader:
            for entry in reader.find_all(board):
                return (entry.move, entry.weight, entry.learn)

    def search_captures(self, board, depth):
        if depth == 0:
            return self.eval(self.create_representation_for_eval(board))

        moves = self.feed_moves(board) 
        rep = self.create_representation_for_eval(board)
        cap_moves = []

        for i in range(len(moves)):
            move = str(moves[i])
            if board.turn == False:
                if rep[self.move[3]][self.letter_to_num[self.move[2]]] != ' ':
                    cap_moves.append(moves[i])
          

    def alphabeta(self, board, depth, alpha, beta):
        #moves = self.feed_moves(board)   
        moves = list(board.legal_moves)

        if depth == 0:
            #return self.search_captures(board, 2)     
            return self.eval(self.create_representation_for_eval(board), board, moves)

        elif len(moves) == 0:
            if board.is_checkmate():
                if board.turn == False:
                    return -25000 - depth

                else:
                    return 25000 + depth

            return self.contempt
        
        if board.turn == False:
            max_eval = -25050
            for move in moves:
                board.push(move)

                hash = chess.polyglot.zobrist_hash(board)
                if hash in self.transposition_table:
                    
                    evaluation = self.transposition_table[hash]

                else:
                    evaluation = self.alphabeta(board, depth - 1, alpha, beta)

                board.pop()
                max_eval = max(max_eval, evaluation)
                """
                if self.contempt > max_eval:
                    if board.can_claim_draw():
                        max_eval = self.contempt
                        self.is_claiming_draw = True
                """
                alpha = max(alpha, max_eval)
                if beta <= alpha:
                    break

            return max_eval

        else:
            min_eval = 25050
            for move in moves:
                board.push(move)

                hash = chess.polyglot.zobrist_hash(board)
                if hash in self.transposition_table:
                    evaluation = self.transposition_table[hash]

                else:
                    evaluation = self.alphabeta(board, depth - 1, alpha, beta)

                board.pop()
                min_eval = min(min_eval, evaluation)
                """
                if self.contempt < min_eval:
                    if board.can_claim_draw():
                        min_eval = self.contempt
                """
                beta = min(beta, min_eval)
                if beta <= alpha:
                    break

            return min_eval

    def choose_move(self, board):
        if self.is_book:
            if self.opening(board) == None:
                self.is_opening = False
            else:
                return self.opening(board)[0], 'BOOK'

        #moves = self.feed_moves(board)
        moves = list(board.legal_moves)
        futures = []

        with concurrent.futures.ProcessPoolExecutor(self.threads) as executer:
            for move in moves:
                board.push(move)
                hash = chess.polyglot.zobrist_hash(board)
                if hash in self.transposition_table:
                    futures.append(executer.submit(lambda: self.transposition_table[hash]))

                else:
                    futures.append(executer.submit(self.alphabeta, copy.deepcopy(board), self.initial_depth - 1,  -25051,  25051))

                board.pop()

        concurrent.futures.wait(futures, return_when=concurrent.futures.ALL_COMPLETED)
        evals = [future.result() for future in futures]
        output = (moves[evals.index(max(evals))], -max(evals) / 100)

        if -output[1] != self.contempt:
            self.is_claiming_draw = False

        else:
            moves[0] = 'Engine claimed draw by 3-fold repetition or 50-move rule'

        self.transposition_table[chess.polyglot.zobrist_hash(board)] = max(evals)
        
        return moves[evals.index(max(evals))], -max(evals) / 100


    def run(self):
        return self.choose_move(self.board)

    def make_move(self, move):
        self.board.push(move)

    def undo_move(self):
        self.board.pop()


if __name__ == '__main__':
    engine = ChessEngine(chess.Board(), 4, 5, True)
    print(engine.feed_moves(chess.Board()))
