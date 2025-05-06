"""
Setup configuration for CapibaraModel.

This script defines the package configuration for the CapibaraModel, including
dependencies, metadata, and package data.
"""

from setuptools import setup, find_packages #type: ignore
from pathlib import Path
import sys
import subprocess
from tqdm import tqdm #type: ignore

class CustomInstallCommand:
    def run(self):
        # Configurar pip para ser silencioso
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "--no-warn-script-location", "."])

# Read the README file for the long description
readme = Path("README.md").read_text(encoding="utf-8")

setup(
    name="capibara",
    version="2.1.4",
    description="Modelo de lenguaje avanzado basado en SSM y experimentación de nuevas tecnologías.",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Anachroni s.coop",
    url="https://github.com/anachroni-io/capibara",
    packages=find_packages(),
    install_requires=[
        "jax>=0.4.23",
        "jaxlib>=0.4.23",
        "flax>=0.8.2",
        "tensorflow>=2.16.1",
        "tensorflow-text>=2.16.1",
        "tensorflow-hub>=0.16.1",
        "transformers>=4.40.1",
        "datasets>=2.18.1",
        "accelerate>=0.29.2",
        "torch>=2.2.2",
        "torchaudio>=0.17.2",
        "torchvision>=0.17.2",
        "wandb>=0.16.6",
        "bitsandbytes>=0.43.0",
        "pydantic>=2.7.0",
        "numpy>=1.26.4",
        "pandas>=2.2.3",
        "scipy>=1.15.2",
        "optax>=0.1.9",
        "chex>=0.1.9",
        "orbax-checkpoint>=0.5.3",
        "tensorboard>=2.19.0",
        "tensorboard-data-server>=0.7.2",
        "safetensors>=0.4.2",
        "tokenizers>=0.15.2",
        "huggingface-hub>=0.20.3",
        "protobuf>=4.25.3",
        "PyYAML>=6.0.1",
        "requests>=2.31.0",
        "tqdm>=4.66.2",
        "rich>=13.7.0",
        "python-dotenv>=1.0.1",
        "sentry-sdk>=2.8.0",
        "psutil>=5.9.8",
        "scikit-learn>=1.6.1",
        "onnxruntime>=1.17.0",
        "onnxruntime-gpu>=1.17.0",
        "tensorflow-probability>=0.20.0",
        "keras==3.9.0"
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.2,<9.0.0",
            "black>=24.2.0,<25.0.0",
            "isort>=5.13.2,<6.0.0",
            "mypy>=1.8.0,<2.0.0",
            "flake8>=7.0.0,<8.0.0",
        ],
        "tpu": [
            "libtpu>=1.0.0,<2.0.0",
            "cloud-tpu-client>=0.10,<1.0",
        ],
    },
    python_requires=">=3.9",
    license="Proprietary - All Rights Reserved",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="machine-learning nlp language-model ssm tpu jax",
    project_urls={
        "Documentation": "https://capibara-model.readthedocs.io",
        "Source": "https://github.com/anachroni-io/capibara-model",
        "Issues": "https://github.com/anachroni-io/capibara-model/issues",
    },
    cmdclass={
        'install': CustomInstallCommand,
    },
)