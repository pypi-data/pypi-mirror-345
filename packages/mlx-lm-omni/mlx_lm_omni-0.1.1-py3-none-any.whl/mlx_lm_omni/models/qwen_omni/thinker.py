from mlx_lm.models.qwen2 import Model, ModelArgs

from mlx_lm_omni.tokenizer import ExtendedEmbedding
from .audio_tower import AudioTower, AudioTowerConfig

class Thinker(Model):
    def __init__(self, config: dict):
        args = ModelArgs.from_dict(config["text_config"])
        super().__init__(args)
        self.model.embed_tokens = ExtendedEmbedding(args.vocab_size, args.hidden_size)
        self.audio_tower = AudioTower(AudioTowerConfig.from_dict(config["audio_config"]))
        