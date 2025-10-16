"""
Model implementations for acceptance-bench.
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any

# Import specific model implementations
from .brightside import Brightside
from .openrouter_model import OpenRouterModel

# Provider defaults - DRY principle!
PROVIDER_DEFAULTS = {
    "openrouter": {
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "api_key_env": "OPENROUTER_API_KEY",
        "site_url": "https://github.com/ellydee",
        "site_name": "acceptance-bench",
    },
    "byo": {
        # BYO models define their own endpoints
    },
}


def load_model(model_name: str, config_path: Optional[str] = None, **kwargs):
    """
    Load a model by name with smart provider-based instantiation.
    
    This function:
    1. Loads config from models.yaml
    2. Applies provider defaults (DRY!)
    3. Overrides with kwargs
    4. Instantiates the appropriate model class
    
    For OpenRouter models, you only need to specify:
    - provider: openrouter
    - model_id: "x-ai/grok-4"
    
    Everything else uses defaults!
    
    Args:
        model_name: Name of the model to load
        config_path: Optional path to models.yaml config file
        **kwargs: Additional configuration to override
        
    Returns:
        Instantiated model object
        
    Raises:
        ValueError: If model configuration is invalid
    """
    # Load configuration from YAML
    config = {}
    if config_path is None:
        # Try default location
        default_config = Path(__file__).parent.parent.parent / "config" / "models.yaml"
        if default_config.exists():
            config_path = str(default_config)
    
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as f:
            yaml_config = yaml.safe_load(f)
            if yaml_config and "models" in yaml_config:
                # Normalize model name for lookup
                normalized_name = model_name.lower().replace("_", "-")
                model_config = yaml_config["models"].get(normalized_name, {})
                
                if not model_config:
                    available = ", ".join(yaml_config["models"].keys())
                    raise ValueError(
                        f"Model '{model_name}' not found in models.yaml. "
                        f"Available: {available}"
                    )
                
                config.update(model_config)
    
    # Override with kwargs
    config.update(kwargs)
    
    # Determine provider
    provider = config.get("provider")
    if not provider:
        raise ValueError(
            f"Model '{model_name}' must specify 'provider' in configuration"
        )
    
    # Apply provider defaults (before user config, so user can override)
    if provider in PROVIDER_DEFAULTS:
        defaults = PROVIDER_DEFAULTS[provider].copy()
        # Merge: defaults < config < kwargs
        for key, value in defaults.items():
            if key not in config:
                config[key] = value
    
    # Instantiate appropriate model class based on provider
    if provider == "openrouter":
        # All OpenRouter models use the same generic class
        if "model_id" not in config:
            raise ValueError(
                f"OpenRouter model '{model_name}' must specify 'model_id'"
            )
        return OpenRouterModel(name=model_name, **config)
    
    elif provider == "byo":
        # BYO models use Brightside pattern (could generalize this too)
        return Brightside(name=model_name, **config)
    
    else:
        raise ValueError(
            f"Unknown provider '{provider}'. Supported: openrouter, byo"
        )


def register_provider_defaults(provider: str, defaults: Dict[str, Any]):
    """
    Register default configuration for a provider.
    
    This allows extending the framework with custom providers.
    
    Args:
        provider: Provider name (e.g., "my-custom-provider")
        defaults: Default configuration dict
        
    Example:
        register_provider_defaults("anthropic", {
            "endpoint": "https://api.anthropic.com/v1/messages",
            "api_key_env": "ANTHROPIC_API_KEY",
        })
    """
    PROVIDER_DEFAULTS[provider] = defaults


__all__ = [
    "Brightside",
    "OpenRouterModel",
    "load_model",
    "register_provider_defaults",
    "PROVIDER_DEFAULTS",
]

