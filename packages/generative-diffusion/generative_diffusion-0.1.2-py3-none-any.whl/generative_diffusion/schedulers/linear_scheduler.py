# -----------------------------------------------------------------------------
# Proyecto: Generative AI Diffusion System - AA3 2024/2025
# Archivo:  schedulers/linear_scheduler.py
# Autores:
#   - Manuel Muñoz Bermejo (manuel.munnozb@estudiante.uam.es)
#   - Daniel Ortiz Buzarra (daniel.ortizbuzarra@estudiante.uam.es)
# Licencia: MIT
# -----------------------------------------------------------------------------

from __future__ import annotations

import torch
from torch import Tensor

from .base_scheduler import BaseScheduler


class LinearScheduler(BaseScheduler):
    def __init__(self, beta_start: float = 0.1, beta_end: float = 20):
        self.beta_start = beta_start
        self.beta_end = beta_end

    def beta(self, t: Tensor) -> Tensor:
        beta_t = self.beta_start + (self.beta_end - self.beta_start) * t
        return beta_t

    def alpha_bar(self, t: Tensor) -> Tensor:
        beta0, beta1 = self.beta_start, self.beta_end
        alpha_bar = torch.exp(-0.5 * (beta1 - beta0) * t**2 - beta0 * t)
        return torch.clamp(alpha_bar, 0.0, 1.0)
