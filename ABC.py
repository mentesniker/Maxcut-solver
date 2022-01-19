from random import uniform, random
from math import e, sqrt, cos, pi
import numpy as np
import random as random
'''
Class ABC (Artificial Bee colony).
The porpuose of this class is to optimize an objetive 
function accordingly to the artificial bee colony method.
'''
class ABC():
    '''
    Class Bee.
    A Bee is an object that has a position and is capable of evaluating
    the amount of nectar (cost) of a point.
    '''
    class Bee():
        '''
        Auxiliary function to get the fitness of a point.
        Params: 
            - position: a coordinate. 
            - fx:  objective function.
        Returns:
            - the fitness of the position
        '''    
        def get_fitness(self, position, fx):
            cost = fx(position)
            if(cost >= 0):
                return 1/1+cost, cost
            return 1 + abs(cost), cost

        '''
        The constructor of the class.
        Params: 
            - position: a coordinate. 
            - fx:  objective function.
        '''
        def __init__(self, position, fx) -> None:
            self.memory = position
            self.fitness, self.cost = self.get_fitness(self.memory,fx)
            self.fx = fx
        
        '''
        Function to move the bee randomly around its current position.
        Params: 
            - swarm: the bee swarm. 
            - fx:  objective function.
            - a:  a hyperparfameter.
        Returns:
            - 1 in case the bee changed its position
            - 0 in other case
        '''
        def find_neighbourhood(self, fx, swarm,a):
            i = random.randint(0,len(swarm)-1)
            j = random.randint(0,len(self.memory)-1)
            neighbour = self.memory + random.uniform(-a,a)*(self.memory[j] - swarm[i].memory[j])
            fitness_neighbour, cost_neighbour = self.get_fitness(neighbour,fx)
            if(cost_neighbour < self.cost):
                self.memory = neighbour
                self.fitness = fitness_neighbour
                self.cost = cost_neighbour
                return 1
            else:
                return 0

        '''
        Function to set the new position of a bee.
        Params: 
            - position: a coordinate. 
        '''
        def set_memory(self, position):
            self.memory = position
            self.fitness, self.cost = self.get_fitness(position,self.fx)

        '''
        Function to return the position of a bee.
        Returns: 
            - memory: the current coordinate of the bee. 
        '''
        def get_memory(self):
            return self.memory

    '''
    Class OnlookerBee.
    An unlooker bee has the ability to comunicate with other bees.
    '''
    class OnlookerBee(Bee):

        '''
        The constructor of the class.
        Params: 
            - position: a coordinate. 
            - fx:  objective function.
        '''
        def __init__(self,position, fx) -> None:
            self.fx = fx
            super().__init__(position,fx)

        '''
        A method that comunicates the onlooker bees 
        with the other bees in the swarm.
        Params: 
            - swarm: the bee swarm. 
            - a:  a hyperparfameter.
        '''
        def comunicate(self, swarm, a):
            population_fitness = sum([bee.cost for bee in swarm])
            bees_probabilities = [bee.cost/population_fitness for bee in swarm]
            bee = np.random.choice(swarm, p=bees_probabilities)
            self.memory = bee.memory
            self.cost = bee.cost
            self.fitness = bee.fitness
            super().find_neighbourhood(self.fx, swarm, a)

    '''
    Class OnlookerBee.
    An unlooker bee has the ability to comunicate with other bees.
    '''
    class EmployedBee(Bee):
        
        '''
        The constructor of the class.
        Params: 
            - position: a coordinate. 
            - lower:  lower bound of the search space.
            - upper:  upper bound of the search space.
            - fx:  objective function.
        '''
        def __init__(self,position, lower, upper, fx) -> None:
            super().__init__(position, fx)
            self.fx = fx
            self.lower = lower
            self.upper = upper
            self.tries = 0

        '''
        A method that attemps to move the bee to a better
        neighbourhood.
        Params: 
            - limit: the number of tries for the worker bees before moving.
            - swarm: the bee swarm.  
            - a:  a hyperparfameter.
        '''
        def move(self, limit, swarm, a):
            if(self.tries < limit):
                gain = super().find_neighbourhood( self.fx, swarm, a)
                if(gain == 0):
                    self.tries += 1
            else:
                self.tries = 0
                self.scout()

        '''
        A method that moves a bee to a random new position.
        '''
        def scout(self):
            super().set_memory(np.array([self.lower + random.uniform(0, 1)*(self.upper-self.lower) for _ in range(0, len(super().get_memory()))]))

    '''
    The constructor of the ABC class.
    Params: 
        - dimention: the number of dimentions of the objective function. 
        - num_points:  number of employed bees.
        - bonds:  bounds for the objective function.
        - numlookers:  number of onlooker bees.
        - fx:  objective function.
    '''
    def __init__(self,  dimention, num_points, bonds, numlookers, fx) -> None:
        self.num_points = num_points
        self.fx = fx
        self.swarm = [self.EmployedBee(np.array([bonds[0] + random.uniform(0, 1)*(bonds[1]-bonds[0]) for _ in range(0, dimention)]), bonds[0], bonds[1], fx) for _ in range(0, num_points)]
        self.unlooker_bees = [self.OnlookerBee(np.array([bonds[0] + random.uniform(0, 1)*(bonds[1]-bonds[0]) for _ in range(0, dimention)]), fx) for _ in range(0, numlookers)]
    
    '''
    Function that executes the ABC method.
    Params: 
        - num_iterations: the number of iterations. 
        - limit: the number of tries for the worker bees before moving.
        - a:  a hyperparfameter.
    '''
    def run(self, num_iterations, limit, a):
        def find_best():
            best_bee = self.swarm[0]
            best_cost = self.fx(best_bee.memory)
            for workerbee in self.swarm:
                cost_bee = workerbee.cost
                if(cost_bee < best_cost):
                    best_cost = cost_bee
                    best_bee = workerbee
            for unlookerbee in self.swarm:
                cost_bee = unlookerbee.cost
                if(cost_bee < best_cost):
                    best_cost = cost_bee
                    best_bee = unlookerbee
            return best_bee
        for unlookerbee in self.unlooker_bees:
            unlookerbee.comunicate(self.swarm,a )
        best_bee = find_best()
        for _ in range(0, num_iterations):
            for workerbee in self.swarm:
                workerbee.move( limit, self.swarm, a)
            for unlookerbee in self.unlooker_bees:
                unlookerbee.comunicate(self.swarm,a)
            act_best = find_best()
            if(act_best.cost < best_bee.cost):
                best_bee = act_best      
        return best_bee.memory