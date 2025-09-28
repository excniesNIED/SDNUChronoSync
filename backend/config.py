"""
Configuration management module for the application.
Loads and manages settings from config.toml file.
"""

import toml
import os
from typing import Dict, Any, Optional
from pathlib import Path

class Config:
    """Configuration manager class."""
    
    def __init__(self, config_path: str = "config.toml"):
        self.config_path = config_path
        self._config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from TOML file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = toml.load(f)
                print(f"Configuration loaded from {self.config_path}")
            except Exception as e:
                print(f"Error loading config: {e}")
                self._config = self._get_default_config()
        else:
            print(f"Config file {self.config_path} not found, using defaults")
            self._config = self._get_default_config()
            self.save_config()
    
    def save_config(self) -> None:
        """Save current configuration to TOML file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                toml.dump(self._config, f)
            print(f"Configuration saved to {self.config_path}")
        except Exception as e:
            print(f"Error saving config: {e}")
            raise
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'storage.provider')."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation."""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update configuration with new values."""
        self._config.update(new_config)
        self.save_config()
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration."""
        return self._config.copy()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "storage": {
                "provider": "local",
                "local": {
                    "upload_path": "uploads/avatars",
                    "base_url": "/static/avatars"
                },
                "alist": {
                    "url": "https://your-alist-instance.com",
                    "token": "alist-your-secret-token",
                    "upload_path": "/_imageStore",
                    "custom_url": ""
                }
            }
        }
    
    @property
    def storage_provider(self) -> str:
        """Get current storage provider."""
        return self.get('storage.provider', 'local')
    
    @property
    def local_config(self) -> Dict[str, Any]:
        """Get local storage configuration."""
        return self.get('storage.local', {})
    
    @property
    def alist_config(self) -> Dict[str, Any]:
        """Get Alist storage configuration."""
        return self.get('storage.alist', {})

# Global configuration instance
config = Config()

# Helper functions
def get_config() -> Config:
    """Get global configuration instance."""
    return config

def reload_config() -> None:
    """Reload configuration from file."""
    global config
    config.load_config()
