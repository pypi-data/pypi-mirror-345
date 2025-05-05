import mlx.nn as nn
import mlx.core as mx

from dataclasses import dataclass

class StackAudioFrames(nn.Module):
    """
    Stack the audio embedding frames to reduce the sequence length by a factor
    of `stack_factor`, padding the last frames with zeros if needed.
    """
    def __init__(self, stack_factor: int = 8):
        super().__init__()
        self.stack_factor = stack_factor

    def __call__(self, audio_embeds: mx.array) -> mx.array:
        # audio_embeds: [B, T, C]
        B, T, C = audio_embeds.shape
        # compute padded length
        T_pad = ((T + self.stack_factor - 1) // self.stack_factor) * self.stack_factor
        # pad only the time dimension (axis=1) at the end
        pad_cfg = [(0, 0), (0, T_pad - T), (0, 0)]
        audio_embeds = mx.pad(
            audio_embeds,
            pad_width=pad_cfg,
            mode="constant",
            constant_values=0,
        )
        # reshape into [B, T//S, C*S]
        B, T2, C = audio_embeds.shape
        audio_embeds = mx.reshape(
            audio_embeds,
            (B, T2 // self.stack_factor, C * self.stack_factor),
        )
        return audio_embeds


class RMSNorm(nn.RMSNorm):
    """
    MLX RMSNorm with weight initialized to `init_val` (defaults to 1).
    """
    def __init__(self, hidden_size: int, init_val: float = 1.0, eps: float = 1e-6):
        super().__init__(dims=hidden_size, eps=eps)
        # override the default γ initialization if desired
        # self.weight is the learned scale parameter (γ), initialized to 1 by default
        if init_val != 1.0:
            init_fn = nn.init.constant(init_val)
            # apply initializer to the existing weight array
            self.weight = init_fn(self.weight)


class SwiGLU(nn.Module):
    """
    Switched GLU: splits the last dim into two halves, gates the first with
    SiLU of the second.
    """
    def __call__(self, x: mx.array) -> mx.array:
        # split along the feature axis
        a, b = mx.split(x, 2, axis=-1)
        return nn.silu(b) * a


class Identity(nn.Module):
    """A no-op layer that returns its input unchanged."""
    def __call__(self, x: mx.array) -> mx.array:
        return x

@dataclass
class ProjectorArgs:
    stack_factor: int
    projector_act: str
    projector_ln_mid: bool
    norm_init: float
    hidden_size: int
    audio_hidden_size: int
    
    @staticmethod
    def from_dict(cfg: dict) -> "ProjectorArgs":
        return ProjectorArgs(
            stack_factor=cfg["stack_factor"],
            projector_act=cfg["projector_act"],
            projector_ln_mid=cfg["projector_ln_mid"],
            norm_init=cfg["norm_init"],
            hidden_size=cfg["hidden_size"],
            audio_hidden_size=cfg["audio_hidden_size"],
        )
    

class Projector(nn.Module):
    def __init__(self, config: ProjectorArgs):
        super().__init__()
        self.hidden_dim = config.hidden_size
        self._pad_and_stack = StackAudioFrames(config.stack_factor)

        dim_in = config.audio_hidden_size * config.stack_factor
        # pre‑norm
        self.ln_pre = RMSNorm(dim_in, init_val=config.norm_init)
        # first linear: [B, T, C*S] → [B, T, H]
        self.linear_1 = nn.Linear(dim_in, self.hidden_dim, bias=False)

        # activation and mid dim
        if config.projector_act.lower() == "swiglu":
            self.act = SwiGLU()
            dim_mid = self.hidden_dim // 2
        else:
            # pick the standard MLX activation module by name
            ActLayer = getattr(nn, config.projector_act.capitalize())
            self.act = ActLayer()
            dim_mid = self.hidden_dim

        # second linear: [B, T, H'] → [B, T, D]
        dim_out = config.hidden_size
        self.linear_2 = nn.Linear(dim_mid, dim_out, bias=False)

        # mid/post normalization choice
        if config.projector_ln_mid:
            self.ln_mid = RMSNorm(dim_mid, init_val=config.norm_init)
            self.ln_post = Identity()
        else:
            self.ln_mid = Identity()
            self.ln_post = RMSNorm(dim_out, init_val=config.norm_init)
            
    def __call__(self, x: mx.array) -> mx.array:
        x = self._pad_and_stack(x)
        x = self.ln_pre(x)
        x = self.linear_1(x)
        x = self.act(x)
        x = self.ln_mid(x)
        x = self.linear_2(x)
        x = self.ln_post(x)
        return x