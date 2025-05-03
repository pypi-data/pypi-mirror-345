'''
A grid-tape Turing machine is a 2-dimensional Turing machine.
These machines can not only move left or right but also up or down over a grid like tape.

As mentioned in the halting_decider module, the machine is assumed to never halt if it continues to remain in the same state for more than 50 steps.
'''

class grid_tape_turing_machine:

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
        
        self.grid_tape = [[self.blank, self.blank], [self.blank], [self.blank, self.blank]]
        self.halt_counter = 0
        
        self.grid = {
            'start': 0,  
            'end' : 2
        }

    def __repr__(self):
        return f"{self.states, self.delta_func, self.start_state, self.final_states}"

    def _simulation_helper(self, qcurr, id, tcurr):
        
        read_symbol = self.grid_tape[tcurr][id]
        (qout, write_symbol, move) = self.delta_func[(qcurr, read_symbol)]
        self.grid_tape[tcurr][id] = write_symbol
        
        if move == 'u':
            return (id, qout, tcurr + 1)
            
        elif move == 'd':
            return (id, qout, tcurr - 1)
            
        else:
            
            if move == 'l': move = -1
            
            if move == 'r': move = 1 
            
            if id + move < -1 :
                
                self.halt_counter += 1
                
                for i in range(len(self.grid_tape)):
                    self.grid_tape[i].insert(0, 'b')
                    
            if id + move >= len(self.grid_tape[0]):
                
                self.halt_counter += 1
                
                for i in range(len(self.grid_tape[0])):
                    self.grid_tape[i].append('b')
                    
            if id + move > -1 and id + move < len(self.grid_tape[0]):
                self.halt_counter = 0
                
            return (id + move, qout, tcurr)
    
    def _add_input(self, x):
        
        for i in range(len(x)):
            self.grid_tape[0].append('b')
            self.grid_tape[1].append(x[i])
            self.grid_tape[2].append('b')
            
        self.grid_tape[1].append('b')

    def simulation(self, x):
        
        qcurr = self.start_state
        tcurr = 1 # tcurr is used to keep track of which track we're currently operating on.
        id = 1
        
        self._add_input(x)
        
        while(1):
            (id, qcurr, tcurr) = self._simulation_helper(qcurr, id, tcurr)
            
            if self.grid['start'] > tcurr - 1:
                
                self.grid_tape.append(['b' for _ in range(len(self.grid_tape[0]))])
                tcurr = 0
                self.grid['end'] += 1
                
            if self.grid['end'] < tcurr + 1:
                
                self.grid_tape.insert(0, ['b' for _ in range(len(self.grid_tape[0]))])
                self.grid['end'] += 1
                
            if self.halt_counter > 50: break
            
            if qcurr in self.final_states: break            
            
        for i in range(len(self.grid_tape)):
            print(self.grid_tape[i])