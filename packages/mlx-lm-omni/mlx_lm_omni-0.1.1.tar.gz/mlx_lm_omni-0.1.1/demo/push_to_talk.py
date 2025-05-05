import argparse
from mlx_lm_omni import load, generate
from mlx_lm.sample_utils import make_sampler
from mlx_lm.models.cache import make_prompt_cache
from recorder import AudioRecorder
parser = argparse.ArgumentParser()
parser.add_argument('--model', type=str, help='Path to the model')
parser.add_argument('--text-model-id', type=str, help='Override the text model id for ultravox model')
parser.add_argument('--single', type=str, help='Path to the input file, we will transcribe the input file')
parser.add_argument('--folder', type=str, help='Path to the input folder, we will transcribe all files in the folder')
parser.add_argument('--repl', type=str, help='Manual input mode, we will transcribe the input file in repl mode. Input as recording folder path')

args = parser.parse_args()

if args.model is None:
    args.model = "Qwen/Qwen2.5-Omni-3B"

model, tokenizer = load(args.model, model_config={"text_model_id": args.text_model_id})
kv_cache = make_prompt_cache(model)

messages = [
    {"role": "system", "content": "You are a helpful voice assistant, please listen carefully and summarize what user want to do in English. With name or other identification information, make sure to mention it. Response in Vietnamese."}
]

recorder = AudioRecorder()
print("Press and hold SPACE to record audio. Release to stop recording.")
try:
    while True:
        audio, file_path = recorder.get_last_recording()
        if audio is not None:
            messages.append({"role": "user", "content": "User voice:", "audio": audio})
            prompt = tokenizer.apply_chat_template(
                messages, add_generation_prompt=True
            )
            text = generate(model, tokenizer, prompt=prompt, max_tokens=1000, prompt_cache=kv_cache, verbose=True)
            messages.clear()
            
            # debug kv-cache
            keys, value = kv_cache[0].state
            print(f"Kv-Cache keys: {keys.shape}, value: {value.shape}")
            
except KeyboardInterrupt:
    print("\nExiting...") 
    