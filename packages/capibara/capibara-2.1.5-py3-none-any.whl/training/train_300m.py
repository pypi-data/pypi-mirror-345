# train_300m.py
from pathlib import Path
from capibara_model.core.model import DynamicCapibaraModel
from capibara_model.train_unified import train_model, load_config

def main():
    # Cargar configuración
    config = load_config("config_300m.yaml")
    
    # Inicializar modelo
    model = DynamicCapibaraModel(**config["model"])
    
    # Entrenar usando el entrenador unificado
    train_model(
        config=config,
        output_dir=Path("checkpoints/300m"),
        use_tpu=True
    )

if __name__ == "__main__":
    main()