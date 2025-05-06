# -----------------------------------------------------------------------------
# Proyecto: Generative AI Diffusion System - AA3 2024/2025
# Archivo:  samplers/exponential_integrator.py
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


class ExponentialIntegratorSampler(BaseSampler):
    """
    Integrador exponencial (Zhang & Chen, 2023) para SDEs con parte lineal analítica.
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

        for i, t in enumerate(times[:-1]):
            t_batch = torch.full((x_0.shape[0],), t, device=device, dtype=x_0.dtype)

            x = traj[i]

            # Drift y diffusions
            noise = torch.randn_like(traj[i])
            diffusion = sde.diffusion(t_batch).view(-1, *([1] * (x.ndim - 1)))
            drift_coefficient_exponencial = sde.backward_drift_exponencial(
                x, t_batch, score_fn
            )
            drift = sde.drift_backward(x, t_batch)

            z = drift * dt

            # Usamos Taylor por si |z| es pequeño
            taylor_approx = 1 + 0.5 * z + (1 / 6) * z**2 + (1 / 24) * z**3

            drift_exp = torch.exp(z)
            numerador = drift_exp - 1

            threshold = 1e-6
            use_taylor = z.abs() < threshold

            resultado = torch.where(
                use_taylor,
                taylor_approx,
                numerador
                / torch.where(
                    z.abs() < threshold, torch.ones_like(z), z
                ),  # Para evitar cero en denominador
            )

            x = (
                +drift_exp * traj[i]
                + resultado * dt * drift_coefficient_exponencial
                + 0.9 * diffusion * torch.sqrt(dt.abs()) * noise
            )

            if controller is not None:
                x = controller.process_step(x_t=x, t=t_batch)

            traj[i + 1] = x

        return times, traj
