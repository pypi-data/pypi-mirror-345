# -----------------------------------------------------------------------------
# Proyecto: Generative AI Diffusion System - AA3 2024/2025
# Archivo:  schedulers/constant_scheduler.py
# Autores:
#   - Manuel Muñoz Bermejo (manuel.munnozb@estudiante.uam.es)
#   - Daniel Ortiz Buzarra (daniel.ortizbuzarra@estudiante.uam.es)
# Licencia: MIT
# -----------------------------------------------------------------------------

from __future__ import annotations

import torch
from torch import Tensor

from .base_scheduler import BaseScheduler


class ConstantScheduler(BaseScheduler):
    """
    Scheduler con β(t) constante.

    β(t) = β₀  ⇒  ᾱ(t) = (1 − β₀)ᵗ   (t ∈ [0, 1])
    """

    def __init__(self, *, beta: float = 0.1) -> None:
        if not (0.0 < beta < 1.0):
            raise ValueError("`beta` debe pertenecer al intervalo (0, 1).")
        self.beta_value = float(beta)

    # ------------------------------------------------------------------ #
    # Implementación de la interfaz                                      #
    # ------------------------------------------------------------------ #
    def beta(self, t: Tensor) -> Tensor:
        return torch.full_like(t, self.beta_value)

    def alpha_bar(self, t: Tensor) -> Tensor:
        # t se espera normalizado en [0,1]; no necesitamos convertir a pasos enteros
        return (1.0 - self.beta_value) ** t
