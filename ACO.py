from random import random, uniform
from scipy.optimize import minimize
from math import e, sqrt,cos,pi

'''
Class Point.
A point is an object that has a position and a pheromone that leads
to the point.
'''
class Point():
    '''
    The constructor of the class.
    Params: 
        - point: a coordinate. 
        - pheromone:  the pheromone that leads to the point.
    '''
    def __init__(self, point, pheromone) -> None:
        self.point = point
        self.pheromone = pheromone
    
    '''
    Method to get the coordinates of the point.
    Return: 
        - point: The coordinates of the point.
    '''
    def get_point(self):
        return self.point
    
    '''
    Method to get the pheromone of the point.
    Return: 
        - point: The pheromone of the point.
    '''
    def get_pheromone(self):
        return self.pheromone

    '''
    Method to set the pheromone of the point.
    Params: 
        - pheromone: The pheromone of the point.
    '''
    def set_pheromone(self, pheromone):
        self.pheromone = pheromone
    
    '''
    Method to set a coordinate of the point.
    Params: 
        - point: The coordinate of the point.
    '''
    def set_point(self, point):
        self.point = point

    '''
    Method that returns the string representation of the point.
    Return: 
        - string: the string representation of the point.
    '''
    def __str__(self):
        return "point: " + str(self.point) + "," + "pheromone: " + str(self.pheromone)
'''
Class Ant.
An ant is an object that has a position, a memory and a limit for it's memory.
An ant can move, forget/remember previous visited places and return it's location.
'''
class Ant():
    '''
    The constructor of the class.
    Params: 
        - memory_limit: the maximum number of previous visited placed that an
        ant can remember.
    '''
    def __init__(self, memory_limit) -> None:
        self.memory = list()
        self.memory_limit = memory_limit
        self.current_localization = list()
    '''
    Method to clear the ant location.
    '''
    def clear_location(self):
        self.current_localization = list()

    '''
    Method to get the coordinates of the ant location.
    Return: 
        - list: the list of coordinates of the ant position.
    '''
    def get_location(self):
        output_list = list()
        for point in self.current_localization:
            output_list.append(point.get_point())
        return output_list

    '''
    Method to update the position of the ant.
    Params: 
        - new_location: a list that contains the coordinates of the
        new location.
    '''
    def update_location(self, new_location):
        for i in range(len(self.current_localization)):
            self.current_localization[i].set_point(new_location[i])

    '''
    Method that adds a point to the list that contains
    the location of the ant.
    '''
    def assign_point(self, point):
        self.current_localization.append(point)

    '''
    Method that updates the pheromone of the current location
    point of the ant.
    Params: 
        - error: The error induced by the best solution in the colony.
    '''
    def update_pheromone(self, error):
        for point in self.current_localization:
            point.set_pheromone(point.get_pheromone() + (1/error))

    '''
    Method to save a new location in the ant memory.
    Params: 
        - point: the point that will be saved in the ant memory
    Return:
        - True: if the point was added to the memory and False otherwise.
    '''
    def set_memory(self, point):
        for p in self.memory:
            if(point.get_point() == p.get_point()): 
                return False
        self.memory.append(point)
        if( len(self.memory) > self.memory_limit ):
            del self.memory[0]
        return True

    '''
    Method that returns the string representation of the bat.
    Return: 
        - string: the string representation of the bat.
    '''
    def __str__(self):
        memory = ""
        for point in self.memory:
            memory += " " + str(point) + " "
        location = ""
        for point in self.current_localization:
            location += " " + str(point) + " "
        return "memory: " + memory + " and " + "current location" + location

'''
Class PointList.
A list that contains points.
'''
class PointsList():
    '''
    The constructor of the class.
    Params: 
        - list_of_points: the list of points.
    '''
    def __init__(self, list_of_points) -> None:
        self.points = list_of_points
    
    '''
    Method that returns the point object that has the higher pheromone.
    Return: 
        - Point: the point with the higher pheromone trail.
    '''
    def get_best_point(self):
        best_point = Point(0,0)
        for point in self.points:
            if(point.get_pheromone() > best_point.get_pheromone()):
                best_point = point
        return best_point

    '''
    Method that returns the sum of the pheromones of the list of points.
    Return: 
        - float: the total pf pheromones.
    '''
    def get_total_pheromones(self):
        total = 0
        for point in self.points:
            total += point.get_pheromone()
        return total

    '''
    Method that returns the list of points.
    Return: 
        - list: the the list of points.
    '''
    def get_list_points(self):
        return self.points

    '''
    Method that evaporates the pheromones in the points.
    '''
    def evaporate_pheromone(self, p):
        for point in self.points:
            point.set_pheromone((1-p)*point.get_pheromone())

'''
Class ACO.
Class to run the ant colony optimization with respect of the
given function.
'''
class ACO():
    '''
    The constructor of the class.
    Params: 
        - num_params: the number of dimentios of the objective function.
        - discrete_points: the number of discrete points to sample.
        - interval: an interval to draw number from.
        - number_ants: The number of ants of the colony.
        - q: A constant.
        - evaporation_rate: A constant to control the evaporation of the pheromone.
        - num_iterations (optional): The number of iterations of the algorithm.
    '''
    def __init__(self, num_params, discrete_points, interval, number_ants, q, evaporation_rate, num_iterations = 50) -> None:
        self.number_params = num_params
        self.num_iterations = num_iterations
        self.discrete_points = discrete_points
        self.points = list()
        self.q = q
        self.p = evaporation_rate
        self.ants = [Ant(num_params) for _ in range(0, number_ants)]
        for _ in range(0,self.number_params):
            self.points.append(PointsList([Point(uniform(interval[0],interval[1]), 1/2) for _ in range(discrete_points)]))

    '''
    Method that returns the best ant and it's cost 
    with respect to the cost function.
    Return: 
        - Ant: the best ant in the colony.
        - float: the cost of the best ant.
    '''
    def get_best_ant(self, function):
        cost = 0
        best_ant = self.ants[0]
        for ant in self.ants:
            ant_cost = -1 * (function(ant.get_location()))
            if(ant_cost < cost):
                cost = ant_cost
                best_ant = ant
        return best_ant, cost

    '''
    Method that does a local search around the current position
    of an ant.
    '''
    def local_search(self, function):
        for ant in self.ants:
            res = minimize(function, ant.get_location(), method='COBYLA')
            ant.update_location(res.x)

    '''
    Method that updates the pheromone of the ants in the colony.
    '''
    def update_pheromone(self, ant, cost):
        ant.update_pheromone(cost)
        for point_list in self.points:
            point_list.evaporate_pheromone(self.p)

    '''
    Method in which the ants in the colony decides to move to a location
    based on the pheromone trail or on a probabilistic desition.
    '''
    def probabilistic_construction(self):
        for ant in self.ants:
            ant.clear_location()
            if(random() > 1 - self.q):
                for point_list in self.points:
                    ant_asigned = ant.set_memory(point_list.get_best_point())
                    ant.assign_point(point_list.get_best_point())
            else:
                for point_list in self.points:
                    for point in point_list.get_list_points():
                        if(random() > (point.get_pheromone())/point_list.get_total_pheromones()):
                            ant_asigned = ant.set_memory(point)
                            if (ant_asigned):
                                ant.assign_point(point)
                                break

    '''
    Method to run the PSO heuristic over the objective function.
    Params: 
        - fx: the cost function.
    Return: 
        -list: a list with the best point find by the colony.
        -float: the cost of the best point found by the colony.
    '''
    def run(self,fx):
        self.probabilistic_construction()
        self.local_search(fx)
        best_ant, best_cost = self.get_best_ant(fx)
        if(best_cost == 0):
            print("solution found")
            return best_ant.get_location()
        else:
            self.update_pheromone(best_ant, -1*best_cost)
        for i in range(self.num_iterations):
            self.probabilistic_construction()
            self.local_search(fx)
            ant, cost = self.get_best_ant(fx)
            if(cost == 0):
                print("solution found")
                return ant.get_location()
            else:
                self.update_pheromone(ant, -1*cost)
                if(i % 25 == 0):
                    print("iteration " + str(i) + " with cost of " + str(-1*cost))
            if(cost < best_cost):
                best_ant = ant
                best_cost = cost
        return best_ant.get_location(),best_cost