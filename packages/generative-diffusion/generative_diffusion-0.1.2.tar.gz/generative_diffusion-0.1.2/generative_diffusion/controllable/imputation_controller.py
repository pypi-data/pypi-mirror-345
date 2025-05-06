# -----------------------------------------------------------------------------
# Proyecto: Generative AI Diffusion System - AA3 2024/2025
# Archivo:  controllable/imputation_controller.py
# Autores:
#   - Manuel Muñoz Bermejo (manuel.munnozb@estudiante.uam.es)
#   - Daniel Ortiz Buzarra (daniel.ortizbuzarra@estudiante.uam.es)
# Licencia: MIT
# -----------------------------------------------------------------------------

from __future__ import annotations

from typing import Optional

import torch
from torch import Tensor

from .base_controller import BaseController


class ImputationController(BaseController):
    """
    Mantiene fijas las regiones conocidas de la imagen y genera las regiones
    faltantes durante el muestreo.
    """

    def __init__(self, mask: Tensor) -> None:
        """
        Parameters
        ----------
        mask : Tensor
            Máscara binaria con 1 → píxel conocido, 0 → desconocido.
            Admite formas `[B,1,H,W]` o `[B,C,H,W]`.
        """
        if mask.dtype not in (torch.bool, torch.float32, torch.float64):
            raise TypeError("`mask` debe ser tensor booleano o float en [0,1].")

        self.mask: Tensor = mask.float()
        self._prepared_x: Optional[Tensor] = None

    # ------------------------------------------------------------------ #
    # API pública (override de BaseController)                           #
    # ------------------------------------------------------------------ #
    def prepare_initial(self, x_t: Tensor) -> Tensor:
        """
        Mezcla la imagen con ruido blanco en las zonas ocultas.

        Devuelve el tensor resultante que servirá como estado inicial del
        sampler.
        """
        mask = self._expanded_mask(x_t)
        noise = torch.randn_like(x_t)
        self._prepared_x = x_t * mask + noise * (1.0 - mask)
        return self._prepared_x

    def process_step(
        self,
        x_t: Tensor,
        t: Tensor,  # noqa: ARG002 – se mantiene por compatibilidad con la interfaz
        *,
        x_orig: Optional[Tensor] = None,  # noqa: ARG002
        step_index: Optional[int] = None,  # noqa: ARG002
    ) -> Tensor:
        """
        Restaura las regiones conocidas tras cada paso del sampler.
        """
        if self._prepared_x is None:
            raise RuntimeError(
                "Debes llamar primero a `prepare_initial` antes de `process_step`."
            )

        mask = self._expanded_mask(x_t)
        return x_t * (1.0 - mask) + self._prepared_x * mask

    # ------------------------------------------------------------------ #
    # Utilidades internas                                                #
    # ------------------------------------------------------------------ #
    def _expanded_mask(self, x: Tensor) -> Tensor:
        """
        Expande la máscara a C canales si llega con un único canal.
        """
        if self.mask.shape[1] == 1 and x.shape[1] > 1:
            return self.mask.expand(-1, x.shape[1], -1, -1)
        return self.mask
