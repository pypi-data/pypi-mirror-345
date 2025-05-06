# -----------------------------------------------------------------------------
# Proyecto: Generative AI Diffusion System - AA3 2024/2025
# Archivo:  samplers/euler_maruyama.py
# Autores:
#   - Manuel Muñoz Bermejo (manuel.munnozb@estudiante.uam.es)
#   - Daniel Ortiz Buzarra (daniel.ortizbuzarra@estudiante.uam.es)
# Licencia: MIT
# -----------------------------------------------------------------------------

from __future__ import annotations

import logging
from typing import Callable, Optional, Tuple

import torch
from torch import Tensor

from .base_sampler import BaseSampler
from generative_diffusion.controllable import BaseController


class EulerMaruyamaSampler(BaseSampler):
    """
    Integración backward de la SDE con el esquema clásico Euler‑Maruyama.
    """

    def __init__(self, *, logger: Optional[logging.Logger] = None) -> None:
        self.logger = logger or logging.getLogger(__name__)

    # ------------------------------------------------------------------ #
    # Main                                                               #
    # ------------------------------------------------------------------ #
    def sample(
        self,
        x_0: Tensor,
        sde,
        score_model: Callable,
        *,
        t_0: float = 1.0,
        t_end: float = 1e-3,
        n_steps: int = 500,
        condition: Optional[Tensor] = None,
        seed: Optional[int] = None,
        controller: Optional[BaseController] = None,
    ) -> Tuple[Tensor, Tensor]:
        if seed is not None:
            torch.manual_seed(seed)

        device = x_0.device
        times = torch.linspace(t_0, t_end, n_steps + 1, device=device)
        dt = times[1] - times[0]

        traj = torch.empty(n_steps + 1, *x_0.shape, device=device, dtype=x_0.dtype)
        traj[0] = x_0

        score_fn = self._prepare_score_model(score_model, condition)

        x = x_0.clone()
        for i in range(n_steps):
            t = times[i]
            t_batch = torch.full((x.shape[0],), t, device=device, dtype=x.dtype)

            drift = sde.backward_drift(x, t_batch, score_fn)
            diffusion = sde.diffusion(t_batch).view(-1, *([1] * (x.ndim - 1)))

            x = x + drift * dt + diffusion * torch.sqrt(dt.abs()) * torch.randn_like(x)

            if controller is not None:
                x = controller.process_step(x_t=x, t=t_batch)

            traj[i + 1] = x

        return times, traj
