# -----------------------------------------------------------------------------
# Proyecto: Generative AI Diffusion System - AA3 2024/2025
# Archivo:  utils/visualization_utils.py
# Autores:
#   - Manuel Muñoz Bermejo (manuel.munnozb@estudiante.uam.es)
#   - Daniel Ortiz Buzarra (daniel.ortizbuzarra@estudiante.uam.es)
# Licencia: MIT
# -----------------------------------------------------------------------------

from __future__ import annotations

from typing import Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import torch
from torch.utils.data import DataLoader


# --------------------------------------------------------------------- #
# Helpers                                                               #
# --------------------------------------------------------------------- #
def _tensor_to_img(x: torch.Tensor) -> np.ndarray:
    """
    Convierte un tensor [C,H,W] a un array NHWC normalizado en [0,1].
    """
    if x.ndim != 3:
        raise ValueError("Se esperaba tensor 3‑D [C,H,W].")
    x = x.detach().cpu()
    if x.size(0) == 1:
        x = x.repeat(3, 1, 1)
    x = x.permute(1, 2, 0).clamp(0, 1).numpy()
    return x


# --------------------------------------------------------------------- #
# Grids de imágenes                                                     #
# --------------------------------------------------------------------- #
def show_images(
    data: Union[torch.Tensor, DataLoader, List[torch.Tensor]],
    n_images: int = 16,
    title: str = "Imágenes",
    labels: Optional[Union[torch.Tensor, List[int]]] = None,
    nrow: int = 4,
    figsize: Tuple[int, int] = (12, 6),
    denormalize: bool = False,
    return_fig: bool = False,
) -> Optional[plt.Figure]:
    """
    Muestra un grid de imágenes con sus etiquetas opcionales.
    """
    if isinstance(data, DataLoader):
        batch = next(iter(data))
        if isinstance(batch, (list, tuple)) and len(batch) >= 2:
            images, batch_labels = batch[0], batch[1]
        else:
            images, batch_labels = batch, None
    elif isinstance(data, list) and all(isinstance(img, torch.Tensor) for img in data):
        images = torch.stack(data)
        batch_labels = labels
    else:
        images = data
        batch_labels = labels

    n_images = min(n_images, images.size(0))
    images = images[:n_images]

    if batch_labels is not None:
        batch_labels = batch_labels[:n_images]

    if images.dim() == 4:
        if images.size(1) > 3 and images.size(3) <= 3:
            images = images.permute(0, 3, 1, 2)

    if denormalize:
        images = (images + 1) / 2.0

    if n_images <= 4:
        figsize = (4, 2)
    elif n_images <= 8:
        figsize = (8, 4)

    ncols = min(nrow, n_images)
    nrows = (n_images + ncols - 1) // ncols

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize)
    fig.suptitle(title, fontsize=16)

    if nrows == 1 and ncols == 1:
        axes = np.array([axes])
    elif nrows == 1 or ncols == 1:
        axes = axes.flatten()

    for i in range(n_images):
        row, col = i // ncols, i % ncols
        ax = axes[row, col] if nrows > 1 and ncols > 1 else axes[i]
        img = images[i].permute(1, 2, 0).cpu().detach().numpy()
        if img.shape[2] == 1:
            img = img.squeeze(2)
            ax.imshow(img, cmap="gray")
        else:
            img = np.clip(img, 0, 1)
            ax.imshow(img)
        if batch_labels is not None:
            label = (
                batch_labels[i].item()
                if hasattr(batch_labels[i], "item")
                else batch_labels[i]
            )
            ax.set_title(f"Label: {label}", fontsize=10)
        ax.axis("off")

    for i in range(n_images, nrows * ncols):
        row, col = i // ncols, i % ncols
        ax = axes[row, col] if nrows > 1 and ncols > 1 else axes[i]
        ax.axis("off")
        ax.set_visible(False)

    plt.tight_layout()
    if return_fig:
        return fig
    plt.show()
    plt.close()
    return None


# --------------------------------------------------------------------- #
# Proceso de generación                                                 #
# --------------------------------------------------------------------- #
def show_generation_process(
    image_sequence: torch.Tensor,
    times: Optional[torch.Tensor] = None,
    num_steps_to_show: int = 8,
    title: str = "Proceso de generación",
    figsize: Tuple[int, int] = (12, 6),
    return_fig: bool = False,
) -> Optional[plt.Figure]:
    """
    Muestra el proceso de generación/difusión a través del tiempo.
    """
    T, _ = image_sequence.shape[:2]
    step_indices = np.linspace(0, T - 1, num_steps_to_show, dtype=int)
    selected_images = image_sequence[step_indices, 0]

    fig, axes = plt.subplots(1, num_steps_to_show, figsize=figsize)
    fig.suptitle(title, fontsize=16)

    for i, (ax, img) in enumerate(zip(axes, selected_images)):
        img_np = img.permute(1, 2, 0).cpu().detach().numpy()
        img_np = np.clip(img_np, 0, 1)
        ax.imshow(img_np)
        ax.set_xticks([])
        ax.set_yticks([])
        if times is not None:
            time_val = times[step_indices[i]].item()
            ax.set_title(f"t={time_val:.3f}", fontsize=10)
        else:
            ax.set_title(f"Paso {step_indices[i]}", fontsize=10)

    plt.tight_layout()
    if return_fig:
        return fig
    plt.show()
    plt.close()
    return None


# --------------------------------------------------------------------- #
# Resultados de imputación                                              #
# --------------------------------------------------------------------- #
def show_imputation_results(
    original_images: torch.Tensor,
    masks: torch.Tensor,
    imputed_images: torch.Tensor,
    n_samples: int = 8,
    title: str = "Resultados de imputación",
    original_labels: Optional[Union[torch.Tensor, List[int]]] = None,
    imputed_labels: Optional[Union[torch.Tensor, List[int]]] = None,
    nrow: int = 8,
    figsize: Tuple[int, int] = (12, 6),
    denormalize: bool = False,
    return_fig: bool = False,
) -> Optional[plt.Figure]:
    """
    Muestra original, enmascarada e imputada con etiquetas opcionales.
    """
    n_samples = min(n_samples, original_images.size(0))
    images = original_images[:n_samples]
    masks = masks[:n_samples]
    imputed_images = imputed_images[:n_samples]

    if original_labels is not None:
        original_labels = original_labels[:n_samples]
    if imputed_labels is not None:
        imputed_labels = imputed_labels[:n_samples]

    if denormalize:
        images = (images + 1) / 2.0
        imputed_images = (imputed_images + 1) / 2.0

    ncols = min(nrow, n_samples)
    nrows = ((n_samples + ncols - 1) // ncols) * 3

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize)
    fig.suptitle(title, fontsize=16)

    if nrows == 1 and ncols == 1:
        axes = np.array([[axes]])
    elif nrows == 1:
        axes = np.array([axes])
    elif ncols == 1:
        axes = np.array([[ax] for ax in axes])

    for i in range(n_samples):
        col = i % ncols
        row_base = (i // ncols) * 3

        # original
        ax_orig = axes[row_base, col]
        img_orig = images[i].permute(1, 2, 0).cpu().detach().numpy()
        if img_orig.shape[2] == 1:
            img_orig = img_orig.squeeze(2)
            ax_orig.imshow(img_orig, cmap="gray")
        else:
            ax_orig.imshow(np.clip(img_orig, 0, 1))
        label = ""
        if original_labels is not None:
            original_l = original_labels[i]
            label = original_l.item() if hasattr(original_l, "item") else original_l
            ax_orig.set_title(f"Original (Label: {label})", fontsize=10)
        else:
            ax_orig.set_title("Original", fontsize=10)
        ax_orig.axis("off")

        # enmascarada
        ax_mask = axes[row_base + 1, col]
        mask_exp = masks[i].expand_as(images[i]) if masks[i].size(0) == 1 else masks[i]
        masked = (images[i] * mask_exp).permute(1, 2, 0).cpu().detach().numpy()
        if masked.shape[2] == 1:
            masked = masked.squeeze(2)
            ax_mask.imshow(masked, cmap="gray")
        else:
            ax_mask.imshow(np.clip(masked, 0, 1))
        ax_mask.set_title("Enmascarada", fontsize=10)
        ax_mask.axis("off")

        # imputada
        ax_imp = axes[row_base + 2, col]
        img_imp = imputed_images[i].permute(1, 2, 0).cpu().detach().numpy()
        if img_imp.shape[2] == 1:
            img_imp = img_imp.squeeze(2)
            ax_imp.imshow(img_imp, cmap="gray")
        else:
            ax_imp.imshow(np.clip(img_imp, 0, 1))
        label = ""
        if imputed_labels is not None:
            original_l = imputed_labels[i]
            label = original_l.item() if hasattr(original_l, "item") else original_l
            ax_imp.set_title(f"Imputada (Label: {label})", fontsize=10)
        else:
            ax_imp.set_title("Imputada", fontsize=10)
        ax_imp.axis("off")

    for i in range(n_samples, nrows * ncols // 3):
        col = i % ncols
        row_base = (i // ncols) * 3
        for r in range(3):
            ax = axes[row_base + r, col]
            ax.axis("off")
            ax.set_visible(False)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    if return_fig:
        return fig
    plt.show()
    plt.close()
    return None


# --------------------------------------------------------------------- #
# Historial de entrenamiento                                            #
# --------------------------------------------------------------------- #
def plot_training_history(
    history: Dict[str, List[float]],
    figsize: Tuple[int, int] = (10, 6),
    title: str = "Historial de entrenamiento",
    smooth: bool = True,
    window_size: int = 10,
    return_fig: bool = False,
) -> Optional[plt.Figure]:
    """
    Visualiza el historial de entrenamiento (pérdida, métricas, etc.).
    """
    fig, ax = plt.subplots(figsize=figsize)

    def smooth_curve(values: List[float], window: int) -> np.ndarray:
        kernel = np.ones(window) / window
        return np.convolve(values, kernel, mode="valid")

    for key, values in history.items():
        if key == "epoch":
            continue
        x = history.get("epoch", np.arange(len(values)))
        if smooth and len(values) > window_size:
            y = smooth_curve(values, window_size)
            x = x[window_size - 1 : len(x)]
            ax.plot(x, y, label=f"{key} (suavizado)")
            ax.scatter(
                x, values[window_size - 1 :], alpha=0.3, label=f"{key} (original)"
            )
        else:
            ax.plot(x, values, label=key)

    ax.set_title(title, fontsize=14)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Valor")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()

    if return_fig:
        return fig
    plt.show()
    plt.close()
    return None
