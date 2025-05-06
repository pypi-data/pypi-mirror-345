# -----------------------------------------------------------------------------
# Proyecto: Generative AI Diffusion System - AA3 2024/2025
# Archivo:  sde/ve_sde.py
# Autores:
#   - Manuel Muñoz Bermejo (manuel.munnozb@estudiante.uam.es)
#   - Daniel Ortiz Buzarra (daniel.ortizbuzarra@estudiante.uam.es)
# Licencia: MIT
# -----------------------------------------------------------------------------

from __future__ import annotations

import torch
from torch import Tensor

from .base_sde import BaseSDE


class VESDE(BaseSDE):
    """
    Variance‑Exploding SDE (sigma ≈ 25 en Song et al., 2021).
    """

    def __init__(self, *, sigma: float = 25.0, coef_score: float = 1.0) -> None:
        if sigma <= 1.0:
            raise ValueError("`sigma` debe ser > 1 para VE‑SDE.")
        super().__init__()
        self.sigma = float(sigma)
        self.coef_score = float(coef_score)

    # ------------------------------------------------------------------ #
    # Forward                                                            #
    # ------------------------------------------------------------------ #
    def drift(self, x_t: Tensor, t: Tensor) -> Tensor:
        return torch.zeros_like(x_t)

    def drift_backward(self, x_t: Tensor, t: Tensor) -> Tensor:
        return torch.zeros_like(x_t)

    def diffusion(self, t: Tensor) -> Tensor:
        return self.sigma**t

    def mu_t(self, x_0: Tensor, t: Tensor) -> Tensor:
        return x_0

    def sigma_t(self, t: Tensor) -> Tensor:
        log_sigma = torch.log(torch.tensor(self.sigma, device=t.device))
        return torch.sqrt(0.5 * (self.sigma ** (2 * t) - 1.0) / log_sigma)

    # ------------------------------------------------------------------ #
    # Backward                                                           #
    # ------------------------------------------------------------------ #
    def backward_drift(self, x_t: Tensor, t: Tensor, score_fn) -> Tensor:
        g_t = self._broadcast(self.diffusion(t), x_t)
        return -self.coef_score * (g_t**2) * score_fn(x_t, t)

    def backward_drift_exponencial(self, x_t: Tensor, t: Tensor, score_fn) -> Tensor:
        # Como no hay betas, igual que backward_drift
        return self.backward_drift(x_t, t, score_fn)
