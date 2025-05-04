from mlx_lm_omni import load, generate
import librosa
from io import BytesIO
from urllib.request import urlopen

model, tokenizer = load("fixie-ai/ultravox-v0_5-llama-3_1-8b", model_config={})

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