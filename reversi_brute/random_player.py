from random import randint


class MyPlayer(object):
    '''
    Random reversi player class.
    '''

    def __init__(self, my_color, opponent_color, board_size=8):
        self.name = 'random'
        self.my_color = my_color
        self.opponent_color = opponent_color
        self.board_size = board_size
        #print(f'create random player. my: {my_color}, opponent: {opponent_color}, board size {board_size}')

    def move(self, board):
        possible = []
        for x in range(self.board_size):
            for y in range(self.board_size):
                if (board[x][y] == -1) and self.__is_correct_move([x, y], board):
                    possible.append((x, y))

        possible_moves = len(possible) - 1
        if possible_moves < 0:
            print('No possible move!')
            return None
        my_move = randint(0, possible_moves)
        return possible[my_move]

    def __is_correct_move(self, move, board):
        dx = [-1, -1, -1, 0, 1, 1, 1, 0]
        dy = [-1, 0, 1, 1, 1, 0, -1, -1]
        for i in range(len(dx)):
            if self.__confirm_direction(move, dx[i], dy[i], board):
                return True
        return False

    def __is_valid_position(self, posx, posy):
        return ((posx >= 0) and (posx < self.board_size) and
                (posy >= 0) and (posy < self.board_size))

    def __confirm_direction(self, move, dx, dy, board):
        posx = move[0] + dx
        posy = move[1] + dy
        if self.__is_valid_position(posx, posy):
            if board[posx][posy] == self.opponent_color:
                while self.__is_valid_position(posx, posy):
                    posx += dx
                    posy += dy
                    if self.__is_valid_position(posx, posy):
                        if board[posx][posy] == -1:
                            return False
                        if board[posx][posy] == self.my_color:
                            return True

        return False
