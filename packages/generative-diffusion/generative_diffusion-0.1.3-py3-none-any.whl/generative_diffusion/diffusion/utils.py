# -----------------------------------------------------------------------------
# Proyecto: Generative AI Diffusion System - AA3 2024/2025
# Archivo:  diffusion/utils.py
# Autores:
#   - Manuel Muñoz Bermejo (manuel.munnozb@estudiante.uam.es)
#   - Daniel Ortiz Buzarra (daniel.ortizbuzarra@estudiante.uam.es)
# Licencia: MIT
# -----------------------------------------------------------------------------

from __future__ import annotations

import logging
import colorlog
from pathlib import Path
from typing import Union

import numpy as np
import torch
from torchvision.utils import save_image


# --------------------------------------------------------------------- #
# Logger                                                                #
# --------------------------------------------------------------------- #
def setup_default_logger(name: str) -> logging.Logger:
    """Devuelve un logger INFO-level con colores según el nivel del log."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Verificar si ya tiene un StreamHandler para evitar duplicados
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        # Crear el handler
        handler = colorlog.StreamHandler()

        # Crear el formateador con colores
        formatter = colorlog.ColoredFormatter(
            fmt="%(log_color)s%(asctime)s — %(name)s — %(levelname)s — %(message)s",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
            secondary_log_colors={},
            style="%",
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


# --------------------------------------------------------------------- #
# Guardado de imágenes                                                  #
# --------------------------------------------------------------------- #
def save_images(
    logger: logging.Logger, images: torch.Tensor, path: Union[str, Path]
) -> None:
    """
    Guarda un lote de imágenes normalizado en [0,1].

    *Si* las imágenes están en [−1,1], se remapean automáticamente.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if images.min() < 0.0:
        images = (images + 1.0) * 0.5
    images = images.clamp(0, 1)

    nrow = int(np.ceil(np.sqrt(images.size(0))))
    save_image(images, path, nrow=nrow)
    logger.info("Imágenes guardadas en %s", path)
