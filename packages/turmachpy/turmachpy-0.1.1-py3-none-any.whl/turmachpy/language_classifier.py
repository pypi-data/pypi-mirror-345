'''
Alphabet: A finite non-empty set of symbols.
Examples:
- Σ = {0, 1} is the binary alphabet
- Σ = {a, b, · · · , z} 

String: A finite sequence of symbols chosen from some arbitary Alphabet. 
Examples: 
- 010010 over the alphabet {0, 1}
- 567657667 over the alphabet {5, 6, 7}

Σ^∗ = The set of all strings over an alphabet Σ.

Language: A set of strings each of which can be accepted by the Turing machine question. A formal language L, over the alphabet Σ, is a subset of Σ^∗.
Example: L = {01, 00, 10, 11} over Σ = {0, 1} 

Recurisvely Enumerable languages are languages that can be accepted by Turing machines, but if a string which isn't in that particular language is given as input, then the machine may halt and reject or loop forever.

Recursive languages are Recursively enumerable languages which halt on all strings that aren't a part of the language.

To check if a language is Recursive or RE but not recursive, we simply call the halt_decider from halt.py and simulate the user defined Turing machine over a randomly generated set of strings to assess the nature of the language.

The purpose of this module is to simply classify a language as Recursive or RE but not recursive. 
'''

from turmachpy.halt_decider import halt_decider

class language_classifier(halt_decider):
    def __init__(
            self, 
            states_count, 
            delta_func, 
            start_state, 
            final_states, 
            x
            ):
        super().__init__(states_count, delta_func, start_state, final_states, x)
        
    def classify(self, input_str):
        if self.decide(input_str): return "Recursive and Recursively Enumerable"
        else: return "Recursively Enumerable but not Recursive"