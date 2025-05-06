# -----------------------------------------------------------------------------
# Proyecto: Generative AI Diffusion System - AA3 2024/2025
# Archivo:  score_networks/base_score_model.py
# Autores:
#   - Manuel Muñoz Bermejo (manuel.munnozb@estudiante.uam.es)
#   - Daniel Ortiz Buzarra (daniel.ortizbuzarra@estudiante.uam.es)
# Licencia: MIT
# -----------------------------------------------------------------------------

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Optional

import torch.nn as nn
from torch import Tensor


class BaseScoreModel(nn.Module, ABC):
    """
    Clase base abstracta para modelos de puntuación (score‑based).

    Todos los modelos concretos deben:
    1. Recibir la función ``marginal_prob_std`` de la SDE.
    2. Implementar ``forward(x, t, condition=None)`` devolviendo el score ∇ₓ log p(xₜ).
    """

    def __init__(
        self,
        marginal_prob_std: Callable[[Tensor], Tensor],
        in_channels: int,
        out_channels: Optional[int] = None,
        num_classes: Optional[int] = None,
    ) -> None:
        super().__init__()
        self.marginal_prob_std = marginal_prob_std
        self.in_channels = in_channels
        self.out_channels = out_channels if out_channels is not None else in_channels
        self.num_classes = num_classes
        self.is_conditional = num_classes is not None

    # ------------------------------------------------------------------ #
    # Métodos abstractos
    # ------------------------------------------------------------------ #
    @abstractmethod
    def forward(
        self,
        x: Tensor,
        t: Tensor,
        condition: Optional[Tensor] = None,
    ) -> Tensor:  # pragma: no cover
        """
        Calcula el score para un lote de muestras.

        Raises
        ------
        NotImplementedError
            Debe implementarse en cada subclase.
        """
        raise NotImplementedError
