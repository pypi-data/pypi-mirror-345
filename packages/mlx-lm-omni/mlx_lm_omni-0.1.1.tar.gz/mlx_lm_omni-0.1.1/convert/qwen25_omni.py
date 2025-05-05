import os
import mlx.nn as nn

from mlx_lm.utils import upload_to_hub, save_config, load_config, get_model_path, create_model_card

from mlx_lm_omni import load

repo = "Qwen/Qwen2.5-Omni-3B"
output_path = "./.models/qwen2_5-omni-mlx-3b"
output_repo = "giangndm/qwen2.5-omni-3b-mlx-8bit"
group_size = 64
bits = 8

model_path = get_model_path(repo)
config = load_config(model_path)
model, tokenizer = load(repo)

nn.quantize(model, group_size=group_size, bits=bits)

# create output path
os.makedirs(output_path, exist_ok=True)

model.save_weights(output_path + "/model.safetensors")
tokenizer.save_pretrained(output_path)
config["quantization"] = {"group_size": group_size, "bits": bits}
save_config(config, config_path=output_path + "/config.json")

create_model_card(output_path, repo)
upload_to_hub(output_path, output_repo)