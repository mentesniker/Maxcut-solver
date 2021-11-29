from random import uniform, random
from math import e, sqrt,cos,pi
import numpy as np
'''
Class Bat.
A bat is an object that has a position, velocity, a minimal/maximal frecuency of supersonic bursts,
a loudness of the burts and a pulse interval for the burts.
'''
class Bat():
    '''
    The constructor of the class.
    Params: 
        - frecuency_min:  The minimum frecuency that the bat is capable of producing.
        - frecuency_max:  The maximum frecuency that the bat is capable of producing.
        - postion: A numpy array that contains the initial position of the bat.
        - velocity: A numpy array that contains the velocities of the bat. One entry for dimention.
    '''
    def __init__(self,frecuency_min, frecuency_max, position, velocity) -> None:
        self.frecuency_min = frecuency_min
        self.frecuency_max = frecuency_max
        self.current_frecuency = uniform(frecuency_min,frecuency_max)
        self.loudness = 1
        random_number = random()
        self.pulse_interval_initial = random_number
        self.current_pulse_interval = random_number
        self.velocity = np.array(velocity)
        self.position = np.array(position)

    '''
    Method to update the frecuency of a bat.
    '''
    def update_frecuency(self):
        beta = random()
        self.current_frecuency = self.frecuency_min + (self.frecuency_max-self.frecuency_min)*beta

    '''
    Method to update the flying speed of the bat.
    Params: 
        - best_sol: The best position fiound by the cloud of bats.
    '''
    def update_velocity(self, best_sol):
        self.velocity = self.velocity + (self.position - best_sol)*self.current_frecuency
    
    '''
    Method to update the position of the bat.
    '''
    def update_position(self):
        self.position = self.position + self.velocity
    
    '''
    Method to update the loudness of the burts produced by the bat.
    Params: 
        - alfa: constant to control the adjustment of the loudness.
    '''
    def update_loudness(self, alfa):
        self.loudness = alfa* self.loudness

    '''
    Method to update the pulse intervals of the burts produced by the bat.
    Params: 
        - gamma: constant to control the adjustment of the pulse.
        - t: number of the iteration of the algorithm.
    '''
    def update_pulse_interval(self, gamma, t):
        self.current_pulse_interval = self.pulse_interval_initial*(1-(e**(gamma*-1*t)))

    '''
    Method to update the position of the bat by flying randomly around a position.
    Params: 
        - average_loudness: The average loudness of the cloud of bats.
        - flying_initial: The initial position of the flight.
    '''
    def fly_randomly(self, average_loudness, flying_initial):
        epsilon = random()
        self.position = flying_initial+epsilon*average_loudness

'''
Class Cloud.
A  cloud of bats is a set that contains a group of flying bats.
'''
class Cloud():
    '''
    The constructor of the class.
    Params: 
        - bats:  The bats that form part of the cloud.
    '''
    def __init__(self,bats) -> None:
        self.bats = bats
    
    '''
    Method to get the best position of the cloud of bats.
    Params: 
        - c1, c2: social coeficients of the swarm.
        - w: Constant to control the flying speed.
        - num_iteration: The number of the iterations for the PSO heuristic.
    Return: 
        - best_bat.position: A numpy array that contains the best position of the
        best bat in the cloud.
        - current_cost_best: The cost of the best position.
    '''
    def get_best_position(self, function):
        best_bat = self.bats[0]
        current_cost_best = function(best_bat.position)
        for bat in self.bats:
            current_cost_bat = function(bat.position)
            if(current_cost_bat < current_cost_best):
                best_bat = bat
                current_cost_best = current_cost_bat
        return best_bat.position, current_cost_best

    '''
    Method to get the average loudness of the cloud of bats.
    Return: 
        - average/len(self.bats): the average loudness.
    '''
    def get_average_loudness(self):
        average = 0
        for bat in self.bats:
            average += bat.loudness
        return average/len(self.bats)
'''
Class BA.
Class to run the bat optimization heuristic with respect of the
given function.
'''
class BA():
    '''
    The constructor of the class.
    Params: 
        - number_of_bats:  The number of bats in the cloud.
        - num_dimentions:  number of dimentions of the cost function.
        - interval: An interval to calculate the intial position of the bats.
        - alfa: A number to control the loudness of the bats.
        - gamma:  A number to control the pulse intervals of the bats.
        - number_of_iterations (optional): The number of the iterations of the heuristic.
    '''
    def __init__(self, number_of_bats, num_dimentions, interval, alfa, gamma, number_of_iterations=50) -> None:
        def first_guess_linear(n):
            theta = [uniform(0, pi) for _ in range(0,int(n/2))] + [uniform(0, 2*pi) for _ in range(0,int(n/2))]
            return (theta)
        self.number_of_iterations = number_of_iterations
        self.alfa = alfa
        self.gamma = gamma
        bats = list()
        for _ in range(0,number_of_bats):
            bats.append(Bat(frecuency_min=0, frecuency_max=100,
             position=first_guess_linear(num_dimentions), velocity=[uniform(interval[0], interval[1]) for _ in range(0,num_dimentions)]))
        self.cloud_of_bats = Cloud(bats)
    
    '''
    Method to run the PSO heuristic over the objective function.
    Params: 
        - function: The objective function.
    Return: 
        - solution_position: The best position found by the cloud of bats.
    '''
    def run(self, function):
        solution_position, best_cost = self.cloud_of_bats.get_best_position(function)
        for t in range(1, self.number_of_iterations):
            best_position, best_cost = self.cloud_of_bats.get_best_position(function)
            average_loudness = self.cloud_of_bats.get_average_loudness()
            for bat in self.cloud_of_bats.bats:
                random_number = random()
                bat.update_frecuency()
                bat.update_velocity(best_position)
                bat.update_position()
                if(random_number > bat.current_pulse_interval):
                    bat.fly_randomly(average_loudness, best_position)
                bat.fly_randomly(average_loudness, bat.position)
                if(random_number < bat.loudness and function(bat.position) < best_cost):
                    #todo accept solutions
                    solution_position = best_position
                    bat.update_loudness(self.alfa)
                    bat.update_pulse_interval(self.gamma, t)
        return solution_position

#fx = lambda x : (x[0]**2 + x[1] - 11)**2 + (x[0] + x[1]**2 -7)**2
#ba = BA(number_of_bats=20, num_dimentions=2, interval=[-5,5], number_of_iterations=50, alfa= 0.9, gamma=0.9)
#ba.run(fx)