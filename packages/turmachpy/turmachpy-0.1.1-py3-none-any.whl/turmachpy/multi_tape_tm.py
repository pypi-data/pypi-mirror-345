'''
A Multi-tape Turing machine has multiple tapes over which the read/write head can move.
The transition function needs to be defined relevantly. 

Important Note: If you aren't sure of exactly how the machine you're simulating works, please define a deterministic transition function.
'''

class multi_tape_turing_machine:
    def __init__(
            self, 
            states_count: int, 
            delta_func: dict, 
            start_state: int, 
            final_states: str, 
            tapes_count: int
            ):
            
        assert type(delta_func) == dict; f"Invalid type for the transition function"
        
        self.states = set(f'q{i}' for i in range(states_count))
        self.delta_func = delta_func
        self.tapes_count = tapes_count
        self.start_state = f'q{start_state}'
        self.final_states = [f'q{final_states[i]}' for i in range(len(final_states))]
        self.blank = 'b'
        
        self.tapes = {i : [self.blank, self.blank] for i in range(self.tapes_count)}
        self.halt_counter = [0 for i in range(tapes_count)]

    def __repr__(self):
        return f"{self.states, self.delta_func, self.start_state, self.final_states}"

    def _simulation_helper(self, qcurr, ids):
        
        read_symbols = ''
        
        for i in range(self.tapes_count):
            read_symbols += self.tapes[i][ids[i]]
            
        input_tuple = [i for i in read_symbols]
        input_tuple.insert(0, qcurr)
        input_tuple = tuple(input_tuple)
        
        (qout, *params) = self.delta_func[input_tuple]
        write_symbols = tuple(params[:self.tapes_count])
        move_symbols = tuple(params[self.tapes_count:])
        
        for i in range(self.tapes_count):
            
            self.tapes[i][ids[i]] = write_symbols[i]
            
            if ids[i] + move_symbols[i] < -1 :
                self.halt_counter[i] += 1
                self.tapes[i].insert(0, 'b')
                
            if ids[i] + move_symbols[i] > -1 :
                self.halt_counter[i] = 0
                
            ids[i] = ids[i] + move_symbols[i] 
            
        return (ids + list(move_symbols), qout)
    
    def _add_input(self, x):
        
        for j in range(self.tapes_count):
            self.tapes[j].pop()
            
            for i in range(len(x)):
                self.tapes[j].append(x[i])
                
            self.tapes[j].append('b')

    def _infinitness(self):
        
        for i in range(self.tapes_count):
            
            if self.tapes[i][0] != 'b':
                self.tapes[i].insert(0, 'b')
                
            if self.tapes[i][-1] != 'b':
                self.tapes[i].append('b')

    def simulation(self, x):
        
        qcurr = self.start_state
        ids = [1 for _ in range(self.tapes_count)]
        self._add_input(x)
        
        while(1):
            
            (ids, qcurr) = self._simulation_helper(qcurr, ids)

            if max(self.halt_counter) > 50: break
            
            if qcurr in self.final_states: break
            
        self._infinitness()
        print(self.tapes)