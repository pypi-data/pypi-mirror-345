# -----------------------------------------------------------------------------
# Proyecto: Generative AI Diffusion System - AA3 2024/2025
# Archivo:  utils/data_utils.py
# Autores:
#   - Manuel Muñoz Bermejo (manuel.munnozb@estudiante.uam.es)
#   - Daniel Ortiz Buzarra (daniel.ortizbuzarra@estudiante.uam.es)
# Licencia: MIT
# -----------------------------------------------------------------------------

from __future__ import annotations

import os
import random
from typing import Callable, List, Optional, Sequence

import torch
from torch.utils.data import DataLoader, Dataset, Subset
from torchvision import datasets, transforms


class DatasetManager:
    """
    Gestor de *datasets* (MNIST, CIFAR‑10) con opciones de
    coloreado, subconjuntos y `DataLoader` listos para entrenar.
    """

    def __init__(self, *, root_dir: str = "../data") -> None:
        self.root_dir = root_dir

    # ------------------------------------------------------------------ #
    # MNIST                                                              #
    # ------------------------------------------------------------------ #
    def mnist(
        self,
        *,
        colored: bool = True,
        random_color: bool = True,
        color_vector: Optional[Sequence[float]] = None,
        digit_subset: Optional[int] = None,
        extra_tfms: Optional[List[Callable]] = None,
        train: bool = True,
    ) -> Dataset:
        """
        Descarga y devuelve **MNIST** con opciones de coloreado.

        * Si `colored=True`, la imagen (1×28×28) se duplica a 3 canales.
        * `random_color` pinta cada imagen con RGB aleatorio (ignorado si
          `color_vector` está definido).

        Retorna únicamente el `Dataset`; genera el `DataLoader` con
        :meth:`get_dataloader`.
        """
        tfms: list[Callable] = [transforms.ToTensor()]

        if colored:
            tfms.append(lambda x: x.repeat(3, 1, 1))  # → RGB
            if color_vector is not None:
                r, g, b = map(float, color_vector)
                tfms.append(lambda x: x * torch.tensor([r, g, b]).view(3, 1, 1))
            elif random_color:
                tfms.append(
                    lambda x: x
                    * torch.tensor(
                        [random.random(), random.random(), random.random()]
                    ).view(3, 1, 1)
                )

        if extra_tfms:
            tfms.extend(extra_tfms)

        ds: Dataset = datasets.MNIST(
            root=self.root_dir,
            train=train,
            download=True,
            transform=transforms.Compose(tfms),
        )

        if digit_subset is not None:
            idx = torch.where(ds.targets == digit_subset)[0]
            ds = Subset(ds, idx)

        return ds

    # ------------------------------------------------------------------ #
    # CIFAR‑10                                                           #
    # ------------------------------------------------------------------ #
    def cifar10(
        self,
        *,
        class_subset: Optional[int] = None,
        extra_tfms: Optional[List[Callable]] = None,
        train: bool = True,
    ) -> Dataset:
        """
        Devuelve **CIFAR‑10**; permite filtrar una única clase (0–9).
        """
        tfms: list[Callable] = [transforms.ToTensor()]
        if extra_tfms:
            tfms.extend(extra_tfms)

        ds: Dataset = datasets.CIFAR10(
            root=self.root_dir,
            train=train,
            download=True,
            transform=transforms.Compose(tfms),
        )

        if class_subset is not None:
            idx = torch.where(torch.tensor(ds.targets) == class_subset)[0]
            ds = Subset(ds, idx)

        return ds

    # ------------------------------------------------------------------ #
    # DataLoader                                                         #
    # ------------------------------------------------------------------ #
    @staticmethod
    def get_dataloader(
        dataset: Dataset,
        *,
        batch_size: int = 64,
        shuffle: bool = True,
        num_workers: Optional[int] = None,
    ) -> DataLoader:
        """
        Crea un `DataLoader` óptimo para CPU disponibles.
        """
        if num_workers is None:
            num_workers = max(1, os.cpu_count() or 1)
        return DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            num_workers=num_workers,
            pin_memory=torch.cuda.is_available(),
            persistent_workers=True,
        )
