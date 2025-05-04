"""Chat interface for Chat2WebDAV."""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from InquirerPy import prompt as inquirer_prompt
from InquirerPy.base.control import Choice

from .config import config_manager, SystemPromptConfig
from .webdav import webdav_handler
from .llm.base import Message
from .sync_client import gemini_client, openrouter_client


class ChatSession:
    """Chat session manager."""
    
    def __init__(self):
        """Initialize the chat session."""
        self.console = Console()
        self.messages: List[Message] = []
        self.model: str = ""
        self.provider: str = ""
        self.topic: str = ""
        self.conversation_content: str = ""
    
    def _format_message_for_display(self, role: str, content: str) -> Panel:
        """Format a message for display."""
        if role == "user":
            return Panel(
                Markdown(content),
                title="You",
                title_align="left",
                border_style="blue"
            )
        elif role == "assistant":
            return Panel(
                Markdown(content),
                title="Assistant",
                title_align="left",
                border_style="green"
            )
        else:
            return Panel(
                Markdown(content),
                title=role.capitalize(),
                title_align="left",
                border_style="yellow"
            )
    
    def _format_message_for_markdown(self, role: str, content: str) -> str:
        """Format a message for markdown export."""
        if role == "user":
            return f"## You\n\n{content}\n\n"
        elif role == "assistant":
            return f"## Assistant\n\n{content}\n\n"
        else:
            return f"## {role.capitalize()}\n\n{content}\n\n"
    
    def add_message(self, role: str, content: str):
        """Add a message to the conversation."""
        self.messages.append(Message(role=role, content=content))
        self.conversation_content += self._format_message_for_markdown(role, content)
    
    def display_message(self, role: str, content: str):
        """Display a message in the console."""
        panel = self._format_message_for_display(role, content)
        self.console.print(panel)
    
    def clear_messages(self):
        """Clear all messages."""
        self.messages = []
        self.conversation_content = ""
    
    def handle_command(self, command: str) -> bool:
        """Handle a command."""
        if command.startswith("/config") or command.startswith("/setting"):
            from .cli import config_command
            config_command()
            return True
        elif command.startswith("/clear"):
            self.clear_messages()
            self.console.print("[bold green]Conversation cleared.[/bold green]")
            return True
        elif command.startswith("/save"):
            if not self.topic:
                questions = [
                    {
                        "type": "input",
                        "name": "topic",
                        "message": "Enter a topic for this conversation:"
                    }
                ]
                answers = inquirer_prompt(questions)
                self.topic = answers["topic"]
            
            success = webdav_handler.save_conversation(self.topic, self.conversation_content)
            if success:
                self.console.print("[bold green]Conversation saved to WebDAV.[/bold green]")
            else:
                self.console.print("[bold red]Failed to save conversation.[/bold red]")
            return True
        elif command.startswith("/help"):
            self.display_help()
            return True
        elif command.startswith("/prompt"):
            self.select_system_prompt()
            return True
        elif command.startswith("/exit") or command.startswith("/quit"):
            return False
        
        return False
    
    def display_help(self):
        """Display help information."""
        help_text = """
# Available Commands

- `/help` - Show this help message
- `/config` - Configure Chat2WebDAV
- `/clear` - Clear the current conversation
- `/save` - Save the conversation to WebDAV
- `/model` - Select a different model
- `/prompt` - Select a different system prompt
- `/exit` or `/quit` - Exit the chat
"""
        self.console.print(Markdown(help_text))
    
    def select_model(self) -> str:
        """Select a model."""
        models = config_manager.get_models()
        
        if not models:
            self.console.print("[bold yellow]No models configured. Use `/config` to add models.[/bold yellow]")
            return ""
        
        choices = []
        for model in models:
            choices.append(Choice(value=(model.provider, model.name), name=f"{model.name} ({model.provider})"))
        
        questions = [
            {
                "type": "list",
                "name": "model",
                "message": "Select a model:",
                "choices": choices
            }
        ]
        
        answers = inquirer_prompt(questions)
        if not answers:
            return ""
            
        selected_model = answers["model"]
        self.provider = selected_model[0]
        self.model = selected_model[1]
        return selected_model[1]
    
    def select_system_prompt(self) -> Optional[SystemPromptConfig]:
        """Select a system prompt."""
        system_prompts = config_manager.get_system_prompts()
        
        if not system_prompts:
            self.console.print("[bold yellow]No system prompts configured. Use `/config` to add system prompts.[/bold yellow]")
            return None
        
        active_prompt = config_manager.get_active_system_prompt()
        active_name = active_prompt.name if active_prompt else None
        
        choices = []
        for prompt in system_prompts:
            name = prompt.name
            if name == active_name:
                name = f"{name} (active)"
            choices.append(Choice(value=prompt.name, name=name))
        
        questions = [
            {
                "type": "list",
                "name": "prompt_name",
                "message": "Select a system prompt:",
                "choices": choices
            }
        ]
        
        answers = inquirer_prompt(questions)
        if not answers:
            return None
            
        selected_prompt_name = answers["prompt_name"]
        success = config_manager.set_active_system_prompt(selected_prompt_name)
        
        if success:
            # Clear current messages and restart with new system prompt
            self.clear_messages()
            selected_prompt = config_manager.get_active_system_prompt()
            if selected_prompt:
                self.add_message("system", selected_prompt.content)
                self.console.print(f"[bold green]System prompt changed to '{selected_prompt.name}'.[/bold green]")
                return selected_prompt
        else:
            self.console.print("[bold red]Failed to set system prompt.[/bold red]")
        
        return None
    
    def get_llm_response(self, messages: List[Message]) -> str:
        """Get a response from the selected LLM."""
        if not self.model or not self.provider:
            self.console.print("[bold red]No model selected. Use `/model` to select a model.[/bold red]")
            return ""
            
        self.console.print("[bold yellow]Generating response...[/bold yellow]")
        
        try:
            if self.provider == "gemini":
                # Ensure we're using the correct model format for Gemini
                # Gemini models should be fully qualified with the API format
                gemini_model = self.model
                
                response = gemini_client.generate(messages, gemini_model)
                
                # If Gemini fails, try OpenRouter as a fallback only if the error is not related to the model format
                if response.startswith("Error:"):
                    self.console.print("[bold yellow]Gemini API failed. [/bold yellow]")
                    print(response)
                    exit(1)
            elif self.provider == "openrouter":
                response = openrouter_client.generate(messages, self.model)
            else:
                self.console.print("Unknown provider.")
                exit(1)
            
            return response
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            self.console.print(f"[bold red]{error_msg}[/bold red]")
            return error_msg


def start_chat():
    """Start a chat session."""
    chat_session = ChatSession()
    
    # Display welcome message
    chat_session.console.print(Markdown("# Welcome to Chat2WebDAV"))
    chat_session.console.print("Type `/help` for available commands.")
    
    # Check if WebDAV is configured
    if not webdav_handler.is_configured():
        chat_session.console.print("[bold yellow]WebDAV is not configured. Use `/config` to set it up.[/bold yellow]")
    
    # Select a model
    chat_session.model = chat_session.select_model()
    if not chat_session.model:
        chat_session.console.print("[bold red]No model selected. Exiting.[/bold red]")
        return
    
    # Get chat topic
    questions = [
        {
            "type": "input",
            "name": "topic",
            "message": "Enter a topic for this conversation:"
        }
    ]
    
    answers = inquirer_prompt(questions)
    chat_session.topic = answers["topic"]
    
    # Add header to conversation content
    date_str = datetime.now().strftime("%Y.%m.%d")
    chat_session.conversation_content = f"# Chat: {chat_session.topic}\n\n"
    chat_session.conversation_content += f"Date: {date_str}\n\n"
    chat_session.conversation_content += f"Model: {chat_session.model}\n\n"
    
    # Select system prompt
    system_prompts = config_manager.get_system_prompts()
    active_prompt = config_manager.get_active_system_prompt()
    
    if system_prompts:
        # Create choices for system prompt selection
        prompt_choices = []
        active_index = 0
        
        for i, sp in enumerate(system_prompts):
            display_name = f"{sp.name}{' (active)' if active_prompt and sp.name == active_prompt.name else ''}"
            prompt_choices.append(Choice(value=sp.name, name=display_name))
            if active_prompt and sp.name == active_prompt.name:
                active_index = i
        
        # Ask user to select a system prompt
        questions = [
            {
                "type": "list",
                "name": "system_prompt",
                "message": "Select a system prompt:",
                "choices": prompt_choices,
                "default": active_index
            }
        ]
        
        answers = inquirer_prompt(questions)
        selected_prompt_name = answers["system_prompt"]
        
        # Find the selected prompt
        selected_prompt = None
        for prompt in system_prompts:
            if prompt.name == selected_prompt_name:
                selected_prompt = prompt
                break
        
        # Add system message if a prompt was selected
        if selected_prompt:
            chat_session.add_message("system", selected_prompt.content)
            chat_session.conversation_content += f"System Prompt: {selected_prompt.name}\n\n"
            
            # Update active prompt if different from current
            if not active_prompt or selected_prompt.name != active_prompt.name:
                config_manager.set_active_system_prompt(selected_prompt.name)
    
    # Main chat loop
    running = True
    while running:
        # Get user input
        user_input = Prompt.ask("\n[bold blue]You[/bold blue]")
        
        # Check if it's a command
        if user_input.startswith("/"):
            running = chat_session.handle_command(user_input)
            continue
        
        # Add user message
        chat_session.add_message("user", user_input)
        chat_session.display_message("user", user_input)
        
        # Get assistant response
        response = chat_session.get_llm_response(chat_session.messages)
        
        # Add assistant message
        chat_session.add_message("assistant", response)
        chat_session.display_message("assistant", response)
        
        # Auto-save to WebDAV if configured
        if webdav_handler.is_configured():
            webdav_handler.save_conversation(chat_session.topic, chat_session.conversation_content)
        else:
            print("webdav not configured.")

# Singleton instance
chat_session = ChatSession()