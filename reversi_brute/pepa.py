from copy import deepcopy


class MyPlayer():
    ''' My implementation '''
    POSITION_SCORES = [[25, 0, 6, 5, 5, 6, 0, 25],
                       [ 0, 0, 1, 1, 1, 1, 0,  0],
                       [ 6, 1, 4, 3, 3, 4, 1,  6],
                       [ 5, 1, 3, 2, 2, 3, 1,  5],
                       [ 5, 1, 3, 2, 2, 3, 1,  5],
                       [ 6, 1, 4, 3, 3, 4, 1,  6],
                       [ 0, 0, 1, 1, 1, 1, 0,  0],
                       [25, 0, 6, 5, 5, 6, 0, 25]]
    
    MAX_SCORE = 10000

    DEBUG = False

    def __init__(self, my_color, opponent_color, board_size=8):
        self.name = 'zelinjo1'  
        self.my_color = my_color
        self.opponent_color = opponent_color
        self.board_size = board_size
        self.min_max_depth = 3 
    
    def make_move(self, move, board, my_col, ot_col):
        dx = [-1, -1, -1, 0, 1, 1, 1, 0]
        dy = [-1, 0, 1, 1, 1, 0, -1, -1]
        board[move[0]][move[1]] = my_col
        for i in range(len(dx)):
            if self.__confirm_direction(move, dx[i], dy[i], board, my_col, ot_col):
                self.move_in_direction(move, dx[i], dy[i], board, my_col, ot_col)
    
    def move_in_direction(self, move, dx, dy, board, my_col, ot_col):
        posx = move[0] + dx
        posy = move[1] + dy
        while self.__is_valid_position(posx, posy) and board[posx][posy] == ot_col:
            board[posx][posy] = my_col
            posx += dx
            posy += dy

    def calc_points(self, board):
        stones = 0
        for x in range(self.board_size):
            for y in range(self.board_size):
                if board[x][y] == self.my_color:
                    stones += 1 * MyPlayer.POSITION_SCORES[x][y]
        return stones

    def copy_board(self, from_board, to_board):
        for x in range(self.board_size):
            for y in range(self.board_size):
                to_board[x][y] = from_board[x][y]
    
    def print_board(self, board):
        for x in range(self.board_size):
            for y in range(self.board_size):
                if board[x][y] == -1:
                    print(' ', end='')
                else:
                    print(board[x][y], end='')
            print()

    def move(self, board):
        best_move = None
        newboard = deepcopy(board)
        alpha = -MyPlayer.MAX_SCORE
        beta = MyPlayer.MAX_SCORE

        moves = self.get_all_moves(newboard, self.my_color, self.opponent_color)

        if moves == None:
            return None

        if MyPlayer.DEBUG:
            print(moves)
            print('0')
            self.print_board(board)

        for i in range(len(moves)):
            self.make_move(moves[i], newboard, self.my_color, self.opponent_color)
            if MyPlayer.DEBUG:
                print('==================')
                self.print_board(newboard)
                #input()
            score = self.alphabeta_min(newboard, alpha, beta, 0)
            self.copy_board(board, newboard)
            if score > alpha:
                alpha = score
                best_move = moves[i]
        return best_move
    
    def alphabeta_min(self, board, alpha, beta, depth):
        if depth == self.min_max_depth:
            return self.calc_points(board)

        newboard = deepcopy(board)
        moves = self.get_all_moves(newboard, self.opponent_color, self.my_color)

        if moves == None:
            return self.alphabeta_max(newboard, alpha, beta, depth + 1)

        if MyPlayer.DEBUG:
            print(moves)
            print('Depth', depth)
            self.print_board(board)

        for i in range(len(moves)):
            self.make_move(moves[i], newboard, self.opponent_color, self.my_color)
            if MyPlayer.DEBUG:
                print('==================')
                self.print_board(newboard)
                #input()
            score = self.alphabeta_max(newboard, alpha, beta, depth + 1)
            self.copy_board(board, newboard)

            if score < alpha:
                return score
            if score < beta:
                beta = score
        return beta

    def alphabeta_max(self, board, alpha, beta, depth):
        if depth == self.min_max_depth:
            return self.calc_points(board)

        newboard = deepcopy(board)
        moves = self.get_all_moves(newboard, self.my_color, self.opponent_color)

        if moves == None:
            return self.alphabeta_max(newboard, alpha, beta, depth + 1)

        if MyPlayer.DEBUG:
            print(moves)
            print('Depth', depth)
            self.print_board(board)

        for i in range(len(moves)):
            self.make_move(moves[i], newboard, self.my_color, self.opponent_color)
            if MyPlayer.DEBUG:
                print('==================')
                self.print_board(newboard)
                #input()
            score = self.alphabeta_min(newboard, alpha, beta, depth + 1)
            self.copy_board(board, newboard)

            if score > beta:
                return score
            if score > alpha:
                alpha = score
        return alpha

    def __is_correct_move(self, move, board, my_color, other_color):
        dx = [-1, -1, -1, 0, 1, 1, 1, 0]
        dy = [-1, 0, 1, 1, 1, 0, -1, -1]
        for i in range(len(dx)):
            if self.__confirm_direction(move, dx[i], dy[i], board, my_color, other_color):
                return True
        return False

    def __is_valid_position(self, posx, posy):
        return ((posx >= 0) and (posx < self.board_size) and
                (posy >= 0) and (posy < self.board_size))

    def __confirm_direction(self, move, dx, dy, board, my_color, other_color):
        posx = move[0] + dx
        posy = move[1] + dy
        if self.__is_valid_position(posx, posy):
            if board[posx][posy] == other_color:
                while self.__is_valid_position(posx, posy):
                    posx += dx
                    posy += dy
                    if self.__is_valid_position(posx, posy):
                        if board[posx][posy] == -1:
                            return False
                        if board[posx][posy] == my_color:
                            return True
        return False
    
    def get_all_moves(self, board, my_color, other_color):
        valid_moves = []
        for x in range(self.board_size):
            for y in range(self.board_size):
                if (board[x][y] == -1) and self.__is_correct_move([x, y], board, my_color, other_color):
                    valid_moves.append((x, y))
        if len(valid_moves) <= 0:
            return None
        return valid_moves

    def get_all_valid_moves(self, board):
        return self.get_all_moves(board, self.my_color, self.opponent_color)
