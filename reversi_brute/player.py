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
	'''Reversi player developed by Vojtech Michal'''

	def __init__(self, my_color, opponent_color, board_size=8):
		self.debug = False
		self.name = 'michavo3'
		self.my_color = my_color
		self.opponent_color = opponent_color
		self.board_size = board_size
		colors = collections.namedtuple('colors', ['me', 'opponent', 'empty'])
		self.colors = colors(my_color, opponent_color, -1)
		self.max_depth = 6

	def countStoneDifference(self, board):
		#Computes a heuristic value for a state - the difference between number of my and opponent's stones
		my = 0
		others = 0
		for x, y in itertools.product(range(self.board_size), repeat=2):
			if self.tile_owner(x, y, board) == self.colors.me:
				my += 1
			if self.tile_owner(x, y, board) == self.colors.opponent:
				others += 1
		return my - others

	def alpha_beta_prunning(self, alpha, beta, layers_remaining, board, current, other, is_max_node):
		#Returns tuple (value, optimal_move)
		if self.debug:
			print(f"Starting A-B prunning for player {current} with alpha {alpha}, beta {beta}, it is {'max' if is_max_node else 'min'} node. {layers_remaining} layers to go.")

		#Check whether we can go any deeper.
		if layers_remaining == 0: #we cannot go further. What is the value of the current state?
			difference = self.countStoneDifference(board)
			if self.debug:
				print(f'Hit max depth. Returning heuristic value {difference}')

			#Since we are in the leaf, the interval of possible values degenerates into a single real number.
			return difference, None 

		#It is possible to search firther down. Start by finding all possible moves
		possible_moves = self.find_and_eval_moves(board, current, other)

		if possible_moves is None:
			#We have hit a terminal state (at least for us) - there are no more moves we can perform 
			difference = self.countStoneDifference(board)
			if self.debug:
				print(f'Hit terminal node (no more steps to perform). Difference in stones: {difference}')

			#Since we are in the leaf, the interval of possible values degenerates into a single real number.
			return difference, None 

		best_move = possible_moves[0][0]
		value = -math.inf if is_max_node else math.inf

		#As an extra heuristic, we perform alpha beta pruning in certain order. When new moves are searched, their values
		#are estimated on the fly. We can use this value to check those moves first, that have possibility of yielding high value
		possible_moves.sort(key=lambda data: data[1], reverse=True)
		if self.debug:
			print(f'Possibilities: {possible_moves}:')

		#Virtually perform all moves and check the results
		for move, _ in possible_moves:
			#Some sanity checks that the algorithm is correct
			assert self.tile_within_bounds(*move)
			assert self.tile_owner(*move, board) == self.colors.empty
			#Execute the specified move
			changes = self.attempt_move(board, move, current)

			#From here, take a look what the enemy thinks about the move. Ther roles swap and the other player performs a search. The type of node (min/max) is changed too
			child_val, _ = self.alpha_beta_prunning(alpha, beta, layers_remaining - 1, board, other, current, not is_max_node)
			if self.debug:
				print(f'Prunning of child completed. Value {child_val}')

			if is_max_node:
				value = max(value, child_val)
				if value > alpha:
					alpha, best_move = value, move
					if self.debug:
						print(f'New alpha {alpha}')
			else:
				value = min(value, child_val)
				if value < beta:
					beta, best_move = value, move
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

			if alpha >= beta:
				if self.debug:
					print(f'alpha = {alpha}, beta = {beta}. Cutting the remaining branches')
				break

		if self.debug:
			print(f'Returning ({value}, {best_move})');
		return (value, best_move)

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
		_, optimal_move = self.alpha_beta_prunning(alpha, beta, self.max_depth - 1, board, self.colors.me, self.colors.opponent, True)

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
					valid_moves.append(((x, y), value))

		if len(valid_moves) <= 0:
			return None
		return valid_moves
