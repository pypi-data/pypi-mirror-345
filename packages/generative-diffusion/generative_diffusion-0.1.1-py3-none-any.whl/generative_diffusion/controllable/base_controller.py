# -----------------------------------------------------------------------------
# Proyecto: Generative AI Diffusion System - AA3 2024/2025
# Archivo:  controllable/base_controller.py
# Autores:
#   - Manuel Muñoz Bermejo (manuel.munnozb@estudiante.uam.es)
#   - Daniel Ortiz Buzarra (daniel.ortizbuzarra@estudiante.uam.es)
# Licencia: MIT
# -----------------------------------------------------------------------------

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from torch import Tensor


class BaseController(ABC):
    """
    Clase base para las técnicas de generación controlada (imputación, guidance,
    generación condicional, etc.).
    """

    # --------------------------------------------------------------------- #
    # Métodos que cada controlador concreto debe implementar
    # --------------------------------------------------------------------- #
    @abstractmethod
    def process_step(
        self,
        x_t: Tensor,
        t: Tensor,
        *,
        x_orig: Optional[Tensor] = None,
        step_index: Optional[int] = None,
    ) -> Tensor:
        """
        Modifica el estado `x_t` tras cada integración del sampler.

        Args:
            x_t: Estado actual.
            t: Tiempo actual (shape: [B]).
            x_orig: Imagen original (si procede).
            step_index: Índice de paso discreto.

        Returns
        -------
        Tensor
            Estado modificado según la técnica de control.
        """
        raise NotImplementedError

    @abstractmethod
    def prepare_initial(self, x_t: Tensor) -> Tensor:
        """
        Prepara el estado inicial antes de iniciar la generación controlada.

        Generalmente mezcla la imagen de entrada con ruido en las regiones que
        se van a sintetizar.

        Parameters
        ----------
        x_t : Tensor
            Imagen original.

        Returns
        -------
        Tensor
            Imagen inicial lista para usarse como `x_0` en el sampler.
        """
        raise NotImplementedError
