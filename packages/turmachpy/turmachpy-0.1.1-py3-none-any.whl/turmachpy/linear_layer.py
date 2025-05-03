'''
To implement a Linear layer of 'x' neurons that can be connected to other layers ('y' or 'z' neurons behind or ahead of it)

Usage:
linear_layer(in_features, out_features) 
-> in_features: number of neurons connected to this layer from the layer behind it
-> out_features: number of neurons connected to this layer from the layer ahead of it

To actually simulate this using a Turing machine, let us define a set of rules and conventions we will be following:
1. Each layer is a tape. This tape, if to be used, needs to be connected to other tapes(layers).
2. The transition function here is a pseudo TM transition function, there is no literal transition function.
3. The essence of the Turing machine is captured using the tapes instead.
'''

import random

class linear_layer:

    def __init__(self, w, b):
    
        self.w = w
        self.b = b

    def step(self, input_symbols):
        output_symbols = []
        for w_row, b in zip(self.w, self.b):
            result = sum(i * w for i, w in zip(input_symbols, w_row)) + b
            output_symbols.append(result)

        return output_symbols


class master_handler:

    def __init__(self, layers):

        self.blank = 'b'
        self.layers = layers
        self.params = self._init_params()
        self.network_states = self._init_network_states()

        self.states = set(f"q{i}" for i in range(len(self.layers) + 1))
        self.final_state = f'q{len(self.layers)}'


    def _init_params(self):

        params = {}
        for i, (in_ch, out_ch) in self.layers.items():

            w = [[random.uniform(-1, 1) for _ in range(in_ch)] for _ in range(out_ch)]
            b = [random.uniform(-1, 1) for _ in range(out_ch)]
            params[f"layer{i}"] = {"w": w, "b": b}

        return params

    def _init_network_states(self):

        states = []
        for i in range(len(self.layers)):
            
            layer_param = self.params[f"layer{i}"]
            layer_state = linear_layer(layer_param['w'], layer_param['b'])
            states.append(layer_state)

        return states

    def _tm_transform(self, tapes, tape):
        
        for indi in tapes:
            indi.insert(0, self.blank)
            indi.append(self.blank)

        return tapes, tape
     
    def handle_it(self, x):
        '''
        This is the pseudo transition function for this module, not an actual transition function as seen in normal Turing machines
        '''
        state = 'q0'
        tape = x
        tapes = [x]
        for i, net_state in enumerate(self.network_states):
            tape = net_state.step(tape) 
            state = f'q{(1 + int(state[1:]))}'
            tapes.append(tape)

        assert self.final_state == state; f"Invalid Transitions encountered"
        tapes, tape = self._tm_transform(tapes, tape)     
        return tapes, tape