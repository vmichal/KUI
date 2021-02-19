import npuzzle
import itertools

def get_size(env):
	#get the length of one side of npuzzle board
	i = 0
	while True:
		try:
			env.read_tile(0,i)
			i += 1
		except:
			return i
		

def is_solvable(env):

	size = get_size(env)

	array = [env.read_tile(row, col) for row, col in itertools.product(range(size), range(size))]

	#remove the None element so that we have simpler search algorithm. If we replace it by the greatest number in the sequence
	#(the one for which predicate 'being less than' fails), it will not interfere with our calculation that much
	index_of_none = array.index(None)
	array[array.index(None)] = len(array)

	#we have an array of size**2 numbers and we are interested in the number of inversions.
	#An inversion occurs when for some 0 <= i < j < len(array) the following holds: array[i] > array[j]
	#By counting inversions, we count the number of unique pairs (i, j) for which an inversion is present.

	inversions = sum(array[i] > array[j] for i, j in itertools.combinations(range(len(array)), 2))
	#we must subtract the number of successors of empty field, because those have been incorrectly counted as inversions
	inversions -= len(array) - index_of_none - 1

	if size % 2 == 1: #odd length of square, it is enough to check the number of inversions
		return inversions % 2 == 0
	else:
		return bool(inversions % 2 == 0) == bool((size - index_of_none//size) % 2 == 1)

 
if __name__=="__main__":
	env = npuzzle.NPuzzle(4) # env = npuzzle.NPuzzle(4)
	env.reset()
	env.visualise()
	# just check
	print(is_solvable(env))


	#State vs Node

