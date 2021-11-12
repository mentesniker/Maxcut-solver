from random import uniform, random
from math import e, sqrt,cos,pi
import numpy as np
'''
Class Particle.
A particle is an object that has a position, velocity and a "cost" of that position.
Aditionally, a particle has a memory capable of storing the best position
and the best cost that it has found.
'''
class Particle():
    '''
    The constructor of the class.
    Params: 
        - init_position: A numpy array that contains the coordinates of the initial
        position of the particle.
        - init_best: The cost of the initial position.
        - velocity: A numpy array that contains the velocities of the particle.
        One entry for dimention.
    '''
    def __init__(self, init_position, init_best, velocity) -> None:
        self.current_position = init_position
        self.current_position_cost = init_best
        self.best_position = init_position
        self.best_position_cost = init_best
        self.velocity = velocity

    '''
    Method to update the velocity of the particle.
    Params: 
        - c1, c2: social coeficients of the swarm.
        - w: Constant to control the flying speed.
        - best: the best position found by the swarm.
    '''
    def update_velocity(self, c1,c2,w,best):
        r1 = random()
        r2 = random()
        self.velocity = w*self.velocity + c1*r1*(self.best_position-self.current_position) + c2*r2*(best-self.current_position)

    '''
    Method to update the position of the particle.
    Params: 
        - function: the cost function.
    '''
    def update_position(self,function):
        self.current_position = self.current_position + self.velocity
        self.current_position_cost = function(self.current_position)
        if(self.current_position_cost < self.best_position_cost):
            self.best_position = self.current_position
            self.best_position_cost = self.current_position_cost

'''
Class Swarm.
A swarm is a list of particles.
The particles in the swarm are capable of identifying the best particle
in the swarm.
'''
class Swarm():
    '''
    The constructor of the class.
    '''
    def __init__(self) -> None:
        self.particles = list()

    '''
    Method to add a particle to the swarm.
    Params: 
        - particle: object of type particle that contains the particle to
        be appended to the particles list.
    '''
    def add_particle(self,particle):
        self.particles.append(particle)

    '''
    Method to get the best position of the swarm.
    Return: 
        - best_pos: a numpy array with the best position
        of the swarm
    '''
    def get_gbest(self):
        best_cost = self.particles[0].best_position_cost
        best_pos = self.particles[0].best_position
        for i in range(0,len(self.particles)):
            if(self.particles[i].best_position_cost < best_cost):
                best_cost = self.particles[i].best_position_cost
                best_pos = self.particles[i].best_position
        return best_pos

'''
Class PSO.
Class to run the particle swarm optimization with respect of the
given function.
'''
class PSO():
    '''
    The constructor of the class.
    Params: 
        - num_particles:  The number of particles in the swarm.
        - num_params: The number of dimentions of the objective function.
        - interval: An interval to grab the intial postion of the particles.
        - function: The objective function
    '''
    def __init__(self,num_particles,num_params, interval, function) -> None:
        self.swarm = Swarm()
        self.dimentions = num_params
        self.function = function
        for _ in range(num_particles):
            current_pos = np.array([uniform(interval[0],interval[1]) for _ in range(0,num_params)])
            current_best = function(current_pos)
            self.swarm.add_particle(Particle(current_pos,current_best,np.array([random() for _ in range(0,num_params)])))
    '''
    Method to run the PSO heuristic over the objective function.
    Params: 
        - c1, c2: social coeficients of the swarm.
        - w: Constant to control the flying speed.
        - num_iteration: The number of the iterations for the PSO heuristic.
    Return: 
        - self.swarm.get_gbest(): The best solution found by the swarm.
    '''
    def run(self,w,c1,c2, num_iterations):
        for _ in range(0, num_iterations):
            for particle in self.swarm.particles:
                particle.update_position(self.function)
                bestPosition = self.swarm.get_gbest()
                particle.update_velocity(c1,c2,w, bestPosition)
        return self.swarm.get_gbest()

#fx = lambda x : (x[0]**2 + x[1] - 11)**2 + (x[0] + x[1]**2 -7)**2
#pso = PSO(num_particles=20,num_params=2, interval=[-5,5], function=fx)
#pso.run(w=0.4,c1=0.1,c2=0.1, num_iterations=100)