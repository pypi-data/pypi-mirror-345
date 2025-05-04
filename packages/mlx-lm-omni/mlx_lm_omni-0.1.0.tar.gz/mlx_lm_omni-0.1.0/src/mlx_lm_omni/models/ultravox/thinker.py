from typing import Type, Tuple

from mlx_lm.models.llama import Model, ModelArgs
from mlx_lm_omni.tokenizer import ExtendedEmbedding

class Thinker(Model):
    def __init__(self, args: ModelArgs):
        super().__init__(args)
        self.model.embed_tokens = ExtendedEmbedding(args.vocab_size, args.hidden_size)
        
def get_thinker_classes(config: dict) -> Tuple[Type[Model], Type[ModelArgs]]:
    return Thinker, ModelArgs
        