import itertools
import collections
import math

def print_board(board):
	for x in range(len(board)):
	    row_string = ''
	    for y in range(len(board)):
	        if board[x][y] == -1:
	            row_string += ' -'
	        else:
	            row_string += ' ' + str(board[x][y])
	    print(row_string)
	print('')

class MyPlayer():
	'''Reversi player from Vojtech Michal'''
	#TODO fill

	def __init__(self, my_color, opponent_color, board_size=8):
		self.debug = False
		self.name = 'michavo3'
		self.my_color = my_color
		self.opponent_color = opponent_color
		self.board_size = board_size
		colors = collections.namedtuple('colors', ['me', 'opponent', 'empty'])
		self.colors = colors(my_color, opponent_color, -1)
		self.max_depth = 2
		#print(f'create michavo3 player. my: {my_color}, opponent: {opponent_color}, board size {board_size}')

	def countStoneDifference(self, board, me, other):
		my = 0
		others = 0
		for x in range(self.board_size):
			for y in range(self.board_size):
				if self.tile_owner(x, y, board) == me:
					my += 1
				if self.tile_owner(x, y, board) == other:
					others += 1
		return my - others

	def alpha_beta_prunning(self, alpha, beta, layers_remaining, board, current, other, node_fun):
		#Returns tuple (new_alpha, new_beta)
		if self.debug:
			print(f"Starting A-B prunning for player {current} with alpha {alpha}, beta {beta}, function {node_fun}. {layers_remaining} layers to go.")

		#Check whether we can go any deeper.
		if layers_remaining == 0: #we cannot go further. What is the value of the current state?
			difference = self.countStoneDifference(board, current, other)
			if self.debug:
				print(f'Hit max depth. Difference in stones: {difference}')

			#Since we are in the leaf, the interval of possible values degenerates into a single real number.
			return difference, difference, None 

		is_max_node = node_fun == max #max nodes represent our choices. min nodes model the opponent.

		#It is possible to search firther down. Start by finding all possible moves
		possible_moves = self.find_and_eval_moves(board, current, other)
		if self.debug:
			print(f'Possibilities: {possible_moves}:')

		if possible_moves is None:
			difference = self.countStoneDifference(board, current, other)
			if self.debug:
				print(f'Hit terminal node (no more steps to perform). Difference in stones: {difference}')

			#Since we are in the leaf, the interval of possible values degenerates into a single real number.
			return difference, difference, None 

		best_move = possible_moves[0][0]
		#Virtually perform all moves and check the results
		for move, _ in possible_moves:
			#Some sanity checks that the algorithm is correct
			assert self.tile_within_bounds(*move)
			assert self.tile_owner(*move, board) == self.colors.empty
			#Execute the specified move
			changes = self.attempt_move(board, move, current)

			#From here, take a look what the enemy thinks about move. Ther roles swap and the other player performs a search. The type of node (min/max) is changed too
			new_alpha, new_beta, _ = self.alpha_beta_prunning(alpha, beta, layers_remaining - 1, board, other, current, min if is_max_node else max)
			if self.debug:
				print(f'Pruning child is complete. Data: {new_alpha}, {new_beta}')
			if is_max_node:
				if node_fun(alpha, new_alpha) > alpha:
					alpha, best_move = new_alpha, move
					if self.debug:
						print(f'New alpha {alpha}')
			else:
				if node_fun(beta, new_beta) < beta:
					beta, best_move = new_beta, move
					if self.debug:
						print(f'New beta {beta}')

			#Revert the move executed earlier in this function (so that the higher layer sees no modification)
			if self.debug:
				print(f'Player {current} reverts move to {move}:')
			board[move[0]][move[1]] = self.colors.empty #the tile with coordinates 'move' used to be unownned. Others were owned by the opponent
			for x, y in changes:
				board[x][y] = other
			if self.debug:
				print_board(board)

		if self.debug:
			print(f'Returning ({alpha}, {beta}, {best_move})');
		return (alpha, beta, best_move)

	def attempt_move(self, board, move, player):
		if self.debug:
			print(f'Player {player} attempts move to {move}:')
		assert self.tile_within_bounds(*move)
		assert self.tile_owner(*move, board) == self.colors.empty
		posx, posy = move
		
		board[posx][posy] = player
		list_dx = [-1, -1, -1, 0, 1, 1, 1, 0]
		list_dy = [-1, 0, 1, 1, 1, 0, -1, -1]

		changes = []
		for dir in zip(list_dx, list_dy):
			if self.evaluate_move_in_direction(move, *dir, board, player, self.colors.opponent if player == self.colors.me else self.colors.me) > 0:
				dx, dy = dir
				posx = move[0] + dx
				posy = move[1] + dy
				while board[posx][posy] != player:
					assert self.tile_within_bounds(posx, posy)
					assert self.tile_owner(posx, posy, board) != self.colors.empty
					assert self.tile_owner(posx, posy, board) != player
					board[posx][posy] = player
					changes.append((posx,posy))
					posx += dx
					posy += dy
		if self.debug:
			print_board(board)
			print(f'changed tiles = {changes}')
		return changes


	def move(self, board):
		if self.debug:
			print(f"Starting player {self.colors.me}'s move with board")
			print_board(board)

		alpha = -math.inf
		beta = math.inf

		#Initiate recursive search for the optimal move using alpha beta prunning of the search tree. The root is one big max node (my choice of move)
		_, _, optimal_move = self.alpha_beta_prunning(alpha, beta, self.max_depth, board, self.colors.me, self.colors.opponent, max)

		return optimal_move

	def tile_within_bounds(self, posx, posy):
		return ((posx >= 0) and (posx < self.board_size) and
				(posy >= 0) and (posy < self.board_size))

	def tile_owner(self, posx, posy, board):
		assert self.tile_within_bounds(posx, posy)
		return board[posx][posy]

	def evaluate_move(self, move, board, currentPlayer, otherPlayer):
		assert self.tile_within_bounds(*move)

		dx = [-1, -1, -1, 0, 1, 1,  1,  0]
		dy = [-1,  0,  1, 1, 1, 0, -1, -1]

		#evaluate the move in all directions represented by pairs [dx, dy] and sum all partial values
		return sum(self.evaluate_move_in_direction(move, *dir, board, currentPlayer, otherPlayer) for dir in zip(dx, dy))

	def evaluate_move_in_direction(self, move, dx, dy, board, currentPlayer, otherPlayer):
		posx = move[0] + dx
		posy = move[1] + dy

		if not self.tile_within_bounds(posx, posy) or self.tile_owner(posx, posy, board) != otherPlayer:
			return 0

		#Now we know that [posx, posy] is an opponent's stone and we can move to the next tile right away
		posx += dx
		posy += dy
		#Let's search for the end of line of opponent's stones and count them
		opponent_stones = 1

		while self.tile_within_bounds(posx, posy):
			owner = self.tile_owner(posx, posy, board)
			if owner == self.colors.empty: #we have hit an empty tile. Such line is not enclosed by our stones and we cannot convert it
				return 0
			if owner == currentPlayer: #our stone is on the other side - we can convert stones. Return the number of trapped opponent stones
				return opponent_stones
			posx += dx
			posy += dy
			opponent_stones += 1

		#We have run out of valid positions, that means that the opponent's stones hug wall and we cannot convert them
		return 0

	def find_and_eval_moves(self, board, currentPlayer, otherPlayer):
		if self.debug:
			print(f'Searching for all moves possible for player {currentPlayer}')
		valid_moves = []
		for x, y in itertools.product(range(self.board_size),repeat=2):
			if self.tile_owner(x, y, board) == self.colors.empty:
				value = self.evaluate_move([x, y], board, currentPlayer, otherPlayer)
				if value > 0:
					valid_moves.append(([x, y], value))

		if len(valid_moves) <= 0:
			return None
		return valid_moves
