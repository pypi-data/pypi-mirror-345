# -----------------------------------------------------------------------------
# Proyecto: Generative AI Diffusion System - AA3 2024/2025
# Archivo:  measures/measures.py
# Autores:
#   - Manuel Muñoz Bermejo (manuel.munnozb@estudiante.uam.es)
#   - Daniel Ortiz Buzarra (daniel.ortizbuzarra@estudiante.uam.es)
# Licencia: MIT
# -----------------------------------------------------------------------------

from __future__ import annotations

import math
from typing import Any, Optional, Tuple

import numpy as np
import torch
import torch.nn.functional as F
from scipy import linalg
from torch import Tensor
from torch.utils.data import DataLoader
from tqdm.auto import tqdm
from torchvision import models, transforms

# --------------------------------------------------------------------- #
# Utilidades                                                            #
# --------------------------------------------------------------------- #
_NORMALIZE = transforms.Normalize(
    mean=[0.485, 0.456, 0.406],
    std=[0.229, 0.224, 0.225],
)
_PREPROCESS = transforms.Compose(
    [
        transforms.Resize((299, 299), antialias=True),
        _NORMALIZE,
    ]
)


# --------------------------------------------------------------------- #
# Inception wrapper                                                     #
# --------------------------------------------------------------------- #
class InceptionModel(torch.nn.Module):
    """
    Capa de extracción de *features* (2048‑D) usando **Inception v3**.

    Parámetros
    ----------
    device : str, optional
        Dispositivo donde se alojará el modelo.
    """

    def __init__(self, *, device: str = "cuda") -> None:
        super().__init__()
        weights = models.Inception_V3_Weights.IMAGENET1K_V1
        net = models.inception_v3(weights=weights)
        net.fc = torch.nn.Identity()  # salidas de 2048 dims
        self.net = net.to(device).eval()
        self.device = device

    @torch.no_grad()
    def forward(self, x: Tensor) -> Tensor:
        """
        Convierte imágenes en *features*.

        Espera tensores **en rango [-1, 1]** con forma `[B, 3, H, W]`.
        """
        x = (x + 1.0) * 0.5  # → [0, 1]
        x = _PREPROCESS(x)
        return self.net(x.to(self.device))


# --------------------------------------------------------------------- #
# Extracción de características                                         #
# --------------------------------------------------------------------- #
@torch.no_grad()
def extract_features(
    images: Tensor,
    *,
    batch_size: int = 64,
    inception: Optional[InceptionModel] = None,
    device: str = "cuda",
) -> Tensor:
    """
    Extrae embeddings de Inception (2048‑D) para un conjunto de imágenes.
    """
    inception = inception or InceptionModel(device=device)
    feats: list[Tensor] = []

    for i in tqdm(range(0, len(images), batch_size), desc="Extract Inception features"):
        batch = images[i : i + batch_size].to(device, non_blocking=True)
        feats.append(inception(batch).cpu())

    return torch.cat(feats, dim=0)


# --------------------------------------------------------------------- #
# FID                                                                   #
# --------------------------------------------------------------------- #
def _mean_cov(x: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Media y covarianza (float64) para un array 2‑D."""
    x = x.astype(np.float64)
    return x.mean(axis=0), np.cov(x, rowvar=False)


def calculate_fid(
    real: Tensor,
    fake: Tensor,
    *,
    batch_size: int = 64,
    device: str = "cuda",
) -> float:
    """
    Fréchet Inception Distance entre dos conjuntos de imágenes.

    Retorna un escalar (menor ⇒ mejor).
    """
    inception = InceptionModel(device=device)
    φ_real = extract_features(
        real, batch_size=batch_size, inception=inception, device=device
    )
    φ_fake = extract_features(
        fake, batch_size=batch_size, inception=inception, device=device
    )

    μ_r, Σ_r = _mean_cov(φ_real.numpy())
    μ_f, Σ_f = _mean_cov(φ_fake.numpy())

    diff = μ_r - μ_f
    covmean, _ = linalg.sqrtm(Σ_r @ Σ_f, disp=False)

    if np.iscomplexobj(covmean):
        covmean = covmean.real

    fid = diff @ diff + np.trace(Σ_r + Σ_f - 2.0 * covmean)
    return float(fid)


# --------------------------------------------------------------------- #
# Inception Score                                                       #
# --------------------------------------------------------------------- #
@torch.no_grad()
def calculate_inception_score(
    images: Tensor,
    *,
    batch_size: int = 64,
    splits: int = 10,
    device: str = "cuda",
) -> float:
    """
    Inception Score para imágenes generadas (mayor ⇒ mejor).

    Implementación estable basada en logits de Inception v3.
    """
    weights = models.Inception_V3_Weights.IMAGENET1K_V1
    net = models.inception_v3(weights=weights).to(device).eval()

    preds: list[Tensor] = []
    for i in tqdm(range(0, len(images), batch_size), desc="Inception Score"):
        batch = images[i : i + batch_size].to(device)
        batch = (batch + 1.0) * 0.5  # → [0, 1]
        batch = _PREPROCESS(batch)
        preds.append(F.softmax(net(batch), dim=1).cpu())

    pyx = torch.cat(preds, dim=0).numpy()
    n = pyx.shape[0]
    splits = max(1, min(splits, n))
    split_size = n // splits

    scores = []
    for k in range(splits):
        part = pyx[k * split_size : (k + 1) * split_size]
        if part.size == 0:
            continue
        py = part.mean(axis=0)
        kl = part * (np.log(part + 1e-16) - np.log(py + 1e-16))
        scores.append(np.exp(kl.sum(axis=1).mean()))

    return float(np.mean(scores))


# --------------------------------------------------------------------- #
# Bits per Dimension                                                    #
# --------------------------------------------------------------------- #
@torch.no_grad()
def calculate_bpd(
    score_model: torch.nn.Module,
    sde: Any,
    dataloader: DataLoader,
    *,
    n_samples: int = 1_000,
    device: str = "cuda",
) -> float:
    """
    Aproximación de Bits per Dimension mediante denoising score matching.
    """
    score_model.eval()
    total_bpd, counted = 0.0, 0

    for x, *_ in tqdm(
        dataloader, total=math.ceil(n_samples / dataloader.batch_size), desc="BPD"
    ):
        if counted >= n_samples:
            break
        x = x.to(device)[: n_samples - counted]
        b = x.size(0)
        counted += b

        # sample t ∼ U(0,1)
        t = torch.rand(b, device=device)
        noise = torch.randn_like(x)
        mean, std = sde.marginal_prob(x, t)

        x_t = mean + std.view(-1, 1, 1, 1) * noise
        score = score_model(x_t, t)

        likelihood_term = (score * noise).flatten(1).sum(dim=1)
        prior_term = 0.5 * noise.flatten(1).pow(2).sum(dim=1)
        log_likelihood = likelihood_term - prior_term  # ≈ log p(x)

        dim = np.prod(x.shape[1:])
        bpd = (-log_likelihood / (dim * math.log(2))).mean().item()
        total_bpd += bpd * b

    return total_bpd / max(counted, 1)
