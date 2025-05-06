# -----------------------------------------------------------------------------
# Proyecto: Generative AI Diffusion System - AA3 2024/2025
# Archivo:  samplers/predictor_corrector.py
# Autores:
#   - Manuel Muñoz Bermejo (manuel.munnozb@estudiante.uam.es)
#   - Daniel Ortiz Buzarra (daniel.ortizbuzarra@estudiante.uam.es)
# Licencia: MIT
# -----------------------------------------------------------------------------

from __future__ import annotations

from typing import Callable, Optional, Tuple

import torch
from torch import Tensor

from .base_sampler import BaseSampler
from generative_diffusion.controllable import BaseController


class PredictorCorrectorSampler(BaseSampler):
    """
    *Predictor–Corrector* de Song et al. (2021) corregido:

    1. Predictor → Euler-Maruyama con término de ruido ajustado.
    2. ``corrector_steps`` pasos de Langevin dynamics con escalado SNR correcto.
    """

    def __init__(
        self, *, corrector_steps: int = 10, corrector_snr: float = 0.1
    ) -> None:
        if corrector_steps <= 0:
            raise ValueError("`corrector_steps` debe ser > 0.")
        self.corrector_steps = int(corrector_steps)
        self.corrector_snr = float(corrector_snr)

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

            # ---------- predictor (Euler-Maruyama corregido) ----------
            drift = sde.backward_drift(traj[i], t_batch, score_fn)
            diffusion = sde.diffusion(t_batch).view(-1, *([1] * (traj[i].ndim - 1)))

            noise = torch.randn_like(traj[i])
            x = traj[i] + drift * dt + 0.9 * diffusion * torch.sqrt(-dt) * noise

            # ---------- corrector (Langevin ajustado) ----------
            for _ in range(self.corrector_steps):
                score = score_fn(x, t_batch)
                noise = torch.randn_like(x)

                # Calcular sigma(t) usando el método correcto de la SDE
                sigma_t = sde.sigma_t(t_batch).view(-1, *([1] * (x.ndim - 1)))

                # Calcular epsilon basado en SNR y sigma(t)
                epsilon = (self.corrector_snr * sigma_t) ** 2

                # Paso de Langevin teóricamente correcto
                x = x + epsilon * score + torch.sqrt(2 * epsilon) * noise

            if controller is not None:
                x = controller.process_step(x_t=x, t=t_batch)

            traj[i + 1] = x

        return times, traj
