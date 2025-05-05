# Inference for Speech Models in MLX

This repo implements some speech models in MLX for better performance on Mac devices.

Currently, it supports the following models:

- [x] Qwen2.5-Omni (both original version and mlx-quant version), currently supported only speech model
- [x] Ultravox-0.5

# Performance

Tested on MacBook M4-Pro (48GB RAM):
| Model                                                                            | Prompt TPS | Generation TPS |
| -------------------------------------------------------------------------------- | ---------- | -------------- |
| Qwen/Qwen2.5-Omni-7B                                                             | 259.5      | 17.8           |
| Qwen/Qwen2.5-Omni-3B                                                             | 468.4      | 38.8           |
| giangndm/qwen2.5-omni-7b-mlx-8bit                                                | 253.4      | 31.7           |
| giangndm/qwen2.5-omni-7b-mlx-4bit                                                | 259.2      | 57.6           |
| giangndm/qwen2.5-omni-3b-mlx-8bit                                                | 456.2      | 67.0           |
| fixie-ai/ultravox-v0_5-llama-3_1-8b and mlx-community/Llama-3.1-8B-Instruct-4bit | 188.5      | 40.4           |

# How to use

```bash
uv add mlx-lm-omni 
# or
uv add https://github.com/giangndm/mlx-lm-omni.git
```

```python
from mlx_lm_omni import load, generate
import librosa
from io import BytesIO
from urllib.request import urlopen

# model, tokenizer = load("giangndm/qwen2.5-omni-7b-mlx-4bit")
model, tokenizer = load("fixie-ai/ultravox-v0_5-llama-3_1-8b", model_config={"text_model_id": "mlx-community/Llama-3.1-8B-Instruct-4bit"})

audio_path = "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen2-Audio/audio/1272-128104-0000.flac"
audio = librosa.load(BytesIO(urlopen(audio_path).read()), sr=16000)[0]

messages = [
    {"role": "system", "content": "You are a speech recognition model."},
    {"role": "user", "content": "Transcribe the English audio into text without any punctuation marks.", "audio": audio},
]
prompt = tokenizer.apply_chat_template(
    messages, add_generation_prompt=True
)

text = generate(model, tokenizer, prompt=prompt, verbose=True)
```