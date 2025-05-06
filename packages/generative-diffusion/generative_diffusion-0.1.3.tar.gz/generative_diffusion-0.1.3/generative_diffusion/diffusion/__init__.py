# -----------------------------------------------------------------------------
# Proyecto: Generative AI Diffusion System - AA3 2024/2025
# Archivo:  diffusion/__init__.py
# Autores:
#   - Manuel Muñoz Bermejo (manuel.munnozb@estudiante.uam.es)
#   - Daniel Ortiz Buzarra (daniel.ortizbuzarra@estudiante.uam.es)
# Licencia: MIT
# -----------------------------------------------------------------------------

"""
Núcleo de alto nivel: creación, entrenamiento y uso de modelos de difusión.
"""

from __future__ import annotations

from .diffusion_core import DiffusionModel
from .diffusion_factory import ModelFactory
from .utils import save_images, setup_default_logger

__all__ = [
    "DiffusionModel",
    "ModelFactory",
    "save_images",
    "setup_default_logger",
    "create_model",
]


def create_model(*args, **kwargs):
    """Atajo a :meth:`ModelFactory.create`."""
    return ModelFactory.create(*args, **kwargs)
