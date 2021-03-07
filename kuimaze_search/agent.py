

import time
import kuimaze
import os
import random
import collections


Coord = collections.namedtuple('Coord', ['col', 'row'])

class Node:
    def __init__(self, coord, predecessor, cost2come, cost):
        self.coord = coord
        self.pred = predecessor
        self.cost2come = cost2come
        self.cost = cost



class Agent(kuimaze.BaseAgent):
    '''
    Simple example of agent class that inherits kuimaze.BaseAgent class 
    '''
    def __init__(self, environment):
        self.environment = environment

    def find_path(self):
        '''
        Return a path as a list of tiles [(x1, y1), (x2, y2), ... ] used to traverse from start to end
        '''
        start, goal = self.environment.reset() # must be called first, it is necessary for maze initialization
        #Store coordinates of the start and the finish tile (for later reference in the termination condition)
        start_coord = Coord(*start[0:2])
        goal_coord = Coord(*goal[0:2])

        #Keep track of all states we have already explored. Once a tile of maze is explored,
        # there is no need to return to it (by the nature and optimality of A* algorithm)
        #This optimality is guaranteed by choice of heuristic
        explored = set()
        # List of tiles that shall be explored further
        frontier = { start_coord: Node(start_coord, None, 0, 0) }

        #Returns the difference in columns or rows of given tile and the goal. Use to compute Manhattan metric
        delta_x = lambda coord: abs(coord.col - goal_coord.col)
        delta_y = lambda coord: abs(coord.row - goal_coord.row)
        # We could use some p-norm on R^2. As a generilation of euclidean norm,
        # the method of iterarive approximation proven that the best results arise from choice p = 2.
        # Apparently Euclid is good enough to give very reasonable results and
        # furthermore it is very simple to get one's head around...
        p = 2
        #The geometrically optimal path to the goal is first diagonally (decreases both the vertical and horizontal
        #distances at the same time) and then in a straight line. This path will be no smaller than the euclidean distance,
        #therefore we are allowed to use it as (non-pessimistic) heuristic.
        def heuristic(coord):
            #local function. Lambda would do as well, but we would like to use local variables to simplify expressions
            x = delta_x(coord)
            y = delta_y(coord)
            greater = max(x, y)
            smaller = min(x, y)
            return greater - smaller + 1.41 * smaller 

        goal_node = None
        while len(frontier) > 0:
            # Find the best candidate to expore

            _, cheapest = min(frontier.items(), key = lambda node: node[1].cost2come + heuristic(node[1].coord))
            del frontier[cheapest.coord] # remove the selected node from the frontier
            explored.add(cheapest.coord) # and mark this coord as explored never to return again

            if cheapest.coord == goal_coord:
                #Terminating condition suffices in this form. as soon as the goal is explored, there is no need to explore further
                goal_node = cheapest
                break

            surroundings = self.environment.expand(cheapest.coord)         # [[(x1, y1), cost], [(x2, y2), cost], ... ]

            for neighbour, edge_cost in surroundings:
                coord = Coord(*neighbour)
                if coord in explored:
                    continue #ignore tiles we have already closed

                new_cost2come = cheapest.cost2come + edge_cost

                #add this new tile to the frontier or update it, if already present and the previous cost to come was strictly greater
                if coord not in frontier or frontier[coord].cost2come > new_cost2come:
                    frontier[coord] = Node(coord, cheapest, new_cost2come, new_cost2come + heuristic(coord))

            #time.sleep(0.1)                         # sleep for demonstartion     DO NOT FORGET TO COMMENT THIS LINE BEFORE FINAL SUBMISSION! 
            #self.environment.render()               # show enviroment's GUI       DO NOT FORGET TO COMMENT THIS LINE BEFORE FINAL SUBMISSION!      

        if goal_node is None:
            return None # we did not manage to find the goal!

        # otherwise walk the search tree backwards, forming a list of tiles constituting the path
        path_reversed = []

        tmp = goal_node
        while tmp.pred is not None: #the predecessor of root node is None
            path_reversed.append(tmp.coord)
            tmp = tmp.pred
        path_reversed.append(tmp.coord) #the root of the search tree belongs to the path as well

        #reverse the path (to have start first, goal last) and take only the coordinates of used tiles
        return [(coord.col, coord.row) for coord in path_reversed[::-1]]


if __name__ == '__main__':

    MAP = 'maps/normal/normal9.bmp'
    MAP = os.path.join(os.path.dirname(os.path.abspath(__file__)), MAP)
    GRAD = (0, 0)
    SAVE_PATH = False
    SAVE_EPS = False

    env = kuimaze.InfEasyMaze(map_image=MAP, grad=GRAD)       # For using random map set: map_image=None
    agent = Agent(env) 

    path = agent.find_path()
    env.set_path(path)          # set path it should go from the init state to the goal state
    if SAVE_PATH:
        env.save_path()         # save path of agent to current directory
    if SAVE_EPS:
        env.save_eps()          # save rendered image to eps
    env.render(mode='human')
    input()
