"""Base types and utilities for Chat2WebDAV LLM clients."""

from typing import Dict, Optional


class Message:
    """Chat message."""
    
    def __init__(self, role: str, content: str):
        """Initialize a message."""
        self.role = role
        self.content = content
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary."""
        return {"role": self.role, "content": self.content}


def get_proxy_settings() -> Dict[str, Optional[str]]:
    """Get proxy settings from config manager.
    
    Returns:
        Dictionary with http and https proxy settings.
    """
    from ..config import config_manager
    
    proxies = {}
    if config_manager.config.http_proxy:
        proxies["http"] = config_manager.config.http_proxy
    if config_manager.config.https_proxy:
        proxies["https"] = config_manager.config.https_proxy
    
    return proxies
