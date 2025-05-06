# -----------------------------------------------------------------------------
# Proyecto: Generative AI Diffusion System - AA3 2024/2025
# Archivo:  diffusion/diffusion_factory.py
# Autores:
#   - Manuel Muñoz Bermejo (manuel.munnozb@estudiante.uam.es)
#   - Daniel Ortiz Buzarra (daniel.ortizbuzarra@estudiante.uam.es)
# Licencia: MIT
# -----------------------------------------------------------------------------

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple, Type, Union

import torch
from torch import nn

from generative_diffusion.score_networks import BaseScoreModel


# --------------------------------------------------------------------- #
# Factory                                                               #
# --------------------------------------------------------------------- #
class ModelFactory:
    """
    Crea un :class:`DiffusionModel` completamente configurado.
    """

    @staticmethod
    def create(
        *,
        score_model_class: Type[BaseScoreModel],
        is_conditional: bool,
        sde_name: str,
        sampler_name: str,
        scheduler_name: Optional[str] = None,
        model_kwargs: Optional[Dict[str, Any]] = None,
        sde_kwargs: Optional[Dict[str, Any]] = None,
        sampler_kwargs: Optional[Dict[str, Any]] = None,
        scheduler_kwargs: Optional[Dict[str, Any]] = None,
        device: Optional[Union[str, torch.device]] = None,
        checkpoint_path: Optional[str] = None,
        data_shape: Optional[Tuple[int, ...]] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Crea una instancia del modelo de difusión configurado
        con los componentes especificados.

        Esta función estática permite construir una instancia
        completa de `DiffusionModel`, incluyendo el modelo de score,
        la SDE, el sampler, el scheduler (si aplica), así como todos los argumentos
        personalizados necesarios para su inicialización.

        Parameters
        ----------
        score_model_class : Type[BaseScoreModel]
            Clase del modelo de score. Debe heredar de `BaseScoreModel`
            o `torch.nn.Module`.
        is_conditional : bool
            Indica si el modelo es condicional.
        sde_name : str
            Nombre de la SDE a utilizar. Valores válidos:
            - "ve_sde"     : Variance Exploding SDE
            - "vp_sde"     : Variance Preserving SDE
            - "subvp_sde"  : Sub-Variance Preserving SDE
        sampler_name : str
            Nombre del método de muestreo. Valores válidos:
            - "euler_maruyama"
            - "predictor_corrector"
            - "probability_flow_ode"
            - "exponential_integrator"
        scheduler_name : Optional[str], default=None
            Nombre del scheduler temporal (si la SDE lo requiere). Valores válidos:
            - "constant"
            - "linear"
            - "cosine"
        model_kwargs : Optional[Dict[str, Any]], default=None
            Argumentos adicionales para inicializar el modelo de score.
        sde_kwargs : Optional[Dict[str, Any]], default=None
            Argumentos adicionales para configurar la SDE.
        sampler_kwargs : Optional[Dict[str, Any]], default=None
            Argumentos adicionales para configurar el sampler.
        scheduler_kwargs : Optional[Dict[str, Any]], default=None
            Argumentos adicionales para configurar el scheduler (si aplica).
        device : Optional[Union[str, torch.device]], default=None
            Dispositivo de ejecución, por ejemplo `"cuda"` o `"cpu"`.
        checkpoint_path : Optional[str], default=None
            Ruta al archivo `.pt` o `.ckpt` con los pesos del modelo entrenado.
        data_shape : Optional[Tuple[int, ...]], default=None
            Forma esperada de los datos de entrada (ej. `(3, 32, 32)` para imágenes).
        logger : Optional[logging.Logger], default=None
            Logger opcional para registrar el proceso.

        Returns
        -------
        DiffusionModel
            Instancia completamente configurada del modelo de difusión.

        Raises
        ------
        TypeError
            Si `score_model_class` no hereda de `BaseScoreModel` o `nn.Module`.
        ValueError
            Si el nombre del sampler, scheduler o SDE no corresponde a los disponibles.
        """

        # imports tardíos para evitar ciclos
        from generative_diffusion.sde import get_sde
        from generative_diffusion.samplers import get_sampler
        from generative_diffusion.schedulers import get_scheduler
        from .diffusion_core import DiffusionModel

        if not issubclass(score_model_class, (BaseScoreModel, nn.Module)):
            raise TypeError(
                "`score_model_class` debe heredar de BaseScoreModel o nn.Module."
            )

        model_kwargs = model_kwargs or {}
        sde_kwargs = sde_kwargs or {}
        sampler_kwargs = sampler_kwargs or {}
        scheduler_kwargs = scheduler_kwargs or {}

        # scheduler (solo si la SDE lo requiere)
        if scheduler_name is not None:
            scheduler = get_scheduler(scheduler_name, **scheduler_kwargs)
            sde_kwargs["scheduler"] = scheduler

        sde = get_sde(sde_name, **sde_kwargs)
        sampler = get_sampler(sampler_name, **sampler_kwargs)

        model_kwargs = model_kwargs.copy()
        model_kwargs.setdefault("marginal_prob_std", sde.sigma_t)

        diffusion = DiffusionModel(
            score_model_class=score_model_class,
            is_conditional=is_conditional,
            sde=sde,
            sampler=sampler,
            model_kwargs=model_kwargs,
            device=device,
            logger=logger,
        )

        if data_shape is not None:
            diffusion.data_shape = data_shape
        if checkpoint_path is not None:
            diffusion.load_score_model(checkpoint_path)

        return diffusion
