# -----------------------------------------------------------------------------
# Proyecto: Generative AI Diffusion System - AA3 2024/2025
# Archivo:  samplers/base_sampler.py
# Autores:
#   - Manuel Muñoz Bermejo (manuel.munnozb@estudiante.uam.es)
#   - Daniel Ortiz Buzarra (daniel.ortizbuzarra@estudiante.uam.es)
# Licencia: MIT
# -----------------------------------------------------------------------------

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Optional, Tuple

from torch import Tensor

from generative_diffusion.controllable import BaseController


class BaseSampler(ABC):
    """
    Interfaz base para *samplers* de SDE/ODE de difusión.
    """

    # ------------------------------------------------------------------ #
    # Método que cada subclase debe implementar                           #
    # ------------------------------------------------------------------ #
    @abstractmethod
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
    ) -> Tuple[Tensor, Tensor]:  # pragma: no cover
        """
        Ejecuta la integración inversa desde ``t_0`` hasta ``t_end``.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------ #
    # Helper                                                             #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _prepare_score_model(
        score_model: Callable, condition: Optional[Tensor] = None
    ) -> Callable[[Tensor, Tensor], Tensor]:
        """Devuelve un wrapper que añade la *condition* si es necesaria."""
        return (
            ConditionalWrapper(score_model, condition)
            if condition is not None
            else score_model
        )


class ConditionalWrapper:
    """Añade una condición fija (etiquetas, texto…) al *score‐model*."""

    def __init__(self, score_model: Callable, condition: Tensor) -> None:
        self._model = score_model
        self._cond = condition

    def __call__(self, x: Tensor, t: Tensor) -> Tensor:
        return self._model(x, t, self._cond)
