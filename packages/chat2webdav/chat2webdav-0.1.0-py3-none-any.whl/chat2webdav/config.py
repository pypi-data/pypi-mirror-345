"""Configuration management for Chat2WebDAV."""

import os
import toml
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from pathlib import Path


class WebDAVConfig(BaseModel):
    """WebDAV configuration."""
    
    url: str = ""
    username: str = ""
    password: str = ""
    folder: str = "Chat"


class GeminiConfig(BaseModel):
    """Google Gemini API configuration."""
    
    api_key: str = ""
    enabled: bool = False


class OpenRouterConfig(BaseModel):
    """OpenRouter API configuration."""
    
    api_key: str = ""
    enabled: bool = False


class ModelConfig(BaseModel):
    """Model configuration."""
    
    name: str
    provider: str


class SystemPromptConfig(BaseModel):
    """System prompt configuration."""
    
    name: str
    content: str


class AppConfig(BaseModel):
    """Application configuration."""
    
    webdav: WebDAVConfig = Field(default_factory=WebDAVConfig)
    gemini: GeminiConfig = Field(default_factory=GeminiConfig)
    openrouter: OpenRouterConfig = Field(default_factory=OpenRouterConfig)
    models: List[ModelConfig] = Field(default_factory=list)
    system_prompts: List[SystemPromptConfig] = Field(default_factory=list)
    active_system_prompt: Optional[str] = None  # Name of the currently active system prompt
    http_proxy: Optional[str] = None
    https_proxy: Optional[str] = None


class ConfigManager:
    """Configuration manager."""
    
    def __init__(self):
        """Initialize the configuration manager."""
        self.config_file = self._find_config_file()
        self.config = self._load_config()
        self._setup_proxies()
    
    def _find_config_file(self) -> str:
        """Find the configuration file."""
        # Check in the current directory
        if os.path.exists("chat2webdav.conf"):
            return os.path.abspath("chat2webdav.conf")
        
        # Check in the package directory
        package_dir = os.path.dirname(os.path.abspath(__file__))
        package_config = os.path.join(package_dir, "chat2webdav.conf")
        if os.path.exists(package_config):
            return package_config
        
        # Check in the user's home directory
        home_config = os.path.join(os.path.expanduser("~"), ".chat2webdav.conf")
        if os.path.exists(home_config):
            return home_config
        
        # Default to creating in the current directory
        return os.path.abspath("chat2webdav.conf")
    
    def _encrypt(self, text: str) -> str:
        """Encrypt text."""
        # No longer encrypting, just return the plain text
        return text
    
    def _decrypt(self, text: str) -> str:
        """Decrypt text."""
        # No longer decrypting, just return the plain text
        return text
    
    def _load_config(self) -> AppConfig:
        """Load configuration from file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    data = toml.loads(f.read())
                
                # Convert TOML data to AppConfig
                config = AppConfig(
                    webdav=WebDAVConfig(
                        url=data.get("webdav", {}).get("url", ""),
                        username=data.get("webdav", {}).get("username", ""),
                        password=data.get("webdav", {}).get("password", ""),
                        folder=data.get("webdav", {}).get("folder", "Chat")
                    ),
                    gemini=GeminiConfig(
                        api_key=data.get("gemini", {}).get("api_key", ""),
                        enabled=data.get("gemini", {}).get("enabled", False)
                    ),
                    openrouter=OpenRouterConfig(
                        api_key=data.get("openrouter", {}).get("api_key", ""),
                        enabled=data.get("openrouter", {}).get("enabled", False)
                    ),
                    active_system_prompt=data.get("active_system_prompt"),
                    http_proxy=data.get("http_proxy"),
                    https_proxy=data.get("https_proxy"),
                )
                
                # Load models
                loaded_models = data.get("models", [])
                for model_data in loaded_models:
                    config.models.append(ModelConfig(
                        name=model_data.get("name", ""),
                        provider=model_data.get("provider", "")
                    ))
                
                # Remove empty models if any loaded incorrectly
                config.models = [m for m in config.models if m.name and m.provider]
                
                # Load system prompts
                loaded_system_prompts = data.get("system_prompts", [])
                for prompt_data in loaded_system_prompts:
                    config.system_prompts.append(SystemPromptConfig(
                        name=prompt_data.get("name", ""),
                        content=prompt_data.get("content", "")
                    ))
                
                # For backward compatibility: if there's a system_prompt field but no system_prompts
                if data.get("system_prompt") and not config.system_prompts:
                    legacy_prompt = data.get("system_prompt")
                    if legacy_prompt:
                        config.system_prompts.append(SystemPromptConfig(
                            name="Default",
                            content=legacy_prompt
                        ))
                        config.active_system_prompt = "Default"

            except Exception as e:
                print(f"Error loading config: {e}. Using default config.")
                config = AppConfig()
                # Add default system prompt
                config.system_prompts.append(SystemPromptConfig(
                    name="Default",
                    content="You are a helpful assistant."
                ))
                config.active_system_prompt = "Default"
        else:
            config = AppConfig()
            # Add default system prompt
            config.system_prompts.append(SystemPromptConfig(
                name="Default",
                content="You are a helpful assistant."
            ))
            config.active_system_prompt = "Default"
            # Save default config if file doesn't exist
            # self.config = config # Temporarily set to save
            # self.save_config()
        return config

    def save_config(self):
        """Save configuration to file."""
        # Convert AppConfig to dictionary for TOML
        data: Dict[str, Any] = {
            "webdav": {
                "url": self.config.webdav.url,
                "username": self.config.webdav.username,
                "password": self.config.webdav.password,  # Store password in plain text
                "folder": self.config.webdav.folder
            },
            "gemini": {
                "api_key": self.config.gemini.api_key,  # Store API key in plain text
                "enabled": self.config.gemini.enabled
            },
            "openrouter": {
                "api_key": self.config.openrouter.api_key,  # Store API key in plain text
                "enabled": self.config.openrouter.enabled
            },
        }
        
        # Add active system prompt if set
        if self.config.active_system_prompt:
            data["active_system_prompt"] = self.config.active_system_prompt
        
        # Add proxy settings if configured
        if self.config.http_proxy:
            data["http_proxy"] = self.config.http_proxy
        
        if self.config.https_proxy:
            data["https_proxy"] = self.config.https_proxy
        
        # Add models
        models_to_save = []
        for model in self.config.models:
            models_to_save.append({
                "name": model.name,
                "provider": model.provider
            })
        
        # Only add models section if there are models
        if models_to_save:
            data["models"] = models_to_save
        
        # Add system prompts
        system_prompts_to_save = []
        for prompt in self.config.system_prompts:
            system_prompts_to_save.append({
                "name": prompt.name,
                "content": prompt.content
            })
        
        # Only add system_prompts section if there are system prompts
        if system_prompts_to_save:
            data["system_prompts"] = system_prompts_to_save
        
        # Save to file
        with open(self.config_file, "w") as f:
            toml.dump(data, f)
        
        # Update proxies
        self._setup_proxies()

    def _setup_proxies(self):
        """Set up proxies."""
        if self.config.http_proxy:
            os.environ["HTTP_PROXY"] = self.config.http_proxy
        
        if self.config.https_proxy:
            os.environ["HTTPS_PROXY"] = self.config.https_proxy
    
    def add_model(self, name: str, provider: str):
        """Add a model to the configuration."""
        # Ensure correct assignment of provider and model name
        # provider should be "gemini" or "openrouter"
        # name should be the model name like "gemini-2.5-pro-preview-03-25"
        
        # Check if model exists in models list
        for model in self.config.models:
            if model.name == name and model.provider == provider:
                return
        
        # Add new model
        self.config.models.append(
            ModelConfig(
                name=name,  # Model name (e.g., "gemini-2.5-pro-preview-03-25")
                provider=provider  # Provider (e.g., "gemini" or "openrouter")
            )
        )
        self.save_config()
    
    def remove_model(self, name: str):
        """Remove a model from the configuration."""
        initial_length = len(self.config.models)
        self.config.models = [m for m in self.config.models if m.name != name]
        if len(self.config.models) < initial_length:
            self.save_config() # Save only if a model was actually removed
        else:
            print(f"Model '{name}' not found in configuration.") # Optional: notify if not found

    def get_models(self) -> List[ModelConfig]:
        """Get all configured models."""
        return self.config.models
    
    def add_system_prompt(self, name: str, content: str):
        """Add a system prompt to the configuration."""
        # Check if system prompt with this name already exists
        for i, prompt in enumerate(self.config.system_prompts):
            if prompt.name == name:
                # Update existing prompt
                self.config.system_prompts[i].content = content
                self.save_config()
                return
        
        # Add new system prompt
        self.config.system_prompts.append(
            SystemPromptConfig(
                name=name,
                content=content
            )
        )
        
        # If this is the first system prompt, make it active
        if len(self.config.system_prompts) == 1:
            self.config.active_system_prompt = name
            
        self.save_config()
    
    def remove_system_prompt(self, name: str):
        """Remove a system prompt from the configuration."""
        initial_length = len(self.config.system_prompts)
        self.config.system_prompts = [p for p in self.config.system_prompts if p.name != name]
        
        # If we removed the active system prompt, set a new one if available
        if self.config.active_system_prompt == name and self.config.system_prompts:
            self.config.active_system_prompt = self.config.system_prompts[0].name
        elif not self.config.system_prompts:
            self.config.active_system_prompt = None
            
        if len(self.config.system_prompts) < initial_length:
            self.save_config()
        else:
            print(f"System prompt '{name}' not found in configuration.")
    
    def get_system_prompts(self) -> List[SystemPromptConfig]:
        """Get all configured system prompts."""
        return self.config.system_prompts
    
    def set_active_system_prompt(self, name: str) -> bool:
        """Set the active system prompt by name."""
        for prompt in self.config.system_prompts:
            if prompt.name == name:
                self.config.active_system_prompt = name
                self.save_config()
                return True
        return False
    
    def get_active_system_prompt(self) -> Optional[SystemPromptConfig]:
        """Get the currently active system prompt."""
        if not self.config.active_system_prompt:
            return None
            
        for prompt in self.config.system_prompts:
            if prompt.name == self.config.active_system_prompt:
                return prompt
                
        return None


# Create a singleton instance
config_manager = ConfigManager()