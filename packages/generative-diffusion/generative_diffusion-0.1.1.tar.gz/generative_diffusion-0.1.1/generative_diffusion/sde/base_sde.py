# -----------------------------------------------------------------------------
# Proyecto: Generative AI Diffusion System - AA3 2024/2025
# Archivo:  sde/base_sde.py
# Autores:
#   - Manuel Muñoz Bermejo (manuel.munnozb@estudiante.uam.es)
#   - Daniel Ortiz Buzarra (daniel.ortizbuzarra@estudiante.uam.es)
# Licencia: MIT
# -----------------------------------------------------------------------------

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Tuple

from torch import Tensor


class BaseSDE(ABC):
    """
    Interfaz base para las EDE/SDE empleadas en modelos de difusión.
    """

    def _broadcast(self, tensor: Tensor, ref_tensor: Tensor) -> Tensor:
        """Redimensiona el tensor para hacer broadcasting con ref_tensor."""
        return tensor.view(-1, *([1] * (ref_tensor.ndim - 1)))

    # ------------------------------------------------------------------ #
    # Parámetros infinitesimales                                         #
    # ------------------------------------------------------------------ #
    @abstractmethod
    def drift(self, x_t: Tensor, t: Tensor) -> Tensor:
        """f(x, t)   — termino determinista."""
        raise NotImplementedError

    @abstractmethod
    def diffusion(self, t: Tensor) -> Tensor:
        """g(t)      — coeficiente de ruido multiplicativo."""
        raise NotImplementedError

    # ------------------------------------------------------------------ #
    # Distribución marginal p(xₜ|x₀)                                     #
    # ------------------------------------------------------------------ #
    @abstractmethod
    def mu_t(self, x_0: Tensor, t: Tensor) -> Tensor:
        """Media de p(xₜ | x₀)."""
        raise NotImplementedError

    @abstractmethod
    def sigma_t(self, t: Tensor) -> Tensor:
        """Desv. estándar de p(xₜ | x₀)."""
        raise NotImplementedError

    def marginal_prob(self, x_0: Tensor, t: Tensor) -> Tuple[Tensor, Tensor]:
        """Devuelve (μₜ, σₜ)."""
        return self.mu_t(x_0, t), self.sigma_t(t)

    # ------------------------------------------------------------------ #
    # Dinámica backward                                                  #
    # ------------------------------------------------------------------ #
    @abstractmethod
    def backward_drift(self, x_t: Tensor, t: Tensor, score_fn: Callable) -> Tensor:
        """f̄(x, t) para la SDE inversa."""
        raise NotImplementedError
