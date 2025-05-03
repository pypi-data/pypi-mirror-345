'''
Alphabet: A finite non-empty set of symbols.
Examples:
- Σ = {0, 1} is the binary alphabet
- Σ = {a, b, · · · , z} 

String: A finite sequence of symbols chosen from some arbitary Alphabet. 
Examples: 
- 010010 over the alphabet {0, 1}
- 567657667 over the alphabet {5, 6, 7}

This module subtly supports the use of custom alphabets.
To define your own alphabet and use it in the Turing machine instance, simply define a deterministic transition function that  

Note that all your states are numbered from 0 to n - 1, where n is the number of states you wish to have. Following standard convention, there shall only ever be only one start state for every Turing machine.


Integrated module to create single tape Turing machines. 
Incorporated a decider to decide if the machine halts based on the code and logic in halt.py  

Usage:
Example instance: machine = single_tape_turing_machine(number_of_states, delta, start_state, final_states)
- The input from the instantiated module is of the following form:
1. The first input to the created instance is the total number of states in the Turing machine

2. The transition function must be written out as a dictionary taking the form:
    transition_function = {
        ...
        ...
        ('q0', 'X'):('q2', 'Y', 1),
        ...
        ...
    }

    in the above given example:
    - 'q0' is the current state
    - 'Z is the symbol read on the tape.
    - 'q2' is the state to transition to
    - 'Y is the symbol to write on the tape
    - 1 for transitioning to the right and -1 for transitioning to the left

3. The initial state is passed simply as an integer. Example: 1 if q1 is the start state

4. If the final states are q2, q3, q4 then the 'final_states' parameter must be passed the argument '234'.

5. The input to the created instance is a string. Example: '0100101001' 

6. Finally call machine.simulation(input_string) to run the machine on input = input_string
'''

class single_tape_turing_machine:

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

    def __repr__(self):
        return f"{self.states, self.delta_func, self.start_state, self.final_states}"

    def _simulation_helper(self, qcurr, id):
        
        read_symbol = str(self.tape[id])
        (qout, write_symbol, move) = self.delta_func[(qcurr, read_symbol)]
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
    
    def _add_input(self, x):
        
        self.tape.pop()
        
        for i in range(len(x)):
            self.tape.append((x[i]))
            
        self.tape.append('b')

    def simulation(self, x):
        
        qcurr = self.start_state
        id = 1
        self._add_input(x)
        
        while(1):

            (id, qcurr) = self._simulation_helper(qcurr, id)
            
            if self.halt_counter > 50: break
            if qcurr in self.final_states: break            
            
        print(self.tape)
