# scale_to_500m.py
from pathlib import Path
from capibara_model.core.scaling import ModelScaler
from capibara_model.core.model import DynamicCapibaraModel
from capibara_model.train_unified import train_model, load_config #type: ignore

def scale_model():
    # Cargar configuración
    config = load_config("scale_to_500m_config.yaml")
    
    # Inicializar scaler
    scaler = ModelScaler(**config["scaling"])
    
    # Escalar modelo
    scaled_model = scaler.scale_model()
    
    # Fine-tuning usando el entrenador unificado
    train_model(
        config=config,
        output_dir=Path("checkpoints/500m"),
        use_tpu=True
    )

if __name__ == "__main__":
    scale_model()