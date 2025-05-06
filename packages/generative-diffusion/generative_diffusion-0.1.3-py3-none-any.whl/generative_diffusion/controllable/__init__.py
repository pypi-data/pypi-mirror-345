# -----------------------------------------------------------------------------
# Proyecto: Generative AI Diffusion System - AA3 2024/2025
# Archivo: controllable/__init__.py
# Autores:
#   - Manuel Muñoz Bermejo (manuel.munnozb@estudiante.uam.es)
#   - Daniel Ortiz Buzarra (daniel.ortizbuzarra@estudiante.uam.es)
# Licencia: MIT
# -----------------------------------------------------------------------------

from __future__ import annotations

from typing import Dict, Type

from .base_controller import BaseController
from .imputation_controller import ImputationController
from .imputation_mask_functions import (
    border_mask,
    center_square_mask,
    random_mask,
)

__all__ = [
    # controladores
    "BaseController",
    "ImputationController",
    # fábricas
    "get_controller",
    # utilidades de máscaras
    "center_square_mask",
    "border_mask",
    "random_mask",
]

# --------------------------------------------------------------------- #
# Registro de controladores disponibles                                 #
# --------------------------------------------------------------------- #
_AVAILABLE_CONTROLLERS: Dict[str, Type[BaseController]] = {
    "imputation": ImputationController,
}


def get_controller(controller_name: str, **kwargs) -> BaseController:
    """
    Devuelve una instancia del controlador solicitado.

    Raises
    ------
    ValueError
        Si el nombre no está registrado.
    """
    try:
        controller_cls = _AVAILABLE_CONTROLLERS[controller_name.lower()]
    except KeyError as err:
        raise ValueError(
            f"Controlador «{controller_name}» no disponible. "
            f"Opciones: {list(_AVAILABLE_CONTROLLERS)}"
        ) from err
    return controller_cls(**kwargs)
