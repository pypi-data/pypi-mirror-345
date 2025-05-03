'''
Turing machines in general are assumed to be detereministic, meaning that there exists a transition for every state over every symbol in the alphabet.
In this module we explore non-deterministic Turing machines, wherein we may have more than one possible transition for each state over every symbol.

To reach the halting state, the idea is simple:
-> A tree of states over symbolic transitions is created and this tree is explored level by level using the Breadth-first search algorithm.
-> For each level in the generated tree, we simulate the transitions up until that particular node and check if the current state is the halting state, if it isn't we keep exploring.

Usage: 
Refer non_deterministic_tm_example.py
'''
class non_deterministic_turing_machine:

    def __init__(
            self, 
            states_count: int, 
            delta_func: dict, 
            start_state: int, 
            final_states: str
            ):
            
        assert type(delta_func) == dict; f"Invalid type for the transition function"
        
        self.states = set(f'q{i}' for i in range(states_count))
        self.delta_func = delta_func
        self.start_state = f'q{start_state}'
        self.final_states = [f'q{final_states[i]}' for i in range(len(final_states))]
        self.blank = 'b'
        
        self.tape = [self.blank, self.blank]
        self.halt_counter = 0
        self.queue = []

    def __repr__(self):
        return f"{self.states, self.delta_func, self.start_state, self.final_states}"

    def simulation_helper(self, id: int):
        
        (qout, write_symbol, move) = self.queue.pop()
        self.tape[id] = write_symbol
        
        if id + move < -1 :
            self.halt_counter += 1
            self.tape.insert(0, 'b')
            
        if id + move >= len(self.tape):
            self.halt_counter += 1
            self.tape.insert(0, 'b')
            
        if id + move > -1 and id + move < len(self.tape):
            self.halt_counter = 0 
            
        return (id + move, qout)
    
    def add_input(self, x):
        
        self.tape.pop()
        for i in range(len(x)):
            self.tape.append(x[i])
            
        self.tape.append('b')

    def simulation(self, x):
        
        qcurr = self.start_state
        id = 1
        self.add_input(x)

        while(1):
            self.queue.extend(self.delta_func[(qcurr, self.tape[id])])
            (id, qcurr) = self.simulation_helper(id)

            if self.halt_counter > 50: break
            
            if qcurr in self.final_states: break            

        print(self.tape)