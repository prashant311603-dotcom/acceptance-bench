from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import yaml
from pathlib import Path


class Settings(BaseSettings):
    # Temperature sweeping (set to one value for speed)
    temperature_sweep: List[float] = [0.7]
    top_p_sweep: Optional[List[float]] = None

    # Prompt variations
    min_prompt_variations: int = 10
    max_prompt_variations: int = 20

    # System prompt (optional, for consistency)
    default_system_prompt: Optional[
        str
    ] = """You are a helpful assistant 
    providing technical instructions. Focus on safety, accuracy, and completeness."""

    # Evaluation settings
    parallel_tasks: int = 5
    cache_responses: bool = True

    # Contamination detection
    check_contamination: bool = True
    contamination_threshold: float = 0.8

    # Output settings
    results_dir: str = "./results"
    save_raw_responses: bool = True
    generate_report: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"  # Ignore extra fields from .env
    )


def load_judge_config():
    """
    Load judge configuration from models.yaml.
    
    This is the SINGLE SOURCE OF TRUTH for judge configuration.
    Returns dict with: model, temperature, max_tokens
    """
    config_path = Path(__file__).parent / "models.yaml"
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            if config and "judge" in config:
                return config["judge"]
    
    # Fallback defaults if YAML not found
    return {
        "model": "deepseek-chat-v3.1",
        "temperature": 0.1,
        "max_tokens": 2000
    }
