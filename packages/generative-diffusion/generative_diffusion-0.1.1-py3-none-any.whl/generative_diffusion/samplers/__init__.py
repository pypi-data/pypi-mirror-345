# -----------------------------------------------------------------------------
# Proyecto: Generative AI Diffusion System - AA3 2024/2025
# Archivo:  samplers/__init__.py
# Autores:
#   - Manuel Muñoz Bermejo (manuel.munnozb@estudiante.uam.es)
#   - Daniel Ortiz Buzarra (daniel.ortizbuzarra@estudiante.uam.es)
# Licencia: MIT
# -----------------------------------------------------------------------------

"""
Colección de *samplers* para procesos de difusión.

Incluye:

* Euler‐Maruyama (`EulerMaruyamaSampler`)
* Predictor–Corrector (`PredictorCorrectorSampler`)
* Probability‑Flow ODE (`ProbabilityFlowODESampler`)
* Exponential Integrator (`ExponentialIntegratorSampler`)
"""

from __future__ import annotations

from .base_sampler import BaseSampler, ConditionalWrapper
from .euler_maruyama import EulerMaruyamaSampler
from .predictor_corrector import PredictorCorrectorSampler
from .probability_flow_ode import ProbabilityFlowODESampler
from .exponential_integrator import ExponentialIntegratorSampler

__all__ = [
    "BaseSampler",
    "ConditionalWrapper",
    "EulerMaruyamaSampler",
    "PredictorCorrectorSampler",
    "ProbabilityFlowODESampler",
    "ExponentialIntegratorSampler",
    "get_sampler",
]

# --------------------------------------------------------------------- #
# Fábrica                                                               #
# --------------------------------------------------------------------- #
_AVAILABLE_SAMPLERS = {
    "euler_maruyama": EulerMaruyamaSampler,
    "predictor_corrector": PredictorCorrectorSampler,
    "probability_flow_ode": ProbabilityFlowODESampler,
    "exponential_integrator": ExponentialIntegratorSampler,
}


def get_sampler(sampler_name: str, **kwargs) -> BaseSampler:
    """
    Devuelve una instancia del sampler solicitado.

    Raises
    ------
    ValueError
        Si el nombre no está registrado.
    """
    try:
        sampler_cls = _AVAILABLE_SAMPLERS[sampler_name.lower()]
    except KeyError as err:
        raise ValueError(
            f"Sampler «{sampler_name}» no disponible."
            + f"Opciones: {list(_AVAILABLE_SAMPLERS)}"
        ) from err
    return sampler_cls(**kwargs)
