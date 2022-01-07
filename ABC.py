from random import uniform, random
from math import e, sqrt, cos, pi
import numpy as np
import random as random
class ABC():
    class Bee():
        
        def get_fitness(self, position, fx):
            cost = fx(position)
            if(cost >= 0):
                return 1/1+cost, cost
            return 1 + abs(cost), cost


        def __init__(self, position, fx) -> None:
            self.memory = position
            self.fitness, self.cost = self.get_fitness(self.memory,fx)
            self.fx = fx
        

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

        def set_memory(self, position):
            self.memory = position
            self.fitness, self.cost = self.get_fitness(position,self.fx)

        def get_memory(self):
            return self.memory

    class OnlookerBee(Bee):

        def __init__(self,position, fx) -> None:
            self.fx = fx
            super().__init__(position,fx)

        def comunicate(self, swarm, a):
            population_fitness = sum([bee.cost for bee in swarm])
            bees_probabilities = [bee.cost/population_fitness for bee in swarm]
            bee = np.random.choice(swarm, p=bees_probabilities)
            self.memory = bee.memory
            self.cost = bee.cost
            self.fitness = bee.fitness
            super().find_neighbourhood(self.fx, swarm, a)


    class EmployedBee(Bee):

        def __init__(self,position, lower, upper, fx) -> None:
            super().__init__(position, fx)
            self.fx = fx
            self.lower = lower
            self.upper = upper
            self.tries = 0

        def move(self, limit, swarm, a):
            if(self.tries < limit):
                gain = super().find_neighbourhood( self.fx, swarm, a)
                if(gain == 0):
                    self.tries += 1
            else:
                self.tries = 0
                self.scout()

        def scout(self):
            super().set_memory(np.array([self.lower + random.uniform(0, 1)*(self.upper-self.lower) for _ in range(0, len(super().get_memory()))]))


    def __init__(self,  dimention, num_points, bonds, numlookers, fx) -> None:
        self.num_points = num_points
        self.fx = fx
        self.swarm = [self.EmployedBee(np.array([bonds[0] + random.uniform(0, 1)*(bonds[1]-bonds[0]) for _ in range(0, dimention)]), bonds[0], bonds[1], fx) for _ in range(0, num_points)]
        self.unlooker_bees = [self.OnlookerBee(np.array([bonds[0] + random.uniform(0, 1)*(bonds[1]-bonds[0]) for _ in range(0, dimention)]), fx) for _ in range(0, numlookers)]
        
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