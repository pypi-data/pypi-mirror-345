'''
Read from the safetensors file itself to store on a tape. Note that to use this module you have to first download the model weights from huggingface
'''
import tiktoken
import numpy as np
from safetensors import safe_open

class tape_desc:
    def __init__(self, token_id, position):
        self.token_id = token_id
        self.position = position
        self.embedding = None
        self.layer_data = {}

class gpt_turing_machine:

    def __init__(self, model_path="model/model.safetensors"):
    
        self.tokenizer = tiktoken.get_encoding("gpt2")
        self.params = {}
        
        with safe_open(model_path, framework="np") as f:
            for key in f.keys():
                self.params[key] = f.get_tensor(key)

        # Config data            
        self.n_heads = 12
        self.embed_dim = 768
        self.head_dim = self.embed_dim // self.n_heads

    def _compute_embeddings(self, tape):
        
        for cell in tape:
        
            wte = self.params["wte.weight"][cell.token_id]
            wpe = self.params["wpe.weight"][cell.position]
            cell.embedding = wte + wpe

    def _layer_norm(self, x, gain, bias, eps=1e-5):

        mean = np.mean(x, axis=-1, keepdims=True)
        variance = np.var(x, axis=-1, keepdims=True)
        
        x = (x - mean) / np.sqrt(variance + eps)
        return gain * x + bias

    def _attention(self, tape, layer_idx):

        for cell in tape:
        
            weight = self.params[f"h.{layer_idx}.attn.c_attn.weight"]
            bias = self.params[f"h.{layer_idx}.attn.c_attn.bias"]
            qkv = cell.embedding @ weight + bias
        
            q, k, v = np.split(qkv, 3)
            q = q.reshape(self.n_heads, self.head_dim)
            k = k.reshape(self.n_heads, self.head_dim)
            v = v.reshape(self.n_heads, self.head_dim)
        
            cell.layer_data.update({"q": q, "k": k, "v": v})

        for i, cell_i in enumerate(tape):

            attention_output = np.zeros(self.embed_dim)
            
            for head in range(self.n_heads):
            
                attn_scores = []
                for j, cell_j in enumerate(tape):
                    
                    if j > i:
                        score = -np.inf
                    
                    else:
                        q = cell_i.layer_data["q"][head]
                        k = cell_j.layer_data["k"][head]
                        score = q @ k / np.sqrt(self.head_dim)
                    
                    attn_scores.append(score)
                
                probs = np.exp(attn_scores - np.max(attn_scores))
                probs = probs / probs.sum()
                
                head_output = np.zeros(self.head_dim)
                
                for j, prob in enumerate(probs):
                
                    cell_j = tape[j]
                    v = cell_j.layer_data["v"][head]
                    head_output += prob * v
                
                attention_output[head*self.head_dim:(head+1)*self.head_dim] = head_output

            weight = self.params[f"h.{layer_idx}.attn.c_proj.weight"]
            bias = self.params[f"h.{layer_idx}.attn.c_proj.bias"]
            
            projected = attention_output @ weight.T + bias
            cell_i.embedding += projected
            
            cell_i.embedding = self._layer_norm(
                cell_i.embedding,
                self.params[f"h.{layer_idx}.ln_1.weight"],
                self.params[f"h.{layer_idx}.ln_1.bias"]
            )

    def _feed_forward(self, tape, layer_idx):
        
        for cell in tape:
        
            weight_fc = self.params[f"h.{layer_idx}.mlp.c_fc.weight"]
            bias_fc = self.params[f"h.{layer_idx}.mlp.c_fc.bias"]
            hidden = cell.embedding @ weight_fc + bias_fc 
            
            hidden = 0.5 * hidden * (1 + np.tanh(np.sqrt(2/np.pi) * (hidden + 0.044715 * hidden**3)))
            
            weight_proj = self.params[f"h.{layer_idx}.mlp.c_proj.weight"]
            bias_proj = self.params[f"h.{layer_idx}.mlp.c_proj.bias"]
            hidden = hidden @ weight_proj + bias_proj
            
            cell.embedding += hidden
            cell.embedding = self._layer_norm(
                cell.embedding,
                self.params[f"h.{layer_idx}.ln_2.weight"],
                self.params[f"h.{layer_idx}.ln_2.bias"]
            )

    def generate(self, prompt, max_new_tokens):
        
        tokens = self.tokenizer.encode(prompt)
        tape = [tape_desc(token_id, pos) for pos, token_id in enumerate(tokens)]
        
        self._compute_embeddings(tape)
        
        for layer_idx in range(12):
            self._attention(tape, layer_idx)
            self._feed_forward(tape, layer_idx)
        
        for _ in range(max_new_tokens):

            final_embedding = tape[-1].embedding
            final_embedding = self._layer_norm(
                final_embedding,
                self.params["ln_f.weight"],
                self.params["ln_f.bias"]
            )
            
            wte = self.params["wte.weight"]
            logits = final_embedding @ wte.T

            next_token = np.argmax(logits)
            new_cell = tape_desc(next_token, len(tape))
            tape.append(new_cell)
            
            self._compute_embeddings([new_cell])
            
            for layer_idx in range(12):
                self._attention(tape, layer_idx)
                self._feed_forward(tape, layer_idx)

        return self.tokenizer.decode([cell.token_id for cell in tape])