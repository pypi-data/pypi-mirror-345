# -----------------------------------------------------------------------------
# Proyecto: Generative AI Diffusion System - AA3 2024/2025
# Archivo:  controllable/imputation_mask_functions.py
# Autores:
#   - Manuel Muñoz Bermejo (manuel.munnozb@estudiante.uam.es)
#   - Daniel Ortiz Buzarra (daniel.ortizbuzarra@estudiante.uam.es)
# Licencia: MIT
# -----------------------------------------------------------------------------

from __future__ import annotations

import torch
from torch import Tensor


def center_square_mask(x: Tensor, keep_ratio: float = 0.5) -> Tensor:
    """
    Devuelve una máscara binaria con un cuadrado central visible.

    keep_ratio es el lado del cuadrado respecto al menor de (H, W).
    """
    b, _, h, w = x.shape
    side = int(min(h, w) * keep_ratio)
    y0, x0 = (h - side) // 2, (w - side) // 2

    mask = torch.zeros(b, 1, h, w, device=x.device)
    mask[:, :, y0 : y0 + side, x0 : x0 + side] = 1.0
    return mask


def border_mask(x: Tensor, border_ratio: float = 0.25) -> Tensor:
    """
    Máscara que deja visibles los bordes y oculta el centro.
    """
    b, _, h, w = x.shape
    y0, y1 = int(h * border_ratio), int(h * (1.0 - border_ratio))
    x0, x1 = int(w * border_ratio), int(w * (1.0 - border_ratio))

    mask = torch.ones(b, 1, h, w, device=x.device)
    mask[:, :, y0:y1, x0:x1] = 0.0
    return mask


def random_mask(x: Tensor, prob: float = 0.5) -> Tensor:
    """
    Máscara aleatoria (Bernoulli) con probabilidad `prob` de mantener un píxel.
    """
    b, _, h, w = x.shape
    return (torch.rand(b, 1, h, w, device=x.device) < prob).float()
