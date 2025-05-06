# -----------------------------------------------------------------------------
# Proyecto: Generative AI Diffusion System - AA3 2024/2025
# Archivo:  sde/__init__.py
# Autores:
#   - Manuel Muñoz Bermejo (manuel.munnozb@estudiante.uam.es)
#   - Daniel Ortiz Buzarra (daniel.ortizbuzarra@estudiante.uam.es)
# Licencia: MIT
# -----------------------------------------------------------------------------

"""
Implementaciones de SDE para procesos de difusión.
"""

from __future__ import annotations

from .base_sde import BaseSDE
from .scheduler_sde import SchedulerBasedSDE, MissingSchedulerError
from .ve_sde import VESDE
from .vp_sde import VPSDE
from .subvp_sde import SubVPSDE

__all__ = [
    "BaseSDE",
    "SchedulerBasedSDE",
    "MissingSchedulerError",
    "VESDE",
    "VPSDE",
    "SubVPSDE",
    "get_sde",
]

# --------------------------------------------------------------------- #
# Fábrica                                                               #
# --------------------------------------------------------------------- #
_SDE_REGISTRY = {
    "ve_sde": VESDE,
    "vp_sde": VPSDE,
    "subvp_sde": SubVPSDE,
}


def get_sde(sde_name: str, **kwargs) -> BaseSDE:
    """
    Devuelve una SDE por nombre.

    Raises
    ------
    ValueError
        Si el nombre no existe.
    """
    try:
        cls = _SDE_REGISTRY[sde_name.lower()]
    except KeyError as err:
        raise ValueError(
            f"SDE «{sde_name}» no disponible. Opciones: {list(_SDE_REGISTRY)}"
        ) from err
    return cls(**kwargs)
