'''
To build a deep neural network instance with the following features:
-> x input neurons
-> w hidden layers of z neurons each
-> y output neurons

Every activation is present on the simulation tape, so for the above described architecture:
-> number of parameters: x * z * ( z**(w - 1) ) * z * y + z * w + y 
-> number of activations including the input and the output: x + z * w + y

- The tape will have 32 bit 'symbols' each of which (when not a delimiter) will hold a floating point number.
- The number of such symbols will be equal to the total number of activations in the deep neural network.

Therefore the number of cells on the simulation tape will be equal to 2 * (x + z * w + y) + 1

But to actually simulate this using a Turing machine, let us define a set of rules and conventions we will be following:
1. If there are 10 layers, we will create 10 tapes, one for each layer.
2. Each symbol is no longer a single bit as that would increase the complexity of the machine and make it 'un-simulatable'.
3. Each symbol on the tape is now a neuron's activation value.
4. The parameters are stored in a dictionary which is conveniently structured so as to allow for easier parametric forward passes

'''

import random

class deep_neural_network_turing_machine():
    def __init__(
        self,
        input_neurons: int,
        hidden_layers: int,
        hidden_neuron_count: int,
        output_neurons: int,
        params: dict = None
    ):
        self.blank = 'b'
        self.input_neurons = input_neurons
        self.hidden_layers = hidden_layers
        self.hidden_neuron_count = hidden_neuron_count
        self.output_neurons = output_neurons
        self.tapes_count = hidden_layers + 2 
        self.tapes = {i: [] for i in range(self.tapes_count)}
        self._init_tapes()
        self.layers = hidden_layers + 2
        self.parameters = self._initialize_parameters() if params is None else params
        self.states = set(f"q{i}" for i in range((self.layers) + 1))
        self.final_state = f'q{(self.layers)}'

    def relu(self, x):
        return max(0, x)

    def _init_tapes(self):
        for i in range(self.tapes_count):
            if i == 0:
                self.tapes[i] = [0.0 for _ in range(self.input_neurons)] + [self.blank]
            elif i == self.tapes_count - 1:
                self.tapes[i] = [0.0 for _ in range(self.output_neurons)] + [self.blank]
            else:
                self.tapes[i] = [0.0 for _ in range(self.hidden_neuron_count)] + [self.blank]

    def _initialize_parameters(self):
        weights = {}
        biases = {}
        for layer in range(self.tapes_count - 1):
            in_size = self.input_neurons if layer == 0 else self.hidden_neuron_count
            out_size = self.output_neurons if layer == self.tapes_count - 2 else self.hidden_neuron_count

            weights[f"layer{layer}"] = {
                f"neuron{j}": [random.uniform(-1, 1) for _ in range(in_size)]
                for j in range(out_size)
            }
            biases[f"layer{layer}"] = {
                f"neuron{j}": random.uniform(-1, 1)
                for j in range(out_size)
            }

        return {'weights': weights, 'biases': biases}

    def _tapify(self):
        for idx, tape in enumerate(self.tapes):
            self.tapes[idx].insert(0, 'b')

    def forward(self, x):
        '''
        This is the pseudo transition function for this module, not an actual transition function as seen in normal Turing machines
        '''
        assert len(x) == self.input_neurons, f"Expected size: {self.input_neurons}, got {len(x)}"
        state = 'q0'
        
        for i in range(len(x)):
            self.tapes[0][i] = x[i]

        for layer in range(self.tapes_count - 1):

            input_activations = self.tapes[layer][:-1]
            output_activations = []

            layer_weights = self.parameters['weights'][f"layer{layer}"]
            layer_biases = self.parameters['biases'][f"layer{layer}"]

            for neuron_idx, weights in layer_weights.items():
            
                weighted_sum = sum(
                    w * inp for w, inp in zip(weights, input_activations)
                )
            
                weighted_sum += layer_biases[neuron_idx]
                output_activations.append(self.relu(weighted_sum))

            for i in range(len(output_activations)):
                self.tapes[layer + 1][i] = output_activations[i]
                
            state = f'q{(1 + int(state[1:]))}'
        
        state = f'q{(1 + int(state[1:]))}'

        assert self.final_state == state; f"Invalid Transitions encountered"
        self._tapify()
        return self.tapes