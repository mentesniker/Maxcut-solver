import qiskit.quantum_info as qi
import numpy as np
from qiskit import QuantumCircuit, Aer, execute
from qiskit.circuit import Parameter
from scipy.optimize import minimize
from BA import BA
from PSO import PSO
from ACO import ACO
from ABC import ABC
from numpy import pi 
'''
Class MaxCutSolver.
A class that is commited to solve a max cut instance problem.
'''
class MaxCutSolver():
        
    '''
    The constructor of the class.
    Params: 
        - graph: The graph of which we want the max cut.
        - num_qubits: The number of qubits needed.
        - backend: The back for running the experiments.
        - p (optinal): The p value for the QAOA
    '''
    def __init__(self, graph, num_qubits, backend, p = 1):
        self.graph = graph
        self.numqubits = num_qubits
        self.circuit = QuantumCircuit(num_qubits)
        self.backend = backend
        self.p = p
        for i in range(0,  self.numqubits):
            self.circuit.h(i)
        gamma = [Parameter("gamma" + str(i)) for i in range(0,p)]
        beta = [Parameter("beta" + str(i)) for i in range(0,p)]
        for j in range(0, p):
            for nodes in list(graph.edges()): 
                self.circuit.rzz(2 * gamma[j], nodes[0], nodes[1])
            for i in range(0,  self.numqubits):
                self.circuit.rx(2 * beta[j], i)

    '''
    Method to get the cost of a cut.
    Params: 
        - bitstring: The cut of the graph.
    Returns:
        - float: the cost of the cut
    '''
    def get_cost_graph(self, bitstring):
        cost = 0
        for i, j in self.graph.edges():
            if bitstring[i] != bitstring[j]:
                cost -= 1
        return cost

    '''
    Method that applies a measurement and executes the class circuit 
    using the parameters passed as a parameter.
    Params: 
        - params: a list that contains the parameters
        for the circuit.
    Returns:
        - dict: a python dict that contains the counts of 
        the execution.
    '''
    def output_circuit(self, params):
        backend = Aer.get_backend(self.backend)
        backend.shots = 1000
        qc_res = self.circuit.copy()
        qc_res = qc_res.bind_parameters(params)
        if (self.backend == 'statevector_simulator'):
            result = qi.Statevector.from_instruction(qc_res).probabilities_dict()
            return result
        else:
            qc_res.measure_all()
            counts = backend.run(qc_res).result().get_counts()
            return counts

    '''
    Method that gets the average value of the execution
    of the class circuit.
    Params: 
        - params: a list that contains the parameters
        for the circuit.
    Returns:
        - float: the average value of the excution.
    '''
    def get_expectation(self, params):
        backend = Aer.get_backend(self.backend)
        qc = self.circuit.copy()
        qc = qc.bind_parameters(params)

        if (self.backend == 'qasm_simulator'):
            qc.measure_all()
            counts = execute(qc, nshots=1000, backend=backend).result().get_counts()
        else:
            counts = qi.Statevector.from_instruction(qc).probabilities_dict()
        avg = 0
        sum_count = 0
        for bitstring, count in counts.items():
            obj = self.get_cost_graph(bitstring)
            avg += obj * count
            sum_count += count
        return avg/sum_count
        
    '''
    Method that gets the optimal values for the parameters
    of the class circuit using the COBYLA optimizer.
    Params: 
        - init_point: the initial point for the cobyla
        optimizer.
    Returns:
        - list: a python list that contains the optimal values.
    '''
    def optimize_classic(self, method, init_point = None):
        #def first_guess_linear(n):
        #    theta = [random.uniform(0, pi) for _ in range(0,n)] + [random.uniform(0, 2*pi) for _ in range(0,n)]
        #    return (theta)
        def first_guess_linear(p,m1=0.5,m2=0.5):
            theta=np.zeros([2*p])
            for i in range(2*p):
                if i % 2 ==0:
                    theta[i]=m1*(i+1)/(2*p)
                else:
                    theta[i]=m2*(2*p-i)/(2*p)
            return(theta)
        def x_ungerade(i,p):# for odd angles (gamma's)
            return (i+0.5)/p
            #return (i+0.25)/(p-0.75)   # unclear what is the best choice for x_i
        def x_gerade(i,p): # for even angles (beta's)
            return (i+0.5)/p
            #return i/p  # unclear what is the best choice for x_i
        def extrapolate(theta):
            p=len(theta)//2+1
            if p<=2: # Extrapolation only makes sense for p>2. Otherwise, take linear guess
                return(first_guess_linear(p))
            else:
                theta2=np.zeros([2*p])
                for i in range(2*p):
                    if i % 2 == 0:
                        x_func = x_ungerade
                        j=0
                    else:
                        x_func = x_gerade
                        j=1
                    x=x_func(i//2,p)
                    while x_func(j//2 +1,p-1)<x:
                        j+=2
                    while j//2>p-3:
                        j-=2
                    x1=x_func(j//2,p-1)
                    x2=x_func(j//2+1,p-1)
                    y1=theta[j]
                    y2=theta[j+2]
                    theta2[i]=((y1-y2)*x+x1*y2-y1*x2)/(x1-x2)
                    i+=1
            return(theta2)
        expectation = self.get_expectation
        if(not init_point):
            theta=[]
            for _ in range(1,self.p+1):
                theta = extrapolate(theta)
            init_point = theta
        res = minimize(expectation, init_point, method=method)
        return res

    '''
    Method that gets the optimal values for the parameters
    of the class circuit using the PSO optimizer.
    Params: 
        - interval: the interval to initialize each coordinate of the initial point
        of the particles.
        - dimentions: the number of parameters for the optimizer to optimize.
    Returns:
        - list: a python list that contains the optimal values.
    '''
    def optimize_swarm(self, interval):
        expectation = self.get_expectation
        pso =  PSO(num_particles=20, num_params=self.p*2, interval=interval, function=expectation)
        return pso.run(w=0.4,c1=0.1,c2=0.1, num_iterations=50)


    '''
    Method that gets the optimal values for the parameters
    of the class circuit using the PSO optimizer.
    Params: 
        - interval: the interval to initialize each coordinate of the initial point
        of the particles.
        - dimentions: the number of parameters for the optimizer to optimize.
    Returns:
        - list: a python list that contains the optimal values.
    '''
    def optimize_bees(self, interval):
        expectation = self.get_expectation
        abc =  ABC(dimention=self.p*2, num_points=30, bonds=interval, numlookers=15, fx=expectation)
        return abc.run(num_iterations=50, limit=15, a=pi)


    '''
    Method that gets the optimal values for the parameters
    of the class circuit using the BA optimizer.
    Params: 
        - interval: the interval to initialize each coordinate of the initial point
        of the bats.
        - dimentions: the number of parameters for the optimizer to optimize.
    Returns:
        - list: a python list that contains the optimal values.
    '''
    def optimize_bats(self, interval):
        expectation = self.get_expectation
        ba = BA(number_of_bats=20, num_dimentions=self.p*2, interval=interval, number_of_iterations=50, alfa= 0.9, gamma=0.9)
        return ba.run(expectation)

    '''
    Method that gets the optimal values for the parameters
    of the class circuit using the ACO optimizer.
    Params: 
        - interval: the interval to initialize each coordinate of the initial point
        of the ants.
        - dimentions: the number of parameters for the optimizer to optimize.
    Returns:
        - list: a python list that contains the optimal values.
    '''
    def optimize_ants(self, interval):
        expectation = self.get_expectation
        aco = ACO(num_params=self.p*2,discrete_points=200,interval=interval,
        number_ants=20,q=0.5, evaporation_rate=0.9, num_iterations = 10)
        return aco.run(expectation)
        