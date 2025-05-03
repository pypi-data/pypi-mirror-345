'''
Given input to a Turing machine, will the machine halt?
Note that it is impossible to answer the above question and therefore the code below only checks if the input given is resulting in transitions that don't change the tape of the Turing machine at all for 'x' number of transitions.
Why is the above not sufficient to decide if the machine halts or not?
Let's say we design a Turing machine 'M' that halts only after 'x + 1' meaningless transitions, thereby voiding the credibility of the code below.
'''

from turmachpy.single_tape_tm import single_tape_turing_machine

class halt_decider(single_tape_turing_machine):
    
    def __init__(
            self,  states_count: int,
            delta_func: dict,
            start_state: int,
            final_states: int,
            x: int
            ):
        super().__init__(states_count, delta_func, start_state, final_states)
        self.x = x
        self.halted = 0

    def decide(self, input_str):
        qcurr = self.start_state
        id = 1
        self._add_input(input_str)
        while(1):
            (id, qcurr) = self._simulation_helper(qcurr, id)
            if self.halt_counter > self.x:
                return f"Machine doesn't halt on input {input_str}"
            if qcurr in self.final_states: break 
        self.halted = 1
        return f"Machine Halts on input {input_str}"