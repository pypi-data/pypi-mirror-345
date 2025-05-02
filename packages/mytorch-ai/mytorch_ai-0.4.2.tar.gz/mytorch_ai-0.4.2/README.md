# MyTorch Preview Setup Guide

Thank you for registering for our MyTorch preview!

You should have received an access token in the email you provided at registration.
If you did not receive such a message, check your spam folder.
Contact [MyTorch.net support](https://mytorch.net/support) if you are having issues getting a mytorch token.

## Step 1: Setting Up

To use MyTorch, you will need to do the following:

1. Create a file named `~/.mytorch` in your home directory and add the line:
   ```
   token=yourmytorchtokenfromyouremail
   ```
   to that file. Modify the line above with your actual token, don't cut and paste.

2. To run the test in `./infer/llama3/infer_llama.py` you will need to follow the procedure described in the [HuggingFace.md](HuggingFace.md) 
   to request and receive a Hugging Face token to access the model weights.

> **Note:** We recommend running the following commands in this (`./examples`) directory

## Step 2: Installation
**IMPORTANT:** MyTorch replaces functions from libraries like PyTorch and Transformers with its own cloud-based implementations. For it to work properly, these libraries **must not** be pre-installed. If you’ve already installed them, create a fresh environment and install MyTorch **before** anything else. We recommend using `virtualenv` or `conda` to ensure a clean setup, even if you're unsure whether conflicts exist.

### Setting up MyTorch on Linux/MacOS

```bash
rm -rf venv_mytorch
python -m venv venv_mytorch
source venv_mytorch/bin/activate
pip install --upgrade pip
pip install --upgrade mytorch-ai
deactivate
```

### For Windows PowerShell

```powershell
Remove-Item -Recurse -Force venv_mytorch
python -m venv venv_mytorch
.\venv_mytorch\Scripts\Activate.ps1
pip install --upgrade pip
pip install --upgrade mytorch-ai
deactivate
```

### Setting up PyTorch Environment (for comparison)

#### For Linux/MacOS:

```bash
rm -rf venv_pytorch
python -m venv venv_pytorch
source venv_pytorch/bin/activate
pip install --upgrade pip
pip install -r pytorch_env_requirements.txt
deactivate
```

#### For Windows PowerShell:

```powershell
Remove-Item -Recurse -Force venv_pytorch
python -m venv venv_pytorch
.\venv_pytorch\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r pytorch_env_requirements.txt
deactivate
```

## Step 3: Running

Now you are ready to run examples...

1. Activate your venv environment of choice from Section 2.
2. Navigate to the example directory:

### Example 1: LLAMA-3.2-3B Inference

```bash
cd ./infer/llama
```

Read the [README.md](./infer/llama/README.md) in that directory for specific instructions.

## Step 4: Sample Output

### Output from running on myTorch servers:

```
(venv_mytorch) PS C:\Users\cenae\myTorch\myTorch_examples\infer\llama> python .\llama_infer.py
INFO - Client process is exiting; disconnecting from server...
INFO - Connecting to server proxy.mytorch.net:55551
*** Using GPU: Tesla P100-PCIE-16GB ***
Loading tokenizer for meta-llama/Llama-3.2-3B-Instruct...
INFO - Loading AutoTokenizer for `meta-llama/Llama-3.2-3B-Instruct`
INFO - ...AutoTokenizer has been loaded
Loading model for meta-llama/Llama-3.2-3B-Instruct...
INFO - Loading AutoModelForCausalLM model `meta-llama/Llama-3.2-3B-Instruct`
INFO - ...model has been loaded
Model loaded
Loading model onto cuda
Model moved to device
Tokenization complete

Generating response...

Prompt: Tell me a 500 word story about a black cat named George

Response:
]
George was a sleek and mysterious black cat with piercing green eyes that seemed to gleam in the dark. He had been a stray for as long as anyone could remember, but he never seemed to need anyone. He was a master of survival, able to scrounge up food and find shelter with ease.

Despite his tough exterior, George had a soft spot for humans. He would often sneak into homes and curl up in laps, purring contentedly as he basked in the warmth and attention. But he was a cat of discerning taste, and only sought out those who were willing to provide him with the finest treats and the most comfortable blankets.

One day, a young girl named Lily wandered into the neighborhood with her family. She was a shy and quiet child, with a mop of curly brown hair and a smile that could light up the darkest of rooms. As she explored the streets, she stumbled upon George lounging in a sunbeam, his eyes fixed intently on a nearby bird.       
Hi
Lily hesitated for a moment, unsure of what to do. But something about George's gentle demeanor put her at ease, and she reached out a hand to pet him. George purred loudly, nuzzling her hand with his head, and Lily felt a sense of calm wash over her.

From that moment on, George and Lily were inseparable. They spent their days exploring the neighborhood, chasing after butterflies, and curled up towatch the birds outside.

As the days turned into weeks, Lily's parents began to notice a change in their daughter. She seemed happier, more confident, and more at ease in her own skin. And whenever she looked into George's piercing green eyes, she felt a sense of peace and contentment wash over her.

One evening, as the sun set over the neighborhood, Lily snuggled up beside George on the couch. She stroked his soft fur, feeling the warmth of his body radiate into

Time taken: 26.29 seconds
INFO - Disconnecting from server...
INFO - Disconnected from server.
```

### Running locally:

```
C:\Users\cenae\myTorch\myTorch_examples\infer\llama> python .\llama_infer.py
INFO - Client process is exiting; disconnecting from server...
INFO - Connecting to server proxy.mytorch.net:55554
*** Using GPU: Tesla V100-DGXS-16GB ***
Loading tokenizer for meta-llama/Llama-3.2-3B-Instruct...
INFO - Loading AutoTokenizer for `meta-llama/Llama-3.2-3B-Instruct`
INFO - ...AutoTokenizer has been loaded
Loading model for meta-llama/Llama-3.2-3B-Instruct...
INFO - Loading AutoModelForCausalLM model `meta-llama/Llama-3.2-3B-Instruct`
INFO - ...model has been loaded
Model loaded
Loading model onto cuda
Model moved to device
Tokenization complete

Generating response...

Prompt: Tell me a 500 word story about a black cat named George

Response:
]
George was a sleek and mysterious black cat with piercing green eyes that seemed to gleam in the dark. He had been a stray for as long as anyone could remember, but he never seemed to need anyone. He was a master of survival, able to scrounge up food and find shelter with ease.

Despite his tough exterior, George had a soft spot for humans. He would often sneak into homes and curl up in laps, purring contentedly as he basked in the warmth and attention. But he was a cat of discerning taste, and only sought out those who were willing to provide him with the finest treats and the most comfortable blankets.

One day, a young girl named Lily wandered into the neighborhood with her family. She was a shy and quiet child, with a mop of curly brown hair and a smile that could light up the darkest of rooms. As she explored the streets, she stumbled upon George lounging in a sunbeam, his eyes fixed intently on a nearby bird.     

Lily gasped in wonder, her eyes locked onto George's piercing green gaze. For a moment, the two simply stared at each other, a connection sparking between them like a live wire. Then, to Lily's surprise, George stood up and began to pad towards her, his tail twitching with curiosity.

Lily hesitated for a moment, unsure of what to do. But something about George's gentle demeanor put her at ease, and she reached out a hand to pet him. George purred loudly, nuzzling her hand with his head, and Lily felt a sense of calm wash over her.

From that moment on, George and Lily were inseparable. They spent their days exploring the neighborhood, chasing after butterflies, and curled up together in the sunbeams that streamed through the windows. George taught Lily all about the art of napping, and how to find the perfect spot to watch the birds outside.     

As the days turned into weeks, Lily's parents began to notice a change in their daughter. She seemed happier, more confident, and more at ease in her own skin. And whenever she looked into George's piercing green eyes, she felt a sense of peace and contentment wash over her.

One evening, as the sun set over the neighborhood, Lily snuggled up beside George on the couch. She stroked his soft fur, feeling the warmth of his body radiate into

Time taken: 21.97 seconds
INFO - Disconnecting from server...
INFO - Disconnected from server.
```
