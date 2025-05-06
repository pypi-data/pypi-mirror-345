# -----------------------------------------------------------------------------
# Proyecto: Generative AI Diffusion System - AA3 2024/2025
# Archivo:  diffusion/losses.py
# Autores:
#   - Manuel Muñoz Bermejo (manuel.munnozb@estudiante.uam.es)
#   - Daniel Ortiz Buzarra (daniel.ortizbuzarra@estudiante.uam.es)
# Licencia: MIT
# -----------------------------------------------------------------------------

from __future__ import annotations

from typing import Optional

import torch
from torch import Tensor


def dsm_loss(
    *,
    score_model: torch.nn.Module,
    sde,
    x_0: Tensor,
    condition: Optional[Tensor] = None,
    eps: float = 1e-5,
) -> Tensor:
    """
    *Denoising Score Matching* (Song & Ermon, 2020).

    .. math::
        L = \\mathbb{E}_{t\\sim U(0,1),\\,z\\sim\\mathcal{N}}
             \\bigl\\|\\sigma_t\\,s_\\theta(x_t,t)+z\\bigr\\|_2^{2}

    Parameters
    ----------
    score_model
        Red neuronal que estima ∇ₓ log p(xₜ).
    sde
        Instancia de :class:`BaseSDE`.
    x_0
        Mini‐batch original (B,C,H,W).
    condition
        Etiquetas/condición fija para modelos condicionales.
    eps
        Margen para evitar t=0.

    Returns
    -------
    Tensor
        Escalar con la pérdida DSM.
    """
    B = x_0.size(0)
    t = torch.rand(B, device=x_0.device) * (1.0 - eps) + eps  # U(0,1)
    z = torch.randn_like(x_0)

    mu, sigma = sde.marginal_prob(x_0, t)
    x_t = mu + sigma.view(-1, *([1] * (x_0.ndim - 1))) * z

    score = score_model(x_t, t, condition)

    # σ_t sθ + z  → L2²
    diff = sigma.view(-1, *([1] * (x_0.ndim - 1))) * score + z
    loss = (diff.pow(2).flatten(1).sum(dim=1)).mean()
    return loss
