# -----------------------------------------------------------------------------
# Proyecto: Generative AI Diffusion System - AA3 2024/2025
# Archivo:  measures/__init__.py
# Autores:
#   - Manuel Muñoz Bermejo (manuel.munnozb@estudiante.uam.es)
#   - Daniel Ortiz Buzarra (daniel.ortizbuzarra@estudiante.uam.es)
# Licencia: MIT
# -----------------------------------------------------------------------------

"""
Métricas estándar para evaluar modelos de difusión:

* :func:`calculate_fid`
* :func:`calculate_inception_score`
* :func:`calculate_bpd`
"""

from __future__ import annotations

from .measures import (
    calculate_fid,
    calculate_inception_score,
    calculate_bpd,
)

__all__ = [
    "calculate_fid",
    "calculate_inception_score",
    "calculate_bpd",
]
