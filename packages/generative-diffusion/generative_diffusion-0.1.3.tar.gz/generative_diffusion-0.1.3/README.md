# Generative‑Diffusion

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
[![Demo](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1oQLH2MrFySWSYcIiAEjTfdHL5xJ_Qm_y?usp=sharing)

Toolkit modular para **modelos de difusión generativos** (imágenes color)
con soporte para:

* **Procesos** VE‑SDE, VP‑SDE, SubVP‑SDE  
* **Samplers** Euler‑Maruyama, Predictor–Corrector, Probability‑Flow ODE,
  Exponential‑Integrator  
* **Noise schedules** lineal, coseno, constante  
* **Control** de generación (class‑conditional, imputación)  
* **Métricas** FID, IS, BPD

## Instalación rápida

```bash
pip install generative-diffusion
```

## Ejemplo mínimo
[![Demo](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1oQLH2MrFySWSYcIiAEjTfdHL5xJ_Qm_y?usp=sharing)

```python
from generative_diffusion.utils import *
from generative_diffusion.diffusion import ModelFactory
from generative_diffusion.score_networks import ScoreNet

# Crear modelo de difusión utilizando el ModelFactory
diffusion_model = ModelFactory.create(
    score_model_class=ScoreNet,
    is_conditional=True,
    sde_name='ve_sde',
    sampler_name='euler_maruyama',
    # scheduler_name='linear',
)

# Cargar un modelo pre-entrenado
diffusion_model.load_score_model("../checkpoints/Diffusion_model_VESDE_is_conditional_True.pt")

# Generar imágenes
generated_images, labels = diffusion_model.generate(
    n_samples=8,
    n_steps=500,
)
# Mostrar imágenes generadas
show_images(generated_images, title="Dígitos generados con difusión", labels=labels)
```

## Estructura de carpetas

```
generative_diffusion/   <-- código del paquete
demo_notebooks/         <-- ejemplos de uso
checkpoints/            <-- pesos entrenados opcionales
pyproject.toml
README.md
```

### 👥 Autores

- Manuel Muñoz Bermejo - [manuel.munnozb@estudiante.uam.es]
- Daniel Ortiz Buzarra - [daniel.ortizbuzarra@estudiante.uam.es]

Si utilizas este código en tus trabajos, por favor, **cita a los autores y enlaza este repositorio.**

## Desarrollo

* **Formateo**: `black .`
* **Linter**: `ruff check . --fix`

---

## Licencia

MIT