# -----------------------------------------------------------------------------
# Proyecto: Generative AI Diffusion System - AA3 2024/2025
# Archivo:  score_networks/unet_score_network.py
# Autores:
#   - Manuel Muñoz Bermejo (manuel.munnozb@estudiante.uam.es)
#   - Daniel Ortiz Buzarra (daniel.ortizbuzarra@estudiante.uam.es)
# Licencia: MIT
# -----------------------------------------------------------------------------

from __future__ import annotations

from typing import Callable, List, Optional

import numpy as np
import torch
import torch.nn as nn
from torch import Tensor

from .base_score_model import BaseScoreModel


class GaussianRandomFourierFeatures(nn.Module):
    """Gaussian random Fourier features to encode time steps."""

    def __init__(self, embed_dim: int, scale: float = 30.0) -> None:
        super().__init__()
        # Fixed random weights (not trainable)
        self.rff_weights = nn.Parameter(
            torch.randn(embed_dim // 2) * scale, requires_grad=False
        )

    def forward(self, x: Tensor) -> Tensor:  # shape x = [B]
        x_proj = x[:, None] * self.rff_weights[None, :] * 2.0 * np.pi
        return torch.cat([torch.sin(x_proj), torch.cos(x_proj)], dim=-1)


class Dense(nn.Module):
    """Fully‑connected layer that reshapes outputs to feature maps."""

    def __init__(self, input_dim: int, output_dim: int) -> None:
        super().__init__()
        self.dense = nn.Linear(input_dim, output_dim)

    def forward(self, x: Tensor) -> Tensor:  # shape → [B, output_dim, 1, 1]
        return self.dense(x)[..., None, None]


class ScoreNet(BaseScoreModel):
    """
    U‑Net dependiente del tiempo que implementa un modelo score‑based.

    Características:
    * Compatible con imágenes 1‑canal o RGB.
    * Soporta generación condicional por clase.
    * Arquitectura configurable vía parámetro ``channels``.
    """

    def __init__(
        self,
        marginal_prob_std: Callable[[Tensor], Tensor],
        *,
        in_channels: int = 3,
        out_channels: Optional[int] = None,
        channels: List[int] | None = None,
        embed_dim: int = 256,
        num_classes: Optional[int] = None,
    ) -> None:
        if channels is None:
            channels = [32, 128, 128, 256]
        super().__init__(marginal_prob_std, in_channels, out_channels, num_classes)

        # Activation (Swish)
        self.act = lambda x: x * torch.sigmoid(x)

        # Time embedding
        self.embed = nn.Sequential(
            GaussianRandomFourierFeatures(embed_dim=embed_dim),
            nn.Linear(embed_dim, embed_dim),
        )

        # Class embedding
        if self.is_conditional:
            self.class_embed = nn.Embedding(self.num_classes, embed_dim)
            self.combine_embed = nn.Linear(embed_dim * 2, embed_dim)

        # ---------------- Encoder ---------------- #
        self.conv1 = nn.Conv2d(self.in_channels, channels[0], 3, stride=1, bias=False)
        self.dense1 = Dense(embed_dim, channels[0])
        self.gnorm1 = nn.GroupNorm(4, channels[0])

        self.conv2 = nn.Conv2d(channels[0], channels[1], 3, stride=2, bias=False)
        self.dense2 = Dense(embed_dim, channels[1])
        self.gnorm2 = nn.GroupNorm(32, channels[1])

        self.conv3 = nn.Conv2d(channels[1], channels[2], 3, stride=2, bias=False)
        self.dense3 = Dense(embed_dim, channels[2])
        self.gnorm3 = nn.GroupNorm(32, channels[2])

        self.conv4 = nn.Conv2d(channels[2], channels[3], 3, stride=2, bias=False)
        self.dense4 = Dense(embed_dim, channels[3])
        self.gnorm4 = nn.GroupNorm(32, channels[3])

        # ---------------- Decoder ---------------- #
        self.tconv4 = nn.ConvTranspose2d(
            channels[3], channels[2], 3, stride=2, bias=False
        )
        self.dense5 = Dense(embed_dim, channels[2])
        self.tgnorm4 = nn.GroupNorm(32, channels[2])

        self.tconv3 = nn.ConvTranspose2d(
            channels[2] + channels[2],
            channels[1],
            3,
            stride=2,
            bias=False,
            output_padding=1,
        )
        self.dense6 = Dense(embed_dim, channels[1])
        self.tgnorm3 = nn.GroupNorm(32, channels[1])

        self.tconv2 = nn.ConvTranspose2d(
            channels[1] + channels[1],
            channels[0],
            3,
            stride=2,
            bias=False,
            output_padding=1,
        )
        self.dense7 = Dense(embed_dim, channels[0])
        self.tgnorm2 = nn.GroupNorm(32, channels[0])

        self.tconv1 = nn.ConvTranspose2d(
            channels[0] + channels[0], self.out_channels, 3, stride=1
        )

    # ------------------------------------------------------------------ #
    # Embeddings                                                         #
    # ------------------------------------------------------------------ #
    def _get_embedding(
        self, t: Tensor, y: Optional[Tensor] = None
    ) -> Tensor:  # shape [B, embed_dim]
        """
        Combina embedding temporal y de clase (si procede).
        """
        t_embed = self.act(self.embed(t))

        if not self.is_conditional:
            return t_embed

        class_embed = (
            self.class_embed(y) if y is not None else torch.zeros_like(t_embed)
        )
        return self.act(self.combine_embed(torch.cat([t_embed, class_embed], dim=1)))

    # ------------------------------------------------------------------ #
    # Forward                                                            #
    # ------------------------------------------------------------------ #
    def forward(
        self, x: Tensor, t: Tensor, condition: Optional[Tensor] = None
    ) -> Tensor:  # noqa: D401
        """
        Calcula el score para el lote ``x`` en instantes ``t``.
        """
        embed = self._get_embedding(t, condition)

        # -------- Encoder -------- #
        h1 = self.act(self.gnorm1(self.conv1(x) + self.dense1(embed)))
        h2 = self.act(self.gnorm2(self.conv2(h1) + self.dense2(embed)))
        h3 = self.act(self.gnorm3(self.conv3(h2) + self.dense3(embed)))
        h4 = self.act(self.gnorm4(self.conv4(h3) + self.dense4(embed)))

        # -------- Decoder -------- #
        h = self.act(self.tgnorm4(self.tconv4(h4) + self.dense5(embed)))
        h = self.act(
            self.tgnorm3(self.tconv3(torch.cat([h, h3], dim=1)) + self.dense6(embed))
        )
        h = self.act(
            self.tgnorm2(self.tconv2(torch.cat([h, h2], dim=1)) + self.dense7(embed))
        )
        h = self.tconv1(torch.cat([h, h1], dim=1))

        # Normalizar salida por σₜ
        return h / self.marginal_prob_std(t)[:, None, None, None]
