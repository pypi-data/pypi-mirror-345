# -----------------------------------------------------------------------------
# Proyecto: Generative AI Diffusion System - AA3 2024/2025
# Archivo:  diffusion/diffusion_core.py
# Autores:
#   - Manuel Muñoz Bermejo (manuel.munnozb@estudiante.uam.es)
#   - Daniel Ortiz Buzarra (daniel.ortizbuzarra@estudiante.uam.es)
# Licencia: MIT
# -----------------------------------------------------------------------------

from __future__ import annotations

import os
import torch
from torch.utils.data import DataLoader
from torch.optim import Adam, Optimizer
import torch.nn as nn
from typing import Callable, Optional, Union, Dict, List, Tuple, Type, Any
import logging
import numpy as np
from tqdm.auto import tqdm

from generative_diffusion.diffusion.utils import setup_default_logger, save_images
from generative_diffusion.diffusion.losses import dsm_loss

from generative_diffusion.sde import BaseSDE
from generative_diffusion.samplers import BaseSampler
from generative_diffusion.score_networks import BaseScoreModel
from generative_diffusion.controllable import BaseController


class ModelNotInitializedError(Exception):
    """Error al intentar usar un modelo no inicializado."""

    pass


class DiffusionModel:
    """
    Clase principal que proporciona una interfaz unificada para entrenar modelos
    de difusión y generar imágenes.
    """

    def __init__(
        self,
        score_model_class: Type[BaseScoreModel],
        is_conditional: bool,
        sde: BaseSDE,
        sampler: BaseSampler,
        model_kwargs: Dict[str, Any] = {},
        device: Optional[Union[str, torch.device]] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Inicializa el modelo de difusión.

        Args:
            score_model_class: Clase del modelo de puntuación
                               (debe heredar de BaseScoreModel)
            is_conditional: Booleano que indica si se usa un modelo condicional
            sde: Ecuación diferencial estocástica que define el proceso de difusión
            sampler: Sampler para la generación de muestras
            model_kwargs: Argumentos adicionales para inicializar
                          el modelo de puntuación
            device: Dispositivo en el que ejecutar el modelo ('cuda' o 'cpu')
            logger: Logger opcional para seguimiento
        """
        if not issubclass(score_model_class, BaseScoreModel) and not issubclass(
            score_model_class, nn.Module
        ):
            raise TypeError(
                "score_model_class debe heredar de BaseScoreModel o nn.Module"
            )

        self.data_shape = None
        self.score_model = None
        self.score_model_class = score_model_class
        self.model_kwargs = (
            model_kwargs.copy()
        )  # Crear una copia para evitar modificaciones externas
        self.is_conditional = is_conditional
        self.sde = sde
        self.sampler = sampler
        self.is_initialized = False

        # Configurar dispositivo
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        # Configurar logger
        self.logger = logger or setup_default_logger("DiffusionModel")
        self.logger.info(
            f"Modelo de difusión inicializado en dispositivo: {self.device}"
        )

        # Si marginal_prob_std no está en model_kwargs, añadirlo automáticamente
        if "marginal_prob_std" not in self.model_kwargs:
            self.model_kwargs["marginal_prob_std"] = self.sde.sigma_t

    def _initialize_score_model(self, dataloader: Optional[DataLoader] = None) -> None:
        """
        Inicializa el modelo de puntuación.

        Args:
            dataloader: DataLoader con los datos de entrenamiento (opcional)
        """
        # Verificar si ya está inicializado
        if self.is_initialized and self.score_model is not None:
            self.logger.info(
                "El modelo ya está inicializado, no se requiere reinicialización"
            )
            return

        # Si no hay dataloader, necesitamos data_shape para la inicialización
        if dataloader is None and self.data_shape is None:
            raise ValueError(
                "Es necesario proporcionar un dataloader o tener un data_shape definido"
            )

        # Obtener el número de canales de entrada desde el dataloader o data_shape
        if dataloader is not None:
            # Obtener un elemento del dataset para determinar la forma
            if isinstance(dataloader.dataset[0], tuple):
                sample_data = dataloader.dataset[0][0]
            else:
                sample_data = dataloader.dataset[0]

            # Guardar la forma de los datos para uso futuro
            self.data_shape = sample_data.shape

            # Obtener el número de canales
            channels = sample_data.shape[0]

            # Obtener el número de clases si es necesario
            if self.is_conditional and "num_classes" not in self.model_kwargs:
                num_classes = (
                    len(dataloader.dataset.classes)
                    if hasattr(dataloader.dataset, "classes")
                    else None
                )
                self.model_kwargs["num_classes"] = num_classes
        else:
            # Usar data_shape existente
            channels = self.data_shape[0]

        # Asegurar que in_channels esté en model_kwargs
        if "in_channels" not in self.model_kwargs:
            self.model_kwargs["in_channels"] = channels

        # Inicializar el modelo de puntuación
        self.score_model = self.score_model_class(**self.model_kwargs)

        # Mover modelo al dispositivo y configurar paralelismo si es necesario
        self.score_model = torch.nn.DataParallel(self.score_model).to(self.device)
        self.is_initialized = True
        self.logger.info("Modelo de score inicializado correctamente")

    def train(
        self,
        dataloader: DataLoader,
        n_epochs: int = 10,
        optimizer: Optional[Optimizer] = None,
        lr: float = 1e-3,
        model_file_name: Optional[str] = None,
        checkpoint_dir: Optional[str] = "../checkpoints",
        checkpoint_interval: int = 5,
        callback: Optional[Callable] = None,
        resume_from: Optional[str] = None,
    ) -> Dict[str, List[float]]:
        """
        Entrena el modelo score.

        Args:
            dataloader: DataLoader con los datos de entrenamiento
            n_epochs: Número de epochs para entrenar
            optimizer: Optimizador a utilizar (si es None, se crea un Adam)
            lr: Learning rate (si se crea un optimizador nuevo)
            model_file_name: Nombre del archivo para guardar el modelo
            checkpoint_dir: Directorio para guardar checkpoints
            checkpoint_interval: Guardar checkpoint cada N epochs
            callback: Función callback opcional que se llama al final de cada epoch
            resume_from: Ruta a un checkpoint para continuar entrenamiento

        Returns:
            Diccionario con historial de pérdidas y métricas
        """
        # Determinar la forma de los datos de entrada
        if isinstance(dataloader.dataset[0], tuple):
            self.data_shape = dataloader.dataset[0][0].shape
        else:
            self.data_shape = dataloader.dataset[0].shape

        # Inicializar el modelo de puntuación si no está inicializado
        if not self.is_initialized:
            self._initialize_score_model(dataloader)

        self.score_model.train()

        # Crear optimizador si no se proporciona
        if optimizer is None:
            optimizer = Adam(self.score_model.parameters(), lr=lr)

        # Historial para seguimiento
        history = {"loss": [], "epoch": []}

        # Crear directorio de checkpoints si no existe
        if checkpoint_dir and not os.path.exists(checkpoint_dir):
            os.makedirs(checkpoint_dir)

        if model_file_name is None:
            # Componemos el nombre del archivo del modelo con
            # el nombre de la sde y si es condicional
            model_file_name = "Diffusion_model"
            model_file_name += (
                f"_{self.sde.__class__.__name__}"
                + f"_is_conditional_{self.is_conditional}"
            )

        # Cargar checkpoint si se especifica
        start_epoch = 0
        if resume_from and os.path.exists(resume_from):
            self.logger.info(f"Cargando checkpoint desde {resume_from}")
            checkpoint = torch.load(resume_from, map_location=self.device)

            # Cargar estado del modelo
            if "model_state_dict" in checkpoint:
                self.score_model.load_state_dict(checkpoint["model_state_dict"])

            # Cargar estado del optimizador si es compatible
            if "optimizer_state_dict" in checkpoint:
                try:
                    optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
                except ValueError:
                    self.logger.warning(
                        "No se pudo cargar el estado del optimizador. "
                        "Se usará un optimizador nuevo."
                    )

            # Cargar el resto del estado
            if "epoch" in checkpoint:
                start_epoch = checkpoint["epoch"]

            if "history" in checkpoint:
                history = checkpoint["history"]

            if "data_shape" in checkpoint:
                self.data_shape = checkpoint["data_shape"]

            self.logger.info(
                "Checkpoint cargado correctamente."
                + f"Reanudando desde epoch {start_epoch}"
            )

        self.logger.info(f"Iniciando entrenamiento por {n_epochs} epochs")
        epoch_iterator = tqdm(range(start_epoch, start_epoch + n_epochs), desc="Epochs")

        for epoch in epoch_iterator:
            total_loss = 0.0
            count = 0
            batch_iterator = tqdm(
                dataloader,
                desc=f"Epoch {epoch+1}/{start_epoch + n_epochs}",
                leave=False,
            )

            for batch in batch_iterator:
                # Procesar lotes de manera adecuada
                # para modelos condicionales o no condicionales
                if (
                    self.is_conditional
                    and isinstance(batch, (tuple, list))
                    and len(batch) == 2
                ):
                    x, condition = batch
                    x = x.to(self.device)
                    condition = condition.to(self.device)
                else:
                    if isinstance(batch, (tuple, list)):
                        x = batch[0]
                    else:
                        x = batch
                    x = x.to(self.device)
                    condition = None

                loss = dsm_loss(
                    score_model=self.score_model,
                    sde=self.sde,
                    x_0=x,
                    condition=condition,
                )

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                total_loss += loss.item() * x.shape[0]
                count += x.shape[0]

                # Actualizar la barra de progreso
                batch_iterator.set_postfix({"loss": loss.item()})

            # Calcular pérdida promedio por epoch
            avg_loss = total_loss / count
            history["loss"].append(avg_loss)
            history["epoch"].append(epoch)

            # Mostrar progreso
            epoch_iterator.set_postfix({"avg_loss": avg_loss})
            self.logger.info(
                f"Epoch {epoch+1}/{start_epoch + n_epochs}, Loss: {avg_loss:.6f}"
            )

            # Guardar checkpoint si corresponde
            if checkpoint_dir and (epoch + 1) % checkpoint_interval == 0:
                checkpoint_path = os.path.join(
                    checkpoint_dir, f"{model_file_name}_checkpoint_epoch_{epoch+1}.pt"
                )
                torch.save(
                    {
                        "epoch": epoch + 1,
                        "model_state_dict": self.score_model.state_dict(),
                        "optimizer_state_dict": optimizer.state_dict(),
                        "loss": avg_loss,
                        "history": history,
                        "data_shape": self.data_shape,
                        "model_kwargs": self.model_kwargs,
                    },
                    checkpoint_path,
                )
                self.logger.info(f"Checkpoint guardado en {checkpoint_path}")

            # Ejecutar callback si se proporciona
            if callback is not None:
                callback(self, epoch, history)

        # Guardar modelo final
        if checkpoint_dir:
            final_model_path = os.path.join(checkpoint_dir, f"{model_file_name}.pt")
            torch.save(
                {
                    "model_state_dict": self.score_model.state_dict(),
                    "data_shape": self.data_shape,
                    "model_kwargs": self.model_kwargs,
                    "is_conditional": self.is_conditional,
                },
                final_model_path,
            )
            self.logger.info(f"Modelo final guardado en {final_model_path}")

        return history

    def load_score_model(self, path: str) -> None:
        """
        Carga el modelo de puntuación desde un archivo guardado.

        Args:
            path: Ruta al archivo de modelo guardado
        """
        self.logger.info(f"Cargando modelo desde {path}")
        checkpoint = torch.load(path, map_location=self.device, weights_only=False)

        # Extraer data_shape del checkpoint si está disponible
        if "data_shape" in checkpoint:
            self.data_shape = checkpoint["data_shape"]
            self.logger.info(f"Forma de datos cargada: {self.data_shape}")

        # Actualizar model_kwargs si están disponibles en el checkpoint
        if "model_kwargs" in checkpoint:
            # Actualizar model_kwargs pero mantener marginal_prob_std actual
            temp_std = self.model_kwargs.get("marginal_prob_std", None)
            self.model_kwargs.update(checkpoint["model_kwargs"])
            if temp_std is not None:
                self.model_kwargs["marginal_prob_std"] = temp_std
            self.logger.info("Parámetros del modelo actualizados desde checkpoint")

        # Actualizar is_conditional si está disponible
        if "is_conditional" in checkpoint:
            self.is_conditional = checkpoint["is_conditional"]

        # Inicializar el modelo si no está inicializado
        if not self.is_initialized:
            if self.data_shape is None:
                raise ValueError(
                    "No se puede inicializar el modelo sin data_shape. "
                    "El checkpoint no contiene esta información."
                )
            self._initialize_score_model()

        # Cargar los pesos del modelo
        if "model_state_dict" in checkpoint:
            self.score_model.load_state_dict(checkpoint["model_state_dict"])
        elif "score_model_state_dict" in checkpoint:
            self.score_model.load_state_dict(checkpoint["score_model_state_dict"])
        else:
            # Intentar cargar directamente como state_dict
            try:
                self.score_model.load_state_dict(checkpoint)
            except Exception as e:
                raise ValueError(f"No se pudo cargar el estado del modelo: {str(e)}")

        self.logger.info("Modelo cargado correctamente")

    def generate(
        self,
        x_0: Optional[torch.Tensor] = None,
        n_samples: int = 16,
        condition: Optional[Union[List, torch.Tensor]] = None,
        t_0: float = 1.0,
        t_end: float = 1e-3,
        n_steps: int = 500,
        seed: Optional[int] = None,
        save_path: Optional[str] = None,
        return_sequence: bool = False,
        model_path: Optional[str] = None,
        data_shape: Optional[Tuple[int, ...]] = None,
        controller: Optional[BaseController] = None,
    ) -> Union[
        torch.Tensor,
        Tuple[torch.Tensor, torch.Tensor],
        Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]],
    ]:
        """
        Genera muestras utilizando el modelo de difusión entrenado.

        Args:
            x_0 (torch.Tensor): Tensor inicial para la generación [B, C, H, W].
            n_samples (int): Número de muestras a generar.
            condition (Any, optional): Condición opcional (por ejemplo, etiquetas).
            t_0 (float): Tiempo inicial del proceso de muestreo.
            t_end (float): Tiempo final del proceso de muestreo.
            n_steps (int): Número de pasos de muestreo.
            seed (int, optional): Semilla para reproducibilidad.
            save_path (str, optional): Ruta para guardar las imágenes generadas.
            return_sequence (bool): Si es True, devuelve toda la secuencia.
            model_path (str, optional): Ruta al modelo preentrenado.
            data_shape (tuple, optional): Forma de los datos.
            controller (Any, optional): Controlador para generación controlada.

        Returns:
            tuple: Si return_sequence es False, devuelve (muestras, condiciones)
                - muestras (torch.Tensor): Tensor de imágenes generadas [B, C, H, W].
                - condiciones (torch.Tensor or None): Tensor con condiciones [B] o None.

            tuple: Si return_sequence es True, devuelve (tiempos, muestras, condiciones)
                - tiempos (torch.Tensor): Tiempos de muestreo [n_steps].
                - muestras (torch.Tensor): Secuencia de imágenes [n_steps, B, C, H, W].
                - condiciones (torch.Tensor or None): Tensor con condiciones [B] o None.
        """
        # Cargar modelo pre-entrenado si se especifica
        if model_path is not None:
            self.load_score_model(model_path)

        # Si se proporciona data_shape, guardarlo
        if data_shape is not None:
            self.data_shape = data_shape

        # Verificar que el modelo está inicializado
        if not self.is_initialized:
            if self.data_shape is None:
                raise ModelNotInitializedError(
                    "El modelo no está inicializado. Debe entrenar el modelo primero, "
                    "cargar un modelo pre-entrenado con model_path,"
                    "o proporcionar data_shape."
                )
            self._initialize_score_model()

        # Verificar que tenemos una forma de datos válida
        if self.data_shape is None:
            raise ValueError(
                "No se ha especificado data_shape. Debe entrenar el modelo primero"
                " o proporcionar data_shape."
            )

        # Transformar la condición a tensor si es necesario
        if condition is not None:
            if isinstance(condition, list):
                condition = torch.tensor(
                    condition, dtype=torch.long, device=self.device
                )
            elif isinstance(condition, torch.Tensor):
                condition = condition.long().to(self.device)
            else:
                raise ValueError(
                    "La condición debe ser una lista o un tensor de PyTorch"
                )

        # Verificar que si se proporciona una condición, el modelo es condicional
        if condition is not None and not self.is_conditional:
            raise ValueError(
                "El modelo no es condicional, pero se proporcionó una condición"
            )

        # Si el modelo es condicional pero no se proporcionó condición, verificar
        if self.is_conditional and condition is None:
            # Generamos nosotros internamente un tensor de condición aleatorio
            condition = torch.randint(
                0, self.model_kwargs["num_classes"], (n_samples,), device=self.device
            )
            # Avismos de que como no se ha proporcionado la condición,
            # se usará una aleatoria
            self.logger.warning(
                "No se proporcionó condición, se usará un tensor aleatorio de condición"
            )

        # Fijar semilla si se proporciona
        if seed is not None:
            torch.manual_seed(seed)
            np.random.seed(seed)

        # verificar que x_0 tiene la forma correcta si se proporciona
        # si x_0 es None, se generará ruido aleatorio normal
        if x_0 is not None:
            if x_0.shape[0] != n_samples:
                raise ValueError(
                    f"El tamaño del batch de x_0 ({x_0.shape[0]})"
                    + f"no coincide con n_samples ({n_samples})"
                )
            if x_0.shape[1:] != self.data_shape:
                raise ValueError(
                    f"La forma de x_0 ({x_0.shape[1:]})"
                    + f"no coincide con data_shape ({self.data_shape})"
                )
            x_T = x_0.to(self.device)
        else:
            # Crear una distribución inicial x_T ~ N(0, I)
            x_T = torch.randn(n_samples, *self.data_shape, device=self.device)

        self.score_model.eval()

        self.logger.info(f"Generando {n_samples} muestras con {n_steps} pasos")

        with torch.no_grad():
            # Generar muestras usando el sampler
            times, samples = self.sampler.sample(
                x_0=x_T,
                sde=self.sde,
                score_model=self.score_model,
                t_0=t_0,
                t_end=t_end,
                n_steps=n_steps,
                condition=condition,
                seed=seed,
                controller=controller,
            )

        # Guardar imágenes si se proporciona una ruta
        if save_path:
            save_images(
                self.logger, samples[-1] if return_sequence else samples, save_path
            )

        # Devolver el resultado y las condiciones utilizadas
        if return_sequence:
            return (times, samples), condition
        else:
            return samples[-1], condition

    def impute(
        self,
        image: torch.Tensor,
        mask: torch.Tensor,
        condition: Optional[Union[List, torch.Tensor]] = None,
        t_0: float = 1.0,
        t_end: float = 1e-3,
        n_steps: int = 500,
        seed: Optional[int] = None,
        save_path: Optional[str] = None,
        return_sequence: bool = False,
        model_path: Optional[str] = None,
    ) -> Union[
        Tuple[torch.Tensor, Optional[torch.Tensor]],
        Tuple[Tuple[torch.Tensor, torch.Tensor], Optional[torch.Tensor]],
    ]:
        """
        Realiza imputación en una imagen utilizando el modelo de difusión.

        Args:
            image (torch.Tensor): Imagen o imágenes a imputar [B, C, H, W].
            mask (torch.Tensor): Máscara binaria con píxeles conocidos.
                Puede tener forma [B, 1, H, W] o [B, C, H, W].
            condition (Any, optional): Condición opcional (por ejemplo, etiquetas).
            t_0 (float): Tiempo inicial del proceso de imputación.
            t_end (float): Tiempo final del proceso de imputación.
            n_steps (int): Número de pasos para imputar.
            seed (int, optional): Semilla para reproducibilidad.
            save_path (str, optional): Ruta para guardar imágenes generadas.
            return_sequence (bool): Si es True, devuelve toda la secuencia.
            model_path (str, optional): Ruta al modelo preentrenado.

        Returns:
            tuple: Si return_sequence es False, devuelve (imputaciones, condiciones)
                - imputaciones (torch.Tensor): Tensor de imágenes imputadas [B, C, H, W]
                - condiciones (torch.Tensor or None): Condiciones usadas [B] o None.

            tuple: Si return_sequence es True, devuelve ((tiempos, imputaciones), condiciones)
                - tiempos (torch.Tensor): Tiempos del proceso [n_steps].
                - imputaciones (torch.Tensor): Secuencia imputada [n_steps, B, C, H, W].
                - condiciones (torch.Tensor or None): Condiciones usadas [B] o None.
        """
        # Cargar modelo pre-entrenado si se especifica
        if model_path is not None:
            self.load_score_model(model_path)

        # Verificar que el modelo está inicializado
        if not self.is_initialized:
            if image is not None:
                # Usar la forma de la imagen de entrada para inicializar
                self.data_shape = image.shape[1:]
                self._initialize_score_model()
            else:
                raise ModelNotInitializedError(
                    "El modelo no está inicializado. Debe entrenar el modelo primero, "
                    "cargar un modelo pre-entrenado con model_path, "
                    "o proporcionar una imagen válida."
                )

        # Mover tensores al dispositivo del modelo
        image = image.to(self.device)
        mask = mask.to(self.device)

        # Verificar formas de los tensores
        if image.shape[0] != mask.shape[0]:
            raise ValueError(
                f"El batch size de la imagen ({image.shape[0]})"
                + f"no coincide con el de la máscara ({mask.shape[0]})"
            )

        # Crear controlador de imputación
        from generative_diffusion.controllable import ImputationController

        controller = ImputationController(mask=mask)
        x_0 = controller.prepare_initial(x_t=image)

        # Usar el método generate para realizar la imputación
        result = self.generate(
            x_0=x_0,
            n_samples=image.shape[0],
            condition=condition,
            t_0=t_0,
            t_end=t_end,
            n_steps=n_steps,
            seed=seed,
            save_path=save_path,
            return_sequence=return_sequence,
            controller=controller,
        )

        return result

    def evaluate(
        self,
        real_dataloader: DataLoader,
        generated_samples: Optional[torch.Tensor] = None,
        n_generated_samples: int = 1000,
        condition: Optional[Union[List, torch.Tensor]] = None,
        metrics: List[str] = ["fid", "is", "bpd"],
        n_steps: int = 500,
        batch_size: int = 32,
        seed: Optional[int] = None,
    ) -> Dict[str, float]:
        """
        Evalúa la calidad de las imágenes generadas usando métricas estándar.

        Args:
            real_dataloader: DataLoader con imágenes reales para comparación
            generated_samples: Tensor con imágenes ya generadas (opcional)
            n_generated_samples: Número de muestras a generar para evaluación
            condition: Condición opcional para generación condicional (ej. etiquetas)
            metrics: Lista de métricas a calcular ("fid", "is", "bpd")
            n_steps: Número de pasos para el muestreo
            batch_size: Tamaño del lote para procesamiento de métricas
            seed: Semilla para reproducibilidad

        Returns:
            Diccionario con los valores de las métricas calculadas
        """
        results = {}

        # Verificar que el modelo está inicializado
        if not self.is_initialized:
            raise ModelNotInitializedError(
                "El modelo no está inicializado. "
                "Debe entrenar el modelo primero o cargar un modelo pre-entrenado."
            )

        if generated_samples is not None:
            n_generated_samples = generated_samples.shape[0]
            generated_samples = generated_samples.to(self.device)
        else:
            # Si no se proporcionan muestras generadas, generarlas
            self.logger.info("Generando nuevas muestras para evaluación")
            generated_samples, _ = self.generate(
                n_samples=n_generated_samples,
                condition=condition,
                n_steps=n_steps,
                seed=seed,
            )

        # Recopilar imágenes reales
        self.logger.info("Recopilando imágenes reales para comparación")
        real_samples = []
        n_real_collected = 0

        for batch in tqdm(real_dataloader, desc="Recopilando imágenes reales"):
            if isinstance(batch, tuple) or isinstance(batch, list):
                x = batch[0]
            else:
                x = batch
            real_samples.append(x)
            n_real_collected += x.shape[0]

            # Limitar la cantidad de imágenes reales
            # para que sea similar a las generadas
            if n_real_collected >= n_generated_samples:
                break

        real_samples = torch.cat(real_samples, dim=0)[
            :n_generated_samples
        ]  # Limitar al mismo número que las generadas

        # Calcular métricas
        if "fid" in metrics:
            self.logger.info("Calculando FID (Fréchet Inception Distance)...")
            from generative_diffusion.measures import calculate_fid

            results["fid"] = calculate_fid(
                real_samples,
                generated_samples,
                batch_size=batch_size,
                device=self.device,
            )
            self.logger.info(f"FID: {results['fid']:.4f} (menor es mejor)")

        if "is" in metrics:
            self.logger.info("Calculando IS (Inception Score)...")
            from generative_diffusion.measures import calculate_inception_score

            results["is"] = calculate_inception_score(
                generated_samples, batch_size=batch_size, device=self.device
            )
            self.logger.info(f"Inception Score: {results['is']:.4f} (mayor es mejor)")

        if "bpd" in metrics:
            self.logger.info("Calculando BPD (Bits Per Dimension)...")
            from generative_diffusion.measures import calculate_bpd

            results["bpd"] = calculate_bpd(
                self.score_model,
                self.sde,
                real_dataloader,
                n_samples=min(n_generated_samples, len(real_dataloader.dataset)),
                device=self.device,
            )
            self.logger.info(f"BPD: {results['bpd']:.4f} (menor es mejor)")

        return results
