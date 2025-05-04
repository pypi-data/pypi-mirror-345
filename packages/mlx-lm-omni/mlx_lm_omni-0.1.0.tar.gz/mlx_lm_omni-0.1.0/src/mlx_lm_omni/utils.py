import mlx.nn as nn
from mlx_lm.utils import load_model, load_tokenizer, get_model_path, load_adapters
from typing import Type, Tuple, Optional
import mlx_lm_omni.models.qwen_omni.model as qwen_omni
import mlx_lm_omni.models.ultravox.model as ultravox

def get_model_classes(config: dict) -> Tuple[Type[nn.Module], Type]:
    match (config["model_type"]):
        case "qwen2_5_omni":
            return qwen_omni.Model, qwen_omni.ModelArgs
        case "ultravox":
            return ultravox.Model, ultravox.ModelArgs
        case _:
            raise ValueError(f"Model type {config['model_type']} not supported")

def load(
    path_or_hf_repo: str,
    tokenizer_config={},
    model_config={},
    adapter_path: Optional[str] = None,
    lazy: bool = False
    ):
    model_path = get_model_path(path_or_hf_repo)

    model, config = load_model(model_path, lazy, model_config=model_config, strict=False, get_model_classes=get_model_classes)
    model = model
    if adapter_path is not None:
        model = load_adapters(model, adapter_path)
        model.eval()
    tokenizer = load_tokenizer(
        model_path, tokenizer_config, eos_token_ids=config.get("eos_token_id", None)
    )
    tokenizer = model.build_custom_tokenizer(tokenizer)
    return model, tokenizer