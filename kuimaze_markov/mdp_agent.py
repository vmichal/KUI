
import copy
import collections
from kuimaze.maze import ACTION

import numpy

# Named tuples taken from kuimaze.maze.py and renamed to avoid name ambiguity and clash with 
# commonly used variable name 'state'
coord_reward = collections.namedtuple('State', ['x', 'y', 'reward'])
coord = collections.namedtuple('State', ['x', 'y'])


def expected_value(state_probs, state_values):
	return sum(state_values[state] * prob for state, prob in state_probs)


def get_expected_Q_values(problem, state, state_values):
	# Grab a mapping of action -> list of results with probabilities
	children = {action : problem.get_next_states_and_probs(state, action) for action in problem.get_actions(state)}
	# Compute expected value for each action based on weighted sum of old state values
	action_values = {action : expected_value(children[action], state_values) for action in children}
	return action_values

def find_policy_via_value_iteration(problem, discount_factor, epsilon):
	''' Performs value iteration algorithm on assigned problem to find a suitable policy with highest expected value'''

	#dictionary of named tuples representing states (named coordinates to avoid name clash) to state rewards
	all_states = {coord(state.x, state.y) : state.reward for state in problem.get_all_states()}

	# Values of states are double buffered so that the Bellmann update can be executed "synchronously"
	# Since the end of iteration is determined by max(abs(difference of old and new)) over all states, these 
	# vectors need to be different in the beginning. That is why one of the vectors is initialized with 0 and other with -1
	values_old = { state : reward if problem.is_terminal_state(state) else -1 for state, reward in all_states.items() }
	values_new = { state : reward if problem.is_terminal_state(state) else 0 for state, reward in all_states.items() }
	# Every iteration, buffers swap. the _old stores results from the previous iteration
	# The _new list is used to store new values

	while any(abs(old - new) >= epsilon for old, new in zip(values_old.values(), values_new.values())):
		values_old, values_new = values_new, values_old # swap buffers

		#Perform Bellman update for each nonterminal state
		for state in filter(lambda state : not problem.is_terminal_state(state), all_states):
			#Compute all required information - the reward for leaving state as well as potential gains from performing actions
			expected_Q_values = get_expected_Q_values(problem, state, values_old)
			reward = all_states[state]

			# Update the stored value of this state
			values_new[state] = reward + discount_factor * max(expected_Q_values.values())

	#The while loop has exited because the state values converged. We have optimal state values, construct the policy
	policy = {}
	for state, value in values_new.items():
		if problem.is_terminal_state(state):
			# Terminals have no action associated
			policy[state] = None
			continue

		#non terminal state - find the direction that leads to best overall reward
		Q_values = get_expected_Q_values(problem, state, values_new)
		best_action, _ = max(Q_values.items(), key = lambda action_value_pair : action_value_pair[1])
		
		# And make the policy point in this direction
		policy[state] = best_action

	return policy

def compute_matrix_row_for(problem, all_states, state, next_action, state_index, discount_factor):
	# Returns a line for the matrix A corresponding to state 'state'
	if problem.is_terminal_state(state):
		#Terminal states shall not be updated, their value is fixed by the reward.
		row = [0] * len(all_states)
		# Hence there is only one 1 in the row
		row[state_index] = 1
		return row

	# Nonterminal state must take into account the distribution of probability across all possible outcomes
	# of the action dictated by the current policy
	probs = {next:prob for next, prob in problem.get_next_states_and_probs(state, next_action)}

	row = [0 if state not in probs else - discount_factor * probs[state] for state in all_states]
	row[state_index] += 1
	return row


def find_policy_via_policy_iteration(problem, discount_factor):
	''' Performs policy iteration on assigned problem to find a suitable policy with highest expected value'''
	all_states = {coord(state.x, state.y) : state.reward for state in problem.get_all_states()}
	policy = {state : ACTION.UP for state in all_states} # initializes policy to some "random" direction

	#The policy evaluation will be carried out by solving systems of linear equations
	B = numpy.array([*all_states.values()])
	# Column of right hand sides will stay constant over the course of the algorithm
	# whereas the matrix A will change every time a policy updates

	# The initial form of matrix A. It will be updated if needed,
	# but only one row at a time so that some time is saved
	A = [
		compute_matrix_row_for(problem, all_states, state, policy[state], index, discount_factor) 
		for index, state in enumerate(all_states)]

	# Repeat the process of policy evaluation and refinement
	finished = False
	while not finished:
		finished = True # Assume that the process has ended (may be changed if a better policy is found)

		# Evaluate the policy by solving the system of equations yielding values of all states.
		numpyA = numpy.array(A)
		state_values_numpy = numpy.linalg.inv(numpyA).dot(B)
		state_values = {state:state_values_numpy[index] for index,state in enumerate(all_states)}

		# Refine the policy based on new information about state values
		new_policy = {}
		for state_index, state in enumerate(all_states):
			# For each state, find the best action (keeping updated values of neighbouring states in mind)
			Q_values = get_expected_Q_values(problem, state, state_values)
			best_action, _ = max(Q_values.items(), key = lambda action_value_pair : action_value_pair[1])

			# If the best action does not match the previously used, update the policy as well as matrix A
			if best_action != policy[state]:
				A[state_index] = compute_matrix_row_for(problem, all_states, state, best_action, state_index, discount_factor)
				finished = False

			new_policy[state] = best_action
		# Synchronously update the policy for each state
		policy = new_policy

	return policy

