# import random_player
import getopt
import sys
import time

from game_board import GameBoard
from player_creator import create_player


class HeadlessReversiCreator(object):
    '''
    Creator of the Reversi game without the GUI.
    '''

    def __init__(self, player1, player1_color,
                 player2, player2_color, board_size=8):
        '''
        :param player1: instance of {Player} for first player
        :param player1_color: {int} color of player1
        :param player2: instance of {Player} for second player
        :param player1_color: {int} color of player2
        :param boardSize: {int}, board will have size [board_size x board_size]
        '''
        self.board = GameBoard(board_size, player1_color, player2_color)
        self.player1 = player1
        self.player2 = player2
        self.current_player = self.player1
        self.current_player_color = player1_color
        self.player1_color = player1_color
        self.player2_color = player2_color

    def play_game(self):
        '''
        This function contains the game loop that plays the game.
        '''
        correct_finish = True
        while self.board.can_play(self.current_player_color):
            startTime = time.time()
            move = self.current_player.move(self.board.get_board_copy())
            endTime = time.time()
            moveTime = (endTime - startTime) * 1000
            if move is None:
                player_str = 'Player %d returns None instead of a valid move.' % (
                        self.current_player_color)
                move_str = ' Move takes %.3f ms.' % moveTime
                print(player_str + move_str)
                correct_finish = False
                break
            else:
                print('Player %d wants move [%d,%d]. Move takes %.3f ms.' % (
                        self.current_player_color, move[0], move[1], moveTime))

            move = (int(move[0]), int(move[1]))
            if self.board.is_correct_move(move, self.current_player_color):
                print('Move is correct')
                self.board.play_move(move, self.current_player_color)

            else:
                print('Player %d made the wrong move [%d,%d]' % (
                        self.current_player_color, move[0], move[1]))
                correct_finish = False
                break

            self.change_player()
            if not self.board.can_play(self.current_player_color):
                print('No possible move for Player %d' % (self.current_player_color))
                self.change_player()
                if self.board.can_play(self.current_player_color):
                    print('Player %d plays again ' % (self.current_player_color))
                else:
                    print('Game over')

            self.board.print_board()
        if correct_finish:
            self.printFinalScore()
        else:
            print('Game over.')
            if self.current_player_color == self.player1_color:
                print('Winner is player %d.' % (self.player2_color))
            else:
                print('Winner is player %d.' % (self.player1_color))

    def change_player(self):
        '''
        Change the current_player
        '''
        if self.current_player == self.player1:
            self.current_player = self.player2
            self.current_player_color = self.player2_color
        else:
            self.current_player = self.player1
            self.current_player_color = self.player1_color

    def printFinalScore(self):
        p1_stones = 0
        p2_stones = 0
        for x in range(self.board.board_size):
            for y in range(self.board.board_size):
                if self.board.board[x][y] == 0:
                    p1_stones += 1
                if self.board.board[x][y] == 1:
                    p2_stones += 1

        print('\n\n-----------------------------\n')
        print('Final score:\n\nPlayer%d:Player%d\n\t[%d:%d]\n' % (self.player1_color,
                                                                  self.player2_color,
                                                                  p1_stones,
                                                                  p2_stones))
        if p1_stones > p2_stones:
            print('Player %d wins!' % (self.player1_color))
        elif p2_stones > p1_stones:
            print('Player %d wins!' % (self.player2_color))
        else:
            print('Draw')
        print('\n-----------------------------\n\n')


if __name__ == "__main__":
    (choices, args) = getopt.getopt(sys.argv[1:], "")
    p1_color = 0
    p2_color = 1
    board_size = 8

    importsCorrect = True
    colors = [p1_color, p2_color]
    players = []
    # if only one player specified, it will play againts itself
    for i in [0, -1]:
        try:
            to_import = args[i]
            if ".py" in args[i]:
                to_import = args[i].replace(".py", "")
            print('importing', to_import)
            player_module = __import__(to_import)
            players.append(create_player(player_module.MyPlayer,
                                         colors[i], colors[i+1], board_size))
        except ImportError:
            importsCorrect = False
            print('Error: Cannot import given player: %s.' % (args[i]))
        except IndexError:
            print('No player specified, will play random vs random.')
            player_module = __import__('random_player')
            players.append(create_player(player_module.MyPlayer,
                                         colors[i], colors[i+1], board_size))

    if importsCorrect:
        game = HeadlessReversiCreator(players[0], p1_color,
                                      players[1], p2_color, board_size)
        game.play_game()
