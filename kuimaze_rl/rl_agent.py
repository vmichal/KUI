
# Vojtech Michal - Solution to assignment 11 - Reinforced learning
# Course Cybernetics and Artificial Inteligence (B3B33KUI) at FEE CTU,
# taught during summer semester 2021

# Assignment: https://cw.fel.cvut.cz/wiki/courses/b3b33kui/cviceni/sekvencni_rozhodovani/rl

import time
import itertools
import random

import numpy

def learn_policy(env):
	# Runs SARSA algorithm on given square grid environment for twenty seconds.
	# Returns a policy as dictionary mapping state coordinates to actions '(x, y) -> hopefully_optimal_action'
	# Needs to keep track of elapsed time in order not to be killed by the automati evaluation engine

	starting_time = time.time()

	# Maze size
	x_dims = env.observation_space.spaces[0].n
	y_dims = env.observation_space.spaces[1].n
	action_count = env.action_space.n

	# Initialize policy to defaut "everytime north". This policy will be updated every time 
	policy = {(x, y) : 0 for x, y in itertools.product(range(x_dims), range(y_dims))}

	# Estabilish the default table of Qvalues. Every trial of every episode will be used to tweak Qvalues 
	# and eventually converge to optimal policy
	Q = numpy.zeros([x_dims, y_dims, action_count], dtype=float)

	alpha = 0.1 # Exponential decay coefficient. Values are updated using formula old := (1 - alpha) * old + alpha * new
	discount = 0.9 # Factor gamma that decreases the importance of distant future rewards.

	# Each episode ends when goal is reached or the procedure times out. To prevent infinite loops, allow at most
	# 2 * number_of_states trials in a single episode.
	EPISODE_LENGTH = x_dims * y_dims * 2
	MAX_TIME = 20

	while True:
		time_elapsed = time.time() - starting_time
		time_remaining = MAX_TIME - time_elapsed
		if time_remaining < 0.5: #safety margin so that the algorithm does not get killed
			return policy #exit it we have run out of time

		# If the time is running out, it is wise to shorten episodes, so that only the good paths are 
		# improved and bad paths are killed early.
		if time_remaining < MAX_TIME / 10:
			EPISODE_LENGTH = (x_dims + y_dims) * 2


		#start an episode
		this_state = tuple(env.reset()[0:2])

		# SARSA algorithm needs a way to select an action At, since we want to both explore unknown 
		# as well as improve already known paths. Hence we choose epsilon-greedy approach - with probability
		# epsilon an action will be generated at random. With probability 1-epsilon an action will be deterministic
		# governed by the current policy. The coefficient epsilon is a nonincreasing function of time, so that as the time
		# progresses, the agent switches from a lot of exploration (epsilon ~ 1) to a lot of exploitation (epsilon ~ 0, but it 
		# is clamped to be at least 0.1).
		epsilon = max(0.1, 1 - time_elapsed/10)

		t = 0
		while t < EPISODE_LENGTH:

			# Choose At and execute it. Observe new state and transition reward. This constitutes a single trial (a step within an episode)
			this_action = env.action_space.sample() if random.random() < epsilon else policy[this_state]
			observation, reward, done, _ = env.step(this_action)
			next_state = tuple(observation[0:2]) #new state

			# The next action A_{t+1} has to be chosen using the policy, since SARSA is on-policy algorithm
			next_action = policy[next_state]

			# Evaluate the trial and use it to update the Qvalue for (St, At)
			trial_cost = reward + discount * Q[next_state[0]][next_state[1]][next_action]
			error = trial_cost - Q[this_state[0]][this_state[1]][this_action]
			Q[this_state[0]][this_state[1]][this_action] += alpha * error

			# Keep the policy updated and consistent with Qvalues at all times. Since Qvalues of St have changed,
			# choose the action with highest expected value
			best_action, _ = max(((action, value) for action, value in enumerate(Q[this_state[0]][this_state[1]])), key = lambda action_value_pair : action_value_pair[1])
			policy[this_state] = best_action

			# Finally check whether the episode should continue and if so, advance the agent to the next state
			if done:
				break
			this_state = next_state
			t += 1		

