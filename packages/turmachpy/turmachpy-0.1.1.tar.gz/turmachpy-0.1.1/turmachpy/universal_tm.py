'''
The universal Turing machine is a Turing machine that can run and simulate any other Turing machine, including itself.
To run these Turing machines on some input, the following conventions are followed:
- The Universal Turing machine is a 3-tape Turing machine.
- The binary machine of the Turing machine to be simulated using the UTM and the input to be simulated are present on the first tape.
- The current state of the machine, if qx, is denoted by the string of 'x + 1' number of zeros. This is written on the second tape.
- The third tape is used to actually simulate the Turing machine being simulated. This tape initially holds the input to the machine needing simulation.

Simulation:
- The input from the third tape is read symbol by symbol. Similarly the state is read from the second tape.
- A relevant transition is searched for in the 1st tape, if found, the transition is simulated.
- Changes in the symbol and state are then made.
- Re-do the same until we reach the halting state.

Usage:
Refer universal_tm_example.py
'''
from turmachpy.multi_tape_tm import multi_tape_turing_machine
from turmachpy.binary_encoding import binary_encoding

class universal_turing_machine(multi_tape_turing_machine):
    
    def __init__(
            self,
            states_count: int,
            delta_func: dict,
            start_state: int,
            final_states: str,
            tapes_count: int, 
            input_str: str,
            machine: str
            ):
            
        super().__init__(states_count, delta_func, start_state, final_states, tapes_count)
        
        self.tracker = 1
        self.machine = machine
        self.states_count = states_count
        self.delta_len = len(list(delta_func.items()))
        
        for i in range(self.tapes_count):
            self.tapes[i].pop() 
            
        for i in machine:
            self.tapes[0].append(i)
            
        self.tapes[1].append('0')
        
        for i in input_str:
            self.tapes[2].append(i)
            
        for i in range(self.tapes_count):
            self.tapes[i].append('b')
    
    def _check_transition(self, start_index, end_index):
        
        parts = self.machine[start_index : end_index].split('1')
        if len(parts) != 5: return 0
        
        len_parts = [len(parts[i]) for i in range(len(parts))]
        
        if len_parts[0] <= 0 or len_parts[0] > self.states_count: return 0
        if len_parts[1] not in [1, 2, 3]: return 0
        if len_parts[2] <= 0 or len_parts[2] > self.states_count: return 0
        if len_parts[3] not in [1, 2, 3]: return 0
        if len_parts[4] not in [1, 2]: return 0
        
        return 1
    
    def _check_validity(self):
        '''
        To check validity: 
        1. First check if every transition is separated by '11'
        2. Only after that check if each individual transition is valid
        '''
        # Overall check:
        # 1. Check if the machine starts and ends with '111'
        # 2. Then check if every transition is separated by '11'
        
        if self.machine[:3] != '111' or self.machine[-3:] != '111' or self.machine[:4] == '1111' or self.machine[-4:] == '1111': return 0
        
        parts = self.machine[3:-3].split('11')
        if len(parts) != self.delta_len: return 0

        # Now check if the individual transitions are valid
        start_index =  self.machine.find('111')
        end_index = self.machine[start_index + 3 :].find('11')
        end_index += start_index + 3
        
        while(1):
            
            if self.machine[start_index + 2] == '1':
                if self._check_transition(start_index + 3, end_index - 1):
                    start_index = end_index
                    continue
                else:
                    return 0
                    
            end_index = self.machine[start_index + 2:].find('11')
            end_index += start_index + 2
            
            if self._check_transition(start_index + 2, end_index) == 0:
                return 0
                
            if self.machine[end_index + 2] != '1':
                start_index = end_index
                
            else:
                return 1

    def _get_transition(self, qcurr, read_symbol):
        
        decoded_qcurr = ''.join('0' for _ in range(int(qcurr[1]) + 1))
        
        if read_symbol == '0':
            decoded_read_symbol = '0'
            
        elif read_symbol == '1':
            decoded_read_symbol = '00'
            
        else:
            decoded_read_symbol = '000'
            
        search_string = '11' + decoded_qcurr + '1' + decoded_read_symbol + '1'
        start_index = self.machine.find(search_string)
        start_index += len(search_string)
        
        search_end_index = self.machine[start_index : -1].find('11')
        search_end_index += start_index
        transition_string = self.machine[start_index : search_end_index]
        
        parts = transition_string.split('1')
        assert len(parts) == 3, f"Logic Error"
        
        qnext = f"q{len(parts[0]) - 1}"
        if parts[1] == '0':
            write_symbol = '0'
            
        elif parts[1] == '00':
            write_symbol = '1'
            
        else:
            write_symbol = 'b'    
            
        if parts[2] == '0':
            move = -1
            
        else: 
            move = 1    
            
        return (qnext, write_symbol, move)

    def _utm_simulation_helper(self, qcurr):
        
        read_symbol = self.tapes[2][self.tracker]
        (qnext, write_symbol, move) = self._get_transition(qcurr, read_symbol)
        self.tapes[2][self.tracker] = write_symbol
        
        if self.tracker + move < -1:
            self.halt_counter += 1
            self.tapes[2].insert(0, 'b')
            
        if self.tracker + move >= len(self.tapes[2]):
            self.halt_counter += 1
            self.tapes[2].insert(0, 'b')
            
        if self.tracker + move > -1 and self.tracker + move < len(self.tapes[2]):
            self.halt_counter = 0 
            
        return (self.tracker + move, qnext)

    def utm_simulation(self):
        
        if not self._check_validity(): return print("Invalid Encoding")
        
        while(1):
            qcurr = f'q{len(self.tapes[1]) - 3}'
            
            for _ in range(len(self.tapes[1]) - 1):
                self.tapes[1].pop()
                
            (self.tracker, qcurr) = self._utm_simulation_helper(qcurr)
            
            for _ in range(int(qcurr[1]) + 1):
                self.tapes[1].append(0)

            self.tapes[1].append('b')
            
            if self.halt_counter > 50: break
            
            if qcurr in self.final_states: break            
            
        print(self.tapes)