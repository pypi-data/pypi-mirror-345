import mlx.core as mx
import mlx.nn as nn
import math

from dataclasses import dataclass

@dataclass
class AudioTowerConfig:
    num_mel_bins: int
    d_model: int
    n_window: int
    encoder_attention_heads: int
    encoder_layers: int
    max_source_positions: int
    output_dim: int
    
    @staticmethod
    def from_dict(cfg: dict) -> "AudioTowerConfig":
        return AudioTowerConfig(
            num_mel_bins=cfg["num_mel_bins"],
            d_model=cfg["d_model"],
            n_window=cfg["n_window"],
            encoder_attention_heads=cfg["encoder_attention_heads"],
            encoder_layers=cfg["encoder_layers"],
            max_source_positions=cfg["max_source_positions"],
            output_dim=cfg["output_dim"],
        )
    
def sinusoids(length, channels, max_timescale=10000):
    """Returns sinusoids for positional embedding"""
    assert channels % 2 == 0
    log_timescale_increment = math.log(max_timescale) / (channels // 2 - 1)
    inv_timescales = mx.exp(-log_timescale_increment * mx.arange(channels // 2, dtype=mx.bfloat16))
    scaled_time = mx.arange(length, dtype=mx.bfloat16)[:, None] * inv_timescales[None, :]
    return mx.concatenate([mx.sin(scaled_time), mx.cos(scaled_time)], axis=1)

class MultiHeadAttention(nn.Module):
    def __init__(self, d_model: int, n_head: int, bias: bool = True):
        super().__init__()
        self.n_head = n_head
        self.k_proj = nn.Linear(d_model, d_model, bias=False)
        self.v_proj = nn.Linear(d_model, d_model, bias=bias)
        self.q_proj = nn.Linear(d_model, d_model, bias=bias)
        self.out_proj = nn.Linear(d_model, d_model, bias=bias)

    def __call__(self, x: mx.array, xa: mx.array = None, mask: mx.array = None, kv_cache: tuple[mx.array, mx.array] = None) -> tuple[mx.array, tuple[mx.array, mx.array], mx.array]:
        q = self.q_proj(x)
        if xa is None:
            k = self.k_proj(x)
            v = self.v_proj(x)
            if kv_cache is not None:
                k = mx.concatenate([kv_cache[0], k], axis=1)
                v = mx.concatenate([kv_cache[1], v], axis=1)
        elif kv_cache is None:
            k = self.k_proj(xa)
            v = self.v_proj(xa)
        else:
            k, v = kv_cache
        wv, qk = self.qkv_attention(q, k, v, mask)
        return self.out_proj(wv), (k, v), qk

    def qkv_attention(self, q: mx.array, k: mx.array, v: mx.array, mask: mx.array = None) -> tuple[mx.array, mx.array]:
        n_batch, n_ctx, n_state = q.shape
        scale = (n_state // self.n_head) ** -0.25
        q = q.reshape(*q.shape[:2], self.n_head, -1).transpose(0, 2, 1, 3) * scale
        k = k.reshape(*k.shape[:2], self.n_head, -1).transpose(0, 2, 3, 1) * scale
        v = v.reshape(*v.shape[:2], self.n_head, -1).transpose(0, 2, 1, 3)
        qk = q @ k
        if mask is not None:
            qk = qk + mask[:n_ctx, :n_ctx]
        w = mx.softmax(qk, axis=-1)
        out = (w @ v).transpose(0, 2, 1, 3)
        out = out.reshape(n_batch, n_ctx, n_state)
        return out, qk

class ResidualAttentionBlock(nn.Module):
    def __init__(self, d_model: int, n_head: int, cross_attention: bool = False):
        super().__init__()
        self.self_attn = MultiHeadAttention(d_model, n_head)
        self.self_attn_layer_norm = nn.LayerNorm(d_model)
        self.encoder_attn = MultiHeadAttention(d_model, n_head) if cross_attention else None
        self.encoder_attn_layer_norm = nn.LayerNorm(d_model) if cross_attention else None
        n_mlp = d_model * 4
        self.fc1 = nn.Linear(d_model, n_mlp)
        self.fc2 = nn.Linear(n_mlp, d_model)
        self.final_layer_norm = nn.LayerNorm(d_model)

    def __call__(self, x: mx.array, xa: mx.array = None, mask: mx.array = None, kv_cache: tuple[mx.array, mx.array] = None) -> tuple[mx.array, tuple[mx.array, mx.array], mx.array]:
        residual = x
        kv, cross_kv = kv_cache if kv_cache else (None, None)
        x, kv, _ = self.self_attn(self.self_attn_layer_norm(x), mask=mask, kv_cache=kv)
        x = x + residual
        cross_qk = None
        if self.encoder_attn:
            y, cross_kv, cross_qk = self.encoder_attn(self.encoder_attn_layer_norm(x), xa, kv_cache=cross_kv)
            x += y
        residual = x
        x = self.final_layer_norm(x)
        x = self.fc1(x)
        x = nn.gelu(x)
        x = self.fc2(x)
        x = x + residual
        return x, (kv, cross_kv), cross_qk

class AudioTower(nn.Module):
    def __init__(self, cfg: AudioTowerConfig):
        super().__init__()
        self.n_window = cfg.n_window
        self.conv1 = nn.Conv1d(cfg.num_mel_bins, cfg.d_model, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(cfg.d_model, cfg.d_model, kernel_size=3, stride=2, padding=1)
        self._positional_embedding = sinusoids(cfg.max_source_positions, cfg.d_model)
        self.layers = [ResidualAttentionBlock(cfg.d_model, cfg.encoder_attention_heads) for _ in range(cfg.encoder_layers)]
        
        self.avg_pooler = nn.AvgPool1d(2, stride=2)
        self.proj = nn.Linear(cfg.d_model, cfg.output_dim)
        
        self.ln_post = nn.LayerNorm(cfg.d_model)

    def __call__(self, audio_mel: mx.array) -> mx.array:
        # padding more to the right to make the length a multiple of self.n_window
        x_size = audio_mel.shape[1] // 2
        if audio_mel.shape[1] % (self.n_window * 2) != 0:
            last_chunk_size = audio_mel.shape[1] % (self.n_window * 2)
            audio_mel = mx.pad(audio_mel, pad_width=[(0, 0), (0, self.n_window * 2 - last_chunk_size)], mode="constant", constant_values=0)
        else:
            last_chunk_size = self.n_window
        
        # split audio_mel into chunks of size self.n_window * 2
        chunks_count = math.floor(audio_mel.shape[1] / (self.n_window * 2))
        chunks = mx.reshape(audio_mel, (audio_mel.shape[0], chunks_count, self.n_window * 2))
        chunks = mx.transpose(chunks, (1, 2, 0))
    
        x = nn.gelu(self.conv1(chunks))
        
        if last_chunk_size != self.n_window:
            x[chunks_count - 1, last_chunk_size:, :] = 0
            
        x = nn.gelu(self.conv2(x))
        
        embed_pos = mx.expand_dims(self._positional_embedding[:x.shape[1]], axis=0)
        x = x + embed_pos        
        x = mx.reshape(x, (1, x.shape[0] * x.shape[1], x.shape[2]))[:, :x_size, :]
        
        for block in self.layers:
            x, _, _ = block(x)
                        
        x = self.avg_pooler(x)
        x = self.ln_post(x)
        x = self.proj(x)
        return x

    def update(self, weights: dict):
        if weights["conv1"]['weight'].shape[1] == 128: # convert from pytorch to mlx
            weights["conv1"]['weight'] = mx.swapaxes(weights["conv1"]['weight'], 1, 2)
            weights["conv2"]['weight'] = mx.swapaxes(weights["conv2"]['weight'], 1, 2)
        super().update(weights)
        
        