# minigpt

Official pip package for the MiniGPT series.

```bash
pip install minigptai
```

```python
from minigpt import load_model, generate
from tokenizers import ByteLevelBPETokenizer

model, vocab, merges = load_model("minigpt0")
tokenizer = ByteLevelBPETokenizer(vocab, merges)

prompt = "What is a neural network?"
generate(model, tokenizer, prompt)
```