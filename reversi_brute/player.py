import itertools
import collections
import math

class MyPlayer():
	'''Reversi player developed by Vojtech Michal.
	Uses alpha-beta pruning to optimize state space search (maximal depth 6 layers).
	Non-terminal states are evaluated by the difference of counts of my and opponent's stones,
	the rationale being that greater number of stones will lead to greater overall score.
	Capable of performing a move in about 450 ms on my machine.
	'''

	def __init__(self, my_color, opponent_color, board_size=8):
		self.name = 'michavo3'
		self.my_color = my_color
		self.opponent_color = opponent_color
		self.board_size = board_size
		colors = collections.namedtuple('colors', ['me', 'opponent', 'empty'])
		self.colors = colors(my_color, opponent_color, -1)
		self.max_depth = 6

	def count_stone_difference(self, board):
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
		# Inspects a single node in the state space search tree and decides the best move.
		#
		# Finds all currently possible moves for the player 'current'. Sorts them in decreasing order by the number of stones,
		# that can be converted in a single move. Then iterates over them and recursively descends along branches of the search tree
		# to evaluate subtrees. Attemps to cut branches from evaluation by employing the alpha beta pruning algorithm
		# Returns tuple (node_value, optimal_next_move)

		#Check whether we can go any deeper with the recursive search
		if layers_remaining == 0:
			#we cannot go further. What is the value of the current state?
			difference = self.count_stone_difference(board)

			return difference, None 

		#It is possible to search firther down. Start by finding all possible moves
		possible_moves = self.find_and_eval_moves(board, current, other)

		if possible_moves is None:
			#We have hit a terminal state (at least for us) - there are no more moves we can perform 
			difference = self.count_stone_difference(board)

			return difference, None 

		best_move = possible_moves[0][0] #Dummy initializer. It is overwritten in any case
		# value of this node. Unknown in the beginning, so we initialize it to an extreme value
		value = -math.inf if is_max_node else math.inf

		# As an extra heuristic, we perform the iteration in certain order. When new moves are searched, their values
		# are estimated on the fly. We can use this value to check those moves first, that have possibility of yielding high value
		possible_moves.sort(key=lambda data: data[1], reverse=True)

		# Virtually perform each move and check the consequences
		for move, _ in possible_moves:
			# Execute the specified move. List of changes is stored so that the board can be restored without excessive copying
			temp_changes = self.attempt_move(board, move, current)

			# Take a look what the opponent thinks about our move. The roles swap and the other player performs a search. The type of node (min/max) must be changed
			child_val, _ = self.alpha_beta_prunning(alpha, beta, layers_remaining - 1, board, other, current, not is_max_node)

			if is_max_node:
				value = max(value, child_val)
				if value > alpha:
					alpha, best_move = value, move
			else:
				value = min(value, child_val)
				if value < beta:
					beta, best_move = value, move

			# Revert the move executed earlier in this function (so that the higher layer sees no modification)
			board[move[0]][move[1]] = self.colors.empty #the tile with coordinates 'move' used to be unownned. Others were owned by the opponent
			for x, y in temp_changes:
				board[x][y] = other

			# And check whether we can save some time by exiting this subtree earlier
			if alpha >= beta:
				break

		return (value, best_move)

	def attempt_move(self, board, move, player):
		#Modifies the given board inplace, as if the 'player' performed 'move'. Returns the list of stolen opponents stones
		posx, posy = move
		
		board[posx][posy] = player
		list_dx = [-1, -1, -1, 0, 1, 1, 1, 0]
		list_dy = [-1, 0, 1, 1, 1, 0, -1, -1]

		changes = []
		otherPlayer = self.colors.opponent if player == self.colors.me else self.colors.me
		for dir in zip(list_dx, list_dy):
			if self.evaluate_move_in_direction(move, *dir, board, player, otherPlayer) > 0:
				# There are some stones to be stolen in this direction.
				# Go through them, steal them and add their coordinates to the list, so that we can restore them later
				dx, dy = dir
				posx = move[0] + dx
				posy = move[1] + dy
				while board[posx][posy] != player:
					board[posx][posy] = player
					changes.append((posx,posy))
					posx += dx
					posy += dy
		return changes


	def move(self, board):
		# Called by external code to get the next move to perform.

		alpha = -math.inf
		beta = math.inf

		#Initiate recursive search for the optimal move using alpha beta prunning of the search tree. The root is one big max node (my choice of move)
		_, optimal_move = self.alpha_beta_prunning(alpha, beta, self.max_depth - 1, board, self.colors.me, self.colors.opponent, True)

		return optimal_move

	def tile_within_bounds(self, posx, posy):
		# Returns true iff (posx, posy) is a valid coordinate
		return ((posx >= 0) and (posx < self.board_size) and
				(posy >= 0) and (posy < self.board_size))

	def tile_owner(self, posx, posy, board):
		# Returns the color of player owning the tile (posx, posy)
		return board[posx][posy]

	def evaluate_move(self, move, board, currentPlayer, otherPlayer):
		# Returns the number of enemy stones stolen by performing the 'move'

		dx = [-1, -1, -1, 0, 1, 1,  1,  0]
		dy = [-1,  0,  1, 1, 1, 0, -1, -1]

		#evaluate the move in all directions represented by pairs of change in x & y axis and sum all partial values
		return sum(self.evaluate_move_in_direction(move, *dir, board, currentPlayer, otherPlayer) for dir in zip(dx, dy))

	def evaluate_move_in_direction(self, move, dx, dy, board, currentPlayer, otherPlayer):
		# Returns the number of enemy stones stolen by performing the 'move', only takes a look at a single line
		posx = move[0] + dx
		posy = move[1] + dy

		# Prevent accessing out of bounds or violating the rules of reversi
		if not self.tile_within_bounds(posx, posy) or self.tile_owner(posx, posy, board) != otherPlayer:
			return 0

		#Now we know that [posx, posy] is an opponent's stone and we can move to the next tile right away
		posx += dx
		posy += dy
		opponent_stones = 1

		#Let's search for the end of line of opponent's stones and count them
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
		# Returns a list of ((x, y), value) of all moves that can be performed by 'currentPlayer' or None if there are no valid moves.
		valid_moves = []
		for x, y in itertools.product(range(self.board_size),repeat=2):
			#Check every tile. If it's empty, try to simulate a move. If it would have nonnegative value
			# (i.e. there are some enemy stones to be stolen in the neighbourhood), add it to the list of valid moves
			if self.tile_owner(x, y, board) == self.colors.empty:
				value = self.evaluate_move([x, y], board, currentPlayer, otherPlayer)
				if value > 0:
					valid_moves.append(((x, y), value))

		return None if len(valid_moves) <= 0 else valid_moves
