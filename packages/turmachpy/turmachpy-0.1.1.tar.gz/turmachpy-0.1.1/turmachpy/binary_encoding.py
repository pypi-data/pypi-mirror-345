'''
The Binary Encoding for a Turing machines is an encoding which follows a set of rules to encode any Turing machine as a binary string.

The following are the conventions and the rules adhered to when encoding a Turing machine:
1. For a Turing machine M = (Q, Σ, Γ, δ, q1, B, F) | Q = {q1, · · · , qn} | Σ = {0, 1} | Γ = {0, 1, B} | q1 = initial state | Transition function : δ(qi, Xj) = (qk, Xl, L/R) 

2. Each transition in the transition function is encoded as the following binary string: (0^i)1(0^j)1(0^k)1(0^l)1(0^m)

3. Every transition is separated from the other one by using '11'. 'm11n11o11p' where m, n, o, p are binary strings encoding distinct transitions

4. The value of 'i' and 'k' should be between 1 and n (total number of states)

5. X1 = 0, X2 = 1, X3 = B | The value of 'j' and 'l' should be between 1 and 3

6. A move to the left can be encodoed as one 0 and a move to the right can be encoded as two 0's

7. In the Universal Turing machine, every Turing machine's encoding is technically solely defined by it's transition function, so to separate the Turing machines from each other, we use '111'. Example: 'mach111machn111mache' where mach, mache, machn are Turing machines

'''
from turmachpy.single_tape_tm import single_tape_turing_machine

class binary_encoding(single_tape_turing_machine):
    def __init__(
            self, 
            states_count: int, 
            delta_func: dict, 
            start_state: int, 
            final_states: str
            ):
            
        super().__init__(states_count, delta_func, start_state, final_states)
        
        self.states_count = states_count
        self.encoding = ''
        self.delta_len = len(list(delta_func.items()))

    def encode_machine(self):
        
        self.encoding += '111'
        
        for i, ((qcurr, read_symbol), (qnext, write_symbol, move)) in enumerate(self.delta_func.items()):
            self.encoding += ''.join('0' for _ in range(int(qcurr[1]) + 1))
            self.encoding += '1'
            
            if read_symbol == '0':
                self.encoding += '0'
                
            elif read_symbol == '1':
                self.encoding += '00'
                
            elif read_symbol == 'b':
                self.encoding += '000'    
                
            self.encoding += '1'
            self.encoding += ''.join('0' for _ in range(int(qnext[1]) + 1))
            self.encoding += '1'
            
            if write_symbol == '0':
                self.encoding += '0'
                
            elif write_symbol == '1':
                self.encoding += '00'
                
            elif write_symbol == 'b':
                self.encoding += '000'    
                
            self.encoding += '1'
            self.encoding += '0' if move == -1 else '00'
            
            if i != self.delta_len - 1:
                self.encoding += '11'
                
        self.encoding += '111'
    
    def _check_transition(self, start_index, end_index):
        
        parts = self.encoding[start_index : end_index].split('1')
        if len(parts) != 5: return 0
        len_parts = [len(parts[i]) for i in range(len(parts))]
        
        if len_parts[0] <= 0 or len_parts[0] > self.states_count: return 0
        if len_parts[1] not in [1, 2, 3]: return 0
        if len_parts[2] <= 0 or len_parts[2] > self.states_count: return 0
        if len_parts[3] not in [1, 2, 3]: return 0
        if len_parts[4] not in [1, 2]: return 0
        
        return 1
    
    def check_validity(self):
        '''
        To check validity: 
        1. First check if every transition is separated by '11'
        2. Only after that check if each individual transition is valid
        '''
        # Overall check:
        # 1. Check if the machine starts and ends with '111'
        # 2. Then check if every transition is separated by '11'
        
        if self.encoding[:3] != '111' or self.encoding[-3:] != '111' or self.encoding[:4] == '1111' or self.encoding[-4:] == '1111': return 0
        
        parts = self.encoding[3:-3].split('11')
        if len(parts) != self.delta_len: return 0

        # Now check if the individual transitions are valid
        start_index =  self.encoding.find('111')
        end_index = self.encoding[start_index + 3 :].find('11')
        end_index += start_index + 3
        
        while(1):
            
            if self.encoding[start_index + 2] == '1':
                if self._check_transition(start_index + 3, end_index - 1):
                    start_index = end_index
                    continue
                else:
                    return 0
                    
            end_index = self.encoding[start_index + 2:].find('11')
            end_index += start_index + 2
            
            if self._check_transition(start_index + 2, end_index) == 0:
                return 0
                
            if self.encoding[end_index + 2] != '1':
                start_index = end_index
                
            else:
                return 1