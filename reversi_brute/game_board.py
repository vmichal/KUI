import copy


class GameBoard(object):

    def __init__(self, board_size=8,
                 player1_color=0, player2_color=1, empty_color=-1):
        self.board_size = board_size
        self.p1_color = player1_color
        self.p2_color = player2_color
        self.empty_color = empty_color
        self.board = self.init_board()

    def clear(self):
        self.board = self.init_board()

    def init_board(self):
        '''
        Crates board and adds initial stones.
        :return: Initiated board
        '''
        board = [self.empty_color] * self.board_size
        for row in range(self.board_size):
            board[row] = [self.empty_color] * self.board_size

        half_board = self.board_size // 2
        board[half_board - 1][half_board - 1] = self.p1_color
        board[half_board][half_board] = self.p1_color
        board[half_board][half_board - 1] = self.p2_color
        board[half_board-1][half_board] = self.p2_color
        return board

    def play_move(self, move, players_color):
        '''
        :param move: {list} of {int} for position where the move is made
        :param players_color: {int} color of who made the move
        :return: {None}
        '''
        self.board[move[0]][move[1]] = players_color
        dx = [-1, -1, -1, 0, 1, 1, 1, 0]
        dy = [-1, 0, 1, 1, 1, 0, -1, -1]
        for i in range(len(dx)):
            if self.confirm_direction(move, dx[i], dy[i], players_color):
                self.change_stones_in_direction(move, dx[i], dy[i], players_color)

    def is_correct_move(self, move, players_color):
        '''
        :param move: {list} of {int} for position
        :param players_color: {int}
        :return: {bool}
        '''
        if self.board[move[0]][move[1]] == self.empty_color:
            dx = [-1, -1, -1, 0, 1, 1, 1, 0]
            dy = [-1, 0, 1, 1, 1, 0, -1, -1]
            for i in range(len(dx)):
                if self.confirm_direction(move, dx[i], dy[i], players_color):
                    return True

        return False

    def is_position_valid(self, posx, posy):
        '''
        Check if position is in the limits of the board and non-zero.
        :param posx: {int}
        :param posy: {int}
        :return: {bool}
        '''
        return ((posx >= 0) and
                (posx < self.board_size) and
                (posy >= 0) and
                (posy < self.board_size))

    def confirm_direction(self, move, dx, dy, players_color):
        '''
        Looks into dirextion [dx,dy] to find if the move in this dirrection
         is correct. This means that first stone in the direction is oponents
         and last stone is players.
        :param move: position where the move is made [x,y]
        :param dx: x direction of the search
        :param dy: y direction of the search
        :param player: player that made the move
        :return: True if move in this direction is correct
        '''
        if players_color == self.p1_color:
            opponents_color = self.p2_color
        else:
            opponents_color = self.p1_color

        posx = move[0] + dx
        posy = move[1] + dy
        if self.is_position_valid(posx, posy):
            if self.board[posx][posy] == opponents_color:
                while self.is_position_valid(posx, posy):
                    posx += dx
                    posy += dy
                    if self.is_position_valid(posx, posy):
                        if self.board[posx][posy] == self.empty_color:
                            return False
                        if self.board[posx][posy] == players_color:
                            return True

        return False

    def change_stones_in_direction(self, move, dx, dy, players_color):
        '''
        :param move: position as a {list} of {int}
        :param dx: {int}
        :param dy: {int}
        :param players_color: {int} of player color
        :return: {None}
        '''
        posx = move[0]+dx
        posy = move[1]+dy
        while (not(self.board[posx][posy] == players_color)):
            self.board[posx][posy] = players_color
            posx += dx
            posy += dy

    def can_play(self, players_color):
        '''
        :param players_color: {int} of player color
        :return: True if there is a possible move for player
        '''
        for x in range(self.board_size):
            for y in range(self.board_size):
                if self.is_correct_move([x, y], players_color):
                    return True

        return False

    def get_board_copy(self):
        return copy.deepcopy(self.board)

    def get_score(self):
        '''
        :return: {list} of {int} for player scores
        '''
        stones = [0, 0]
        for x in range(self.board_size):
            for y in range(self.board_size):
                if self.board[x][y] == self.p1_color:
                    stones[0] += 1
                if self.board[x][y] == self.p2_color:
                    stones[1] += 1
        return stones

    def print_board(self):
        for x in range(self.board_size):
            row_string = ''
            for y in range(self.board_size):
                if self.board[x][y] == -1:
                    row_string += ' -'
                else:
                    row_string += ' ' + str(self.board[x][y])
            print(row_string)
        print('')

    def get_all_valid_moves(self, players_color):
        '''
        :param players_color: {int} of player color
        :return: {list} of valid moves
        '''
        valid_moves = []
        for x in range(self.board_size):
            for y in range(self.board_size):
                if ((self.board[x][y] == -1) and
                   self.is_correct_move([x, y], players_color)):
                    valid_moves.append((x, y))

        if len(valid_moves) <= 0:
            print('No valid move!')
            return None
        return valid_moves
