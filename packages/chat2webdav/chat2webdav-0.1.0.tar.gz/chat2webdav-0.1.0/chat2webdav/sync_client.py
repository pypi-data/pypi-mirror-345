"""Synchronous API clients for Chat2WebDAV."""

import json
import requests
from typing import List, Dict, Any, Optional

from .config import config_manager
from .llm.base import Message, get_proxy_settings


class SyncGeminiClient:
    """Synchronous Google Gemini API client."""
    
    def __init__(self):
        """Initialize the client."""
        self.api_key = ""
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.timeout = 60
    
    def is_configured(self) -> bool:
        """Check if the client is configured."""
        return (
            config_manager.config.gemini.enabled and
            config_manager.config.gemini.api_key
        )
    
    def _get_headers(self) -> Dict[str, str]:
        """Get the headers for the API request."""
        return {
            "Content-Type": "application/json"
        }
    
    def _prepare_messages(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """Prepare messages for the API request."""
        prepared_messages = []
        
        # Handle system message by prepending it to the first user message
        system_content = None
        for message in messages:
            if message.role == "system":
                system_content = message.content
            else:
                if message.role == "user":
                    if system_content and not prepared_messages:
                        # First user message gets the system prompt prepended
                        prepared_messages.append({
                            "role": "user",
                            "parts": [{"text": f"{system_content}\n\n{message.content}"}]
                        })
                        system_content = None
                    else:
                        prepared_messages.append({
                            "role": "user",
                            "parts": [{"text": message.content}]
                        })
                else:
                    prepared_messages.append({
                        "role": "model",
                        "parts": [{"text": message.content}]
                    })
        
        # If there's a system message but no user messages, add it as a user message
        if system_content:
            prepared_messages.append({
                "role": "user",
                "parts": [{"text": system_content}]
            })
        
        return prepared_messages
    
    def generate(self, messages: List[Message], model: str) -> str:
        """Generate a response from the API."""
        if not self.is_configured():
            return "Gemini API is not configured."
        
        self.api_key = config_manager.config.gemini.api_key
        
        prepared_messages = self._prepare_messages(messages)
        
        # Build the request payload
        payload = {
            "contents": prepared_messages,
            "generationConfig": {
                "temperature": 0.0,
                "topP": 0.95,
                "topK": 40,
            }
        }
        
        url = f"{self.api_url}/{model}:generateContent?key={self.api_key}"
        
        # Get proxy settings from utility function
        proxies = get_proxy_settings()
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout,
                proxies=proxies if proxies else None
            )
            
            response.raise_for_status()
            data = response.json()
            
            if "candidates" not in data or not data["candidates"]:
                return "No response generated."
            
            # Extract the text from the first candidate
            candidate = data["candidates"][0]
            if "content" not in candidate or "parts" not in candidate["content"]:
                return "Invalid response format."
            
            parts = candidate["content"]["parts"]
            if not parts:
                return "Empty response."
            
            return parts[0]["text"]
        
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            return error_msg
    
    def get_available_models(self) -> List[str]:
        """Get the list of available models."""
        models = self.fetch_available_models()

        return models
    
    def fetch_available_models(self) -> List[str]:
        """Fetch available models from the Google Gemini API."""
        if not self.is_configured():
            return []
        
        self.api_key = config_manager.config.gemini.api_key
        
        # Get proxy settings from utility function
        proxies = get_proxy_settings()
        
        try:
            response = requests.get(
                f"{self.api_url}?key={self.api_key}",
                headers=self._get_headers(),
                timeout=self.timeout,
                proxies=proxies if proxies else None
            )
            
            response.raise_for_status()
            data = response.json()
            
            if "models" not in data:
                return []
            
            # Extract model names
            return [model["name"].split("/")[-1] for model in data["models"]]
        
        except Exception as e:
            print(f"Error fetching models: {str(e)}")
            return []


class SyncOpenRouterClient:
    """Synchronous OpenRouter API client."""
    
    def __init__(self):
        """Initialize the client."""
        self.api_key = ""
        self.api_url = "https://openrouter.ai/api/v1"
        self.timeout = 60
    
    def is_configured(self) -> bool:
        """Check if the client is configured."""
        return (
            config_manager.config.openrouter.enabled and
            config_manager.config.openrouter.api_key
        )
    
    def _get_headers(self) -> Dict[str, str]:
        """Get the headers for the API request."""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://chat2webdav.app",  # Required by OpenRouter
            "X-Title": "Chat2WebDAV"  # Application name
        }
    
    def _prepare_messages(self, messages: List[Message]) -> List[Dict[str, str]]:
        """Prepare messages for the API request."""
        return [message.to_dict() for message in messages]
    
    def generate(self, messages: List[Message], model: str = "anthropic/claude-3-haiku") -> str:
        """Generate a response from the API."""
        if not self.is_configured():
            return "OpenRouter API is not configured."
        
        self.api_key = config_manager.config.openrouter.api_key
        
        prepared_messages = self._prepare_messages(messages)
        
        # Build the request payload
        payload = {
            "model": model,
            "messages": prepared_messages,
            "temperature": 0.0
        }
        
        # Get proxy settings from utility function
        proxies = get_proxy_settings()
        
        try:
            response = requests.post(
                f"{self.api_url}/chat/completions",
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout,
                proxies=proxies if proxies else None
            )
            
            response.raise_for_status()
            data = response.json()
            
            if "choices" not in data or not data["choices"]:
                return "No response generated."
            
            return data["choices"][0]["message"]["content"]
        
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            return error_msg
    
    def fetch_available_models(self) -> List[Dict[str, Any]]:
        """Fetch available models from the OpenRouter API."""
        if not self.is_configured():
            return []
        
        self.api_key = config_manager.config.openrouter.api_key
        
        # Get proxy settings from utility function
        proxies = get_proxy_settings()
        
        try:
            response = requests.get(
                f"{self.api_url}/models",
                headers=self._get_headers(),
                timeout=self.timeout,
                proxies=proxies if proxies else None
            )
            
            response.raise_for_status()
            data = response.json()
            
            if "data" not in data:
                return []
            
            # Extract relevant model information
            models = []
            for model in data["data"]:
                if "id" in model:
                    model_info = {
                        "id": model["id"],
                        "name": model.get("name", model["id"]),
                        "description": model.get("description", ""),
                        "context_length": model.get("context_length", 0),
                        "pricing": model.get("pricing", {})
                    }
                    models.append(model_info)
            
            return models
        
        except Exception as e:
            print(f"Error fetching models: {str(e)}")
            return []
    
    def get_available_models(self) -> List[str]:
        """Get the list of available models."""
        models = self.fetch_available_models()
 
        # Return model IDs
        return [model["id"] for model in models]


# Create singleton instances
gemini_client = SyncGeminiClient()
openrouter_client = SyncOpenRouterClient()
