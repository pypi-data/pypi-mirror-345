# -----------------------------------------------------------------------------
# Proyecto: Generative AI Diffusion System - AA3 2024/2025
# Archivo:  schedulers/__init__.py
# Autores:
#   - Manuel Muñoz Bermejo (manuel.munnozb@estudiante.uam.es)
#   - Daniel Ortiz Buzarra (daniel.ortizbuzarra@estudiante.uam.es)
# Licencia: MIT
# -----------------------------------------------------------------------------

"""
Colección de *noise schedulers* para modelos de difusión.

Cada scheduler implementa la misma interfaz (`BaseScheduler`) y puede
instanciarse cómodamente a través de :func:`get_scheduler`.
"""

from __future__ import annotations

from .base_scheduler import BaseScheduler
from .constant_scheduler import ConstantScheduler
from .linear_scheduler import LinearScheduler
from .cosine_scheduler import CosineScheduler

__all__ = [
    "BaseScheduler",
    "ConstantScheduler",
    "LinearScheduler",
    "CosineScheduler",
    "get_scheduler",
]

# --------------------------------------------------------------------- #
# Fábrica de schedulers                                                 #
# --------------------------------------------------------------------- #
_AVAILABLE_SCHEDULERS = {
    "constant": ConstantScheduler,
    "linear": LinearScheduler,
    "cosine": CosineScheduler,
}


def get_scheduler(scheduler_name: str, **kwargs) -> BaseScheduler:
    """
    Devuelve una instancia del scheduler solicitado.

    Raises
    ------
    ValueError
        Si `scheduler_name` no corresponde a uno registrado.
    """
    try:
        scheduler_cls = _AVAILABLE_SCHEDULERS[scheduler_name.lower()]
    except KeyError as err:
        raise ValueError(
            f"Scheduler «{scheduler_name}» no disponible. Opciones válidas: "
            f"{list(_AVAILABLE_SCHEDULERS)}"
        ) from err
    return scheduler_cls(**kwargs)
