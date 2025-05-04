"""WebDAV client for Chat2WebDAV."""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from webdav4.client import Client as WebDAVClient
from .config import config_manager


class WebDAVHandler:
    """Handler for WebDAV operations."""
    
    def __init__(self):
        """Initialize the WebDAV handler."""
        self.client = None
        self._initialize_client()
    
    def _set_proxy_env(self):
        """Set proxy environment variables if configured."""
        if config_manager.config.http_proxy:
            os.environ["HTTP_PROXY"] = config_manager.config.http_proxy
        if config_manager.config.https_proxy:
            os.environ["HTTPS_PROXY"] = config_manager.config.https_proxy
    
    def _initialize_client(self) -> bool:
        """Initialize the WebDAV client."""
        webdav_config = config_manager.config.webdav
        
        if not webdav_config.url or not webdav_config.username or not webdav_config.password:
            return False
        
        try:
            # Set proxy environment variables
            self._set_proxy_env()
            
            self.client = WebDAVClient(
                webdav_config.url,
                auth=(webdav_config.username, webdav_config.password)
            )
            return True
        except Exception as e:
            print(f"Error initializing WebDAV client: {e}")
            self.client = None
            return False
    
    def is_configured(self) -> bool:
        """Check if WebDAV is configured."""
        return self.client is not None
    
    def ensure_folder_exists(self, folder: Optional[str] = None) -> bool:
        """Ensure the target folder exists on the WebDAV server."""
        if not self.is_configured():
            if not self._initialize_client():
                return False
        
        folder = folder or config_manager.config.webdav.folder
        
        try:
            if not self.client.exists(folder):
                self.client.mkdir(folder)
            return True
        except Exception as e:
            print(f"Error creating folder: {e}")
            return False
    
    def upload_file(self, content: str, filename: str, folder: Optional[str] = None) -> bool:
        """Upload a file to the WebDAV server."""
        if not self.is_configured():
            if not self._initialize_client():
                return False
        
        folder = folder or config_manager.config.webdav.folder
        
        # Ensure folder exists
        if not self.ensure_folder_exists(folder):
            return False
        
        # Create temporary file
        temp_file = Path(os.path.expanduser("~/.chat2webdav_temp.md"))
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(content)
            
            # Upload to WebDAV
            remote_path = f"{folder}/{filename}"
            
            # Check if file exists and delete it to force overwrite
            if self.client.exists(remote_path):
                self.client.remove(remote_path)
                
            with open(temp_file, "rb") as f:
                self.client.upload_fileobj(f, remote_path)
            
            return True
        except Exception as e:
            print(f"Error uploading file: {e}")
            return False
        finally:
            # Clean up temporary file
            if temp_file.exists():
                temp_file.unlink()
    
    def save_conversation(self, topic: str, conversation_content: str) -> bool:
        """Save a conversation to WebDAV."""
        # Format filename with date and topic
        date_str = datetime.now().strftime("%Y.%m.%d")
        filename = f"{date_str}_{topic}.md"
        print("WebDav file: " + filename)
        return self.upload_file(conversation_content, filename)


# Singleton instance
webdav_handler = WebDAVHandler()