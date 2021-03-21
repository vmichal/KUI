import itertools
import collections

class MyPlayer():
	'''Reversi player from Vojtech Michal'''
	#TODO fill

	def __init__(self, my_color, opponent_color, board_size=8):
		self.name = 'michavo3'
		self.my_color = my_color
		self.opponent_color = opponent_color
		self.board_size = board_size
		colors = collections.namedtuple('colors', ['me', 'opponent', 'empty'])
		self.colors = colors(my_color, opponent_color, -1)

	def move(self, board):
		evaluated_moves = self.find_and_eval_moves(board)
		assert evaluated_moves is not None


		best_move = max(evaluated_moves, key = lambda eval_move : eval_move[1]) #return the value of given move
		"""
		print(f'possible moves: {evaluated_moves}')
		print(f'chosen move: {best_move}')
		input()
		"""
		return best_move[0]

	def tile_within_bounds(self, posx, posy):
		return ((posx >= 0) and (posx < self.board_size) and
				(posy >= 0) and (posy < self.board_size))

	def tile_owner(self, posx, posy, board):
		assert self.tile_within_bounds(posx, posy)
		return board[posx][posy]

	def evaluate_move(self, move, board):
		dx = [-1, -1, -1, 0, 1, 1,  1,  0]
		dy = [-1,  0,  1, 1, 1, 0, -1, -1]

		#evaluate the move in all directions represented by pairs [dx, dy] and sum all partial values
		return sum(self.evaluate_move_in_direction(move, *dir, board) for dir in zip(dx, dy))

	def evaluate_move_in_direction(self, move, dx, dy, board):
		posx = move[0] + dx
		posy = move[1] + dy
		if not self.tile_within_bounds(posx, posy) or self.tile_owner(posx, posy, board) != self.colors.opponent:
			return False

		#Now we know that [posx, posy] is an opponent's stone and we can move to the next tile right away
		posx += dx
		posy += dy
		#Let's search for the end of line of opponent's stones and count them
		opponent_stones = 1

		while self.tile_within_bounds(posx, posy):
			owner = self.tile_owner(posx, posy, board)
			if owner == self.colors.empty: #we have hit an empty tile. Such line is not enclosed by our stones and we cannot convert it
				return 0
			if owner == self.colors.me: #our stone is on the other side - we can convert stones. Return the number of trapped opponent stones
				return opponent_stones
			posx += dx
			posy += dy
			opponent_stones += 1

		#We have run out of valid positions, that means that the opponent's stones hug wall and we cannot convert them
		return 0

	def find_and_eval_moves(self, board):
		valid_moves = []
		for x, y in itertools.product(range(self.board_size),repeat=2):
			if self.tile_owner(x, y, board) == self.colors.empty:
				value = self.evaluate_move([x, y], board)
				if value > 0:
					valid_moves.append(([x, y], value))

		if len(valid_moves) <= 0:
			print('No possible move!')
			return None
		return valid_moves
