# -----------------------------------------------------------------------------
# Proyecto: Generative AI Diffusion System - AA3 2024/2025
# Archivo:  schedulers/base_scheduler.py
# Autores:
#   - Manuel Muñoz Bermejo (manuel.munnozb@estudiante.uam.es)
#   - Daniel Ortiz Buzarra (daniel.ortizbuzarra@estudiante.uam.es)
# Licencia: MIT
# -----------------------------------------------------------------------------

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Final

from torch import Tensor


class BaseScheduler(ABC):
    """
    Interfaz común para *noise schedulers*.

    Cada implementación debe definir:

    * ``beta(t)``  – coeficiente instantáneo β(t) ∈ (0, 1).
    * ``alpha_bar(t)`` – producto acumulado ᾱ(t) = exp(−∫₀ᵗ β(s)ds).
    """

    _EPS: Final[float] = 1e-8  # para evitar divisiones por cero

    # ------------------------------------------------------------------ #
    # Métodos que toda subclase debe implementar                          #
    # ------------------------------------------------------------------ #
    @abstractmethod
    def beta(self, t: Tensor) -> Tensor:  # noqa: D401
        """Devuelve β(t)."""
        raise NotImplementedError

    @abstractmethod
    def alpha_bar(self, t: Tensor) -> Tensor:  # noqa: D401
        """Devuelve ᾱ(t)."""
        raise NotImplementedError

    # ------------------------------------------------------------------ #
    # Utilidades                                                         #
    # ------------------------------------------------------------------ #
    def alpha(self, t: Tensor) -> Tensor:
        """Calcula α(t) = 1 − β(t)."""
        return 1.0 - self.beta(t)
