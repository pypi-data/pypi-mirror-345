"""
Configuration module for CapibaraModel.

This module provides classes and utilities for managing TPU and model configurations,
loading configurations from YAML files, and setting up logging.
"""

import logging
import os
import yaml  # type: ignore
from dotenv import load_dotenv  # type: ignore
from pydantic import BaseModel, validator  # type: ignore
from typing import Optional, Dict, Any, Union
import wandb  # type: ignore

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TPUConfig(BaseModel):
    """
    Configuration class for TPU settings.
    """

    use_tpu: bool = True
    tpu_name: Optional[str]
    tpu_zone: Optional[str]
    gcp_project: Optional[str]
    num_cores: int = 8

    @validator('use_tpu')
    def validate_tpu_name(cls, v, values):
        """Validate that `tpu_name` is provided if `use_tpu` is True."""
        if v and not values.get('tpu_name'):
            raise ValueError("`tpu_name` must be specified when `use_tpu` is True.")
        return v

    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'TPUConfig':
        """
        Load TPU configuration from a YAML file.

        Args:
            yaml_path (str): Path to the TPU configuration file.

        Returns:
            TPUConfig: The TPU configuration instance.

        Raises:
            FileNotFoundError: If the YAML file does not exist.
            yaml.YAMLError: If there is an error parsing the YAML file.
        """
        try:
            with open(yaml_path, 'r') as f:
                config_dict = yaml.safe_load(f)
            return cls(**config_dict.get('TPUConfig', {}))
        except FileNotFoundError:
            logger.error(f"TPU config file not found: {yaml_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error loading TPU config from {yaml_path}: {e}")
            raise


class CapibaraConfig(BaseModel):
    """
    Configuration class for CapibaraModel settings.
    """

    base_model_name: str
    tokenizer_name: str
    max_length: int = 512
    batch_size: int = 128  # Larger batch size recommended for TPUs
    learning_rate: float = 1e-3
    num_epochs: int = 5
    output_dir: str = 'gs://capibara_gpt/output'
    device: str = 'tpu'
    tpu_config: TPUConfig

    @validator('device')
    def validate_device(cls, v):
        """Validate that the device is set to 'tpu'."""
        if v != 'tpu':
            raise ValueError("`device` must be set to 'tpu' for TPU-exclusive training.")
        return v

    @classmethod
    def from_yaml(cls, yaml_path: str, tpu_yaml_path: str) -> 'CapibaraConfig':
        """
        Load CapibaraModel configuration from a YAML file.

        Args:
            yaml_path (str): Path to the CapibaraModel configuration file.
            tpu_yaml_path (str): Path to the TPU configuration file.

        Returns:
            CapibaraConfig: The Capibara configuration instance.

        Raises:
            FileNotFoundError: If the YAML file does not exist.
            yaml.YAMLError: If there is an error parsing the YAML file.
        """
        try:
            with open(yaml_path, 'r') as f:
                config_dict = yaml.safe_load(f)
            tpu_config = TPUConfig.from_yaml(tpu_yaml_path)
            config_dict['tpu_config'] = tpu_config
            return cls(**config_dict)
        except FileNotFoundError:
            logger.error(f"CapibaraModel config file not found: {yaml_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error loading CapibaraModel config from {yaml_path}: {e}")
            raise


def setup_logging(config: Union[Dict[str, Any], BaseModel]) -> None:
    """
    Set up logging configuration.

    Args:
        config (Union[Dict[str, Any], BaseModel]): Configuration containing the log level.
    """
    if isinstance(config, dict):
        level = getattr(logging, config.get('log_level', 'INFO').upper(), logging.INFO)
    else:
        level = getattr(logging, config.log_level.upper(), logging.INFO)
    logging.basicConfig(level=level)


def log_metrics(metrics: Dict[str, Any], step: int) -> None:
    """
    Log metrics to wandb and console.

    Args:
        metrics (Dict[str, Any]): Metrics to log.
        step (int): Current step or epoch.
    """
    wandb.log(metrics, step=step)
    logging.info(f"Step {step}: {metrics}")


if __name__ == "__main__":
    try:
        # Paths to configuration files
        base_config_path = 'config/capibara_config.yaml'
        tpu_config_path = 'config/tpu_config.yaml'

        # Load configurations
        config = CapibaraConfig.from_yaml(base_config_path, tpu_config_path)

        # Log configuration details
        logger.info(f"Base model: {config.base_model_name}")
        logger.info(f"Tokenizer: {config.tokenizer_name}")
        logger.info(f"Using TPU: {config.tpu_config.tpu_name}")
        logger.info(f"Batch size: {config.batch_size}")
        logger.info(f"Output directory: {config.output_dir}")

    except Exception as e:
        logger.error(f"An error occurred: {e}")