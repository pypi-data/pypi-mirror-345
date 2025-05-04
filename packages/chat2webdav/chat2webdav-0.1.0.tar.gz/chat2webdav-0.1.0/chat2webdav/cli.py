"""CLI interface for Chat2WebDAV."""

import typer
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from InquirerPy import prompt as inquirer_prompt
from InquirerPy.base.control import Choice

from .config import config_manager, SystemPromptConfig
from .webdav import webdav_handler
from .sync_client import openrouter_client, gemini_client

app = typer.Typer(
    name="chat2webdav",
    help="CLI tool for saving LLM chat conversations to WebDAV."
)
console = Console()


@app.command(name="chat")
def chat_command():
    """Start a chat session."""
    from .chat import start_chat
    start_chat()


@app.command(name="config")
def config_command(current_menu: str = "main"):
    """Configure Chat2WebDAV."""
    if current_menu == "main":
        # Main configuration menu
        choices = [
            {"name": "🌐 WebDAV Settings", "value": "webdav"},
            {"name": "🧠 Google Gemini API Settings", "value": "gemini"},
            {"name": "🔄 OpenRouter API Settings", "value": "openrouter"},
            {"name": "💬 System Prompts", "value": "system_prompts"},
            {"name": "🔌 HTTP Proxy Settings", "value": "proxy"},
            {"name": "🤖 Manage Models", "value": "models"},
            {"name": "🚪 Exit", "value": "exit"}
        ]
        
        questions = [
            {
                "type": "list",
                "name": "option",
                "message": "Select a setting to configure:",
                "choices": choices
            }
        ]
        
        answers = inquirer_prompt(questions)
        option = answers["option"]
        
        if option == "exit":
            return
        
        elif option == "webdav":
            # Configure WebDAV
            questions = [
                {
                    "type": "input",
                    "name": "url",
                    "message": "WebDAV URL:",
                    "default": config_manager.config.webdav.url
                },
                {
                    "type": "input",
                    "name": "username",
                    "message": "WebDAV Username:",
                    "default": config_manager.config.webdav.username
                },
                {
                    "type": "password",
                    "name": "password",
                    "message": "WebDAV Password:",
                    "default": config_manager.config.webdav.password
                },
                {
                    "type": "input",
                    "name": "folder",
                    "message": "WebDAV Folder:",
                    "default": config_manager.config.webdav.folder
                }
            ]
            
            answers = inquirer_prompt(questions)
            
            config_manager.config.webdav.url = answers["url"]
            config_manager.config.webdav.username = answers["username"]
            config_manager.config.webdav.password = answers["password"]
            config_manager.config.webdav.folder = answers["folder"]
            
            config_manager.save_config()
            webdav_handler._initialize_client()
            
            # Return to config menu
            config_command(current_menu="main")
        
        elif option == "gemini":
            # Configure Gemini
            questions = [
                {
                    "type": "password",
                    "name": "api_key",
                    "message": "Gemini API Key:",
                    "default": config_manager.config.gemini.api_key
                },
                {
                    "type": "confirm",
                    "name": "enabled",
                    "message": "Enable Gemini API?",
                    "default": config_manager.config.gemini.enabled
                }
            ]
            
            answers = inquirer_prompt(questions)
            
            config_manager.config.gemini.api_key = answers["api_key"]
            config_manager.config.gemini.enabled = answers["enabled"]
            
            config_manager.save_config()
            
            # Return to config menu
            config_command(current_menu="main")
        
        elif option == "openrouter":
            # Configure OpenRouter
            questions = [
                {
                    "type": "password",
                    "name": "api_key",
                    "message": "OpenRouter API Key:",
                    "default": config_manager.config.openrouter.api_key
                },
                {
                    "type": "confirm",
                    "name": "enabled",
                    "message": "Enable OpenRouter API?",
                    "default": config_manager.config.openrouter.enabled
                }
            ]
            
            answers = inquirer_prompt(questions)
            
            config_manager.config.openrouter.api_key = answers["api_key"]
            config_manager.config.openrouter.enabled = answers["enabled"]
            
            config_manager.save_config()
            
            # Return to config menu
            config_command(current_menu="main")
        
        elif option == "system_prompts":
            # System Prompts Management
            config_command(current_menu="system_prompts")
        
        elif option == "system_prompt":
            # For backward compatibility, redirect to the new system_prompts menu
            console.print("[bold yellow]Redirecting to the new System Prompts menu...[/bold yellow]")
            config_command(current_menu="system_prompts")
        
        elif option == "proxy":
            # Configure HTTP Proxy
            questions = [
                {
                    "type": "input",
                    "name": "http_proxy",
                    "message": "HTTP Proxy (leave empty to disable):",
                    "default": config_manager.config.http_proxy or ""
                },
                {
                    "type": "input",
                    "name": "https_proxy",
                    "message": "HTTPS Proxy (leave empty to disable):",
                    "default": config_manager.config.https_proxy or ""
                }
            ]
            
            answers = inquirer_prompt(questions)
            
            http_proxy = answers["http_proxy"].strip()
            https_proxy = answers["https_proxy"].strip()
            
            config_manager.config.http_proxy = http_proxy if http_proxy else None
            config_manager.config.https_proxy = https_proxy if https_proxy else None
            
            config_manager.save_config()
            
            # Return to config menu
            config_command(current_menu="main")
        
        elif option == "models":
            # Models management menu
            config_command(current_menu="models")
        
        elif option == "openrouter_models":
            # This option has been removed, but keeping the code structure for backward compatibility
            console.print("[bold yellow]This menu has been deprecated. Please use 'Manage Favorite Models' instead.[/bold yellow]")
            import time
            time.sleep(2)
            config_command(current_menu="main")
        
        else:
            console.print("[bold red]Invalid option. Please try again.[/bold red]")
            config_command(current_menu="main")
    
    elif current_menu == "system_prompts":
        # System Prompts Management
        active_prompt = config_manager.get_active_system_prompt()
        active_name = active_prompt.name if active_prompt else "None"
        
        # Show current active system prompt
        console.print(f"[bold]Current active system prompt:[/bold] {active_name}")
        
        # System Prompts menu
        choices = [
            {"name": "➕ Add New System Prompt", "value": "add"},
            {"name": "✏️ Edit System Prompt", "value": "edit"},
            {"name": "🔄 Set Active System Prompt", "value": "set_active"},
            {"name": "❌ Remove System Prompt", "value": "remove"},
            {"name": "📋 List All System Prompts", "value": "list"},
            {"name": "⬅️ Back", "value": "back"},
            {"name": "🚪 Exit", "value": "exit"}
        ]
        
        questions = [
            {
                "type": "list",
                "name": "action",
                "message": "Select an action:",
                "choices": choices
            }
        ]
        
        answers = inquirer_prompt(questions)
        action = answers["action"]
        
        if action == "back":
            config_command(current_menu="main")
            return
        
        elif action == "exit":
            return
        
        elif action == "add":
            # Add new system prompt
            questions = [
                {
                    "type": "input",
                    "name": "name",
                    "message": "Enter a short name for the system prompt:",
                    "validate": lambda result: len(result) > 0,
                },
                {
                    "type": "input",
                    "name": "content",
                    "message": "Enter the system prompt content:",
                    "multiline": True,
                    "validate": lambda result: len(result) > 0,
                }
            ]
            
            answers = inquirer_prompt(questions)
            name = answers["name"]
            content = answers["content"]
            
            # Check if name already exists
            exists = False
            for prompt in config_manager.get_system_prompts():
                if prompt.name == name:
                    exists = True
                    break
            
            if exists:
                questions = [
                    {
                        "type": "confirm",
                        "name": "overwrite",
                        "message": f"System prompt '{name}' already exists. Overwrite?",
                        "default": False
                    }
                ]
                
                answers = inquirer_prompt(questions)
                if not answers["overwrite"]:
                    console.print("[bold yellow]Operation cancelled.[/bold yellow]")
                    # Return to system prompts menu
                    config_command(current_menu="system_prompts")
                    return
            
            # Add/update the system prompt
            config_manager.add_system_prompt(name, content)
            console.print(f"[bold green]System prompt '{name}' added.[/bold green]")
            
            # Ask if user wants to set this as active
            questions = [
                {
                    "type": "confirm",
                    "name": "set_active",
                    "message": f"Set '{name}' as the active system prompt?",
                    "default": True
                }
            ]
            
            answers = inquirer_prompt(questions)
            if answers["set_active"]:
                config_manager.set_active_system_prompt(name)
                console.print(f"[bold green]System prompt '{name}' set as active.[/bold green]")
            
            # Return to system prompts menu
            config_command(current_menu="system_prompts")
        
        elif action == "edit":
            # Edit existing system prompt
            system_prompts = config_manager.get_system_prompts()
            
            if not system_prompts:
                console.print("[bold yellow]No system prompts configured.[/bold yellow]")
                config_command(current_menu="system_prompts")
                return
            
            # Create choices for prompt selection
            prompt_choices = [
                {"name": f"{prompt.name}{' (active)' if prompt.name == active_name else ''}", "value": prompt.name}
                for prompt in system_prompts
            ]
            
            # Add back and exit options
            prompt_choices.append({"name": "⬅️ Back", "value": "back"})
            prompt_choices.append({"name": "🚪 Exit", "value": "exit"})
            
            # Prompt for selection
            questions = [
                {
                    "type": "list",
                    "name": "prompt_name",
                    "message": "Select a system prompt to edit:",
                    "choices": prompt_choices
                }
            ]
            
            answers = inquirer_prompt(questions)
            selected_prompt_name = answers["prompt_name"]
            
            if selected_prompt_name == "back":
                config_command(current_menu="system_prompts")
                return
            elif selected_prompt_name == "exit":
                return
            
            # Find the selected prompt
            selected_prompt = None
            for prompt in system_prompts:
                if prompt.name == selected_prompt_name:
                    selected_prompt = prompt
                    break
            
            if not selected_prompt:
                console.print("[bold red]System prompt not found.[/bold red]")
                config_command(current_menu="system_prompts")
                return
            
            # Edit the prompt
            questions = [
                {
                    "type": "input",
                    "name": "content",
                    "message": "Edit the system prompt content:",
                    "default": selected_prompt.content,
                    "multiline": True,
                    "validate": lambda result: len(result) > 0,
                }
            ]
            
            answers = inquirer_prompt(questions)
            content = answers["content"]
            
            # Update the system prompt
            config_manager.add_system_prompt(selected_prompt_name, content)
            console.print(f"[bold green]System prompt '{selected_prompt_name}' updated.[/bold green]")
            
            # Return to system prompts menu
            config_command(current_menu="system_prompts")
        
        elif action == "set_active":
            # Set active system prompt
            system_prompts = config_manager.get_system_prompts()
            
            if not system_prompts:
                console.print("[bold yellow]No system prompts configured.[/bold yellow]")
                config_command(current_menu="system_prompts")
                return
            
            # Create choices for prompt selection
            prompt_choices = [
                {"name": f"{prompt.name}{' (active)' if prompt.name == active_name else ''}", "value": prompt.name}
                for prompt in system_prompts
            ]
            
            # Add back and exit options
            prompt_choices.append({"name": "⬅️ Back", "value": "back"})
            prompt_choices.append({"name": "🚪 Exit", "value": "exit"})
            
            # Prompt for selection
            questions = [
                {
                    "type": "list",
                    "name": "prompt_name",
                    "message": "Select a system prompt to set as active:",
                    "choices": prompt_choices
                }
            ]
            
            answers = inquirer_prompt(questions)
            selected_prompt_name = answers["prompt_name"]
            
            if selected_prompt_name == "back":
                config_command(current_menu="system_prompts")
                return
            elif selected_prompt_name == "exit":
                return
            
            # Set the active system prompt
            success = config_manager.set_active_system_prompt(selected_prompt_name)
            if success:
                console.print(f"[bold green]System prompt '{selected_prompt_name}' set as active.[/bold green]")
            else:
                console.print("[bold red]Failed to set active system prompt.[/bold red]")
            
            # Return to system prompts menu
            config_command(current_menu="system_prompts")
        
        elif action == "remove":
            # Remove system prompt
            system_prompts = config_manager.get_system_prompts()
            
            if not system_prompts:
                console.print("[bold yellow]No system prompts configured.[/bold yellow]")
                config_command(current_menu="system_prompts")
                return
            
            # Create choices for prompt selection
            prompt_choices = [
                {"name": f"{prompt.name}{' (active)' if prompt.name == active_name else ''}", "value": prompt.name}
                for prompt in system_prompts
            ]
            
            # Add back and exit options
            prompt_choices.append({"name": "⬅️ Back", "value": "back"})
            prompt_choices.append({"name": "🚪 Exit", "value": "exit"})
            
            # Prompt for selection
            questions = [
                {
                    "type": "list",
                    "name": "prompt_name",
                    "message": "Select a system prompt to remove:",
                    "choices": prompt_choices
                }
            ]
            
            answers = inquirer_prompt(questions)
            selected_prompt_name = answers["prompt_name"]
            
            if selected_prompt_name == "back":
                config_command(current_menu="system_prompts")
                return
            elif selected_prompt_name == "exit":
                return
            
            # Confirm removal
            questions = [
                {
                    "type": "confirm",
                    "name": "confirm",
                    "message": f"Are you sure you want to remove system prompt '{selected_prompt_name}'?",
                    "default": False
                }
            ]
            
            answers = inquirer_prompt(questions)
            if not answers["confirm"]:
                console.print("[bold yellow]Operation cancelled.[/bold yellow]")
                config_command(current_menu="system_prompts")
                return
            
            # Remove the system prompt
            config_manager.remove_system_prompt(selected_prompt_name)
            console.print(f"[bold green]System prompt '{selected_prompt_name}' removed.[/bold green]")
            
            # Return to system prompts menu
            config_command(current_menu="system_prompts")
        
        elif action == "list":
            # List all system prompts
            system_prompts = config_manager.get_system_prompts()
            
            if not system_prompts:
                console.print("[bold yellow]No system prompts configured.[/bold yellow]")
                config_command(current_menu="system_prompts")
                return
            
            # Create a table to display system prompts
            table = Table(title="System Prompts")
            table.add_column("Name", style="cyan")
            table.add_column("Active", style="green")
            table.add_column("Content Preview", style="white")
            
            for prompt in system_prompts:
                is_active = "✓" if prompt.name == active_name else ""
                # Truncate content for preview
                content_preview = prompt.content[:50] + "..." if len(prompt.content) > 50 else prompt.content
                table.add_row(prompt.name, is_active, content_preview)
            
            console.print(table)
            
            # Wait for user to press enter
            input("\nPress Enter to continue...")
            
            # Return to system prompts menu
            config_command(current_menu="system_prompts")
    
    elif current_menu == "models":
        # Models management menu
        choices = [
            {"name": "➕ Add Gemini Model", "value": "add_gemini"},
            {"name": "➕ Add OpenRouter Model", "value": "add_openrouter"},
            {"name": "❌ Remove Model", "value": "remove"},
            {"name": "📋 List Configured Models", "value": "list"},
            {"name": "⬅️ Back", "value": "back"},
            {"name": "🚪 Exit", "value": "exit"}
        ]
        
        questions = [
            {
                "type": "list",
                "name": "action",
                "message": "Select an action:",
                "choices": choices
            }
        ]
        
        answers = inquirer_prompt(questions)
        action = answers["action"]
        
        if action == "back":
            config_command(current_menu="main")
            return
        
        elif action == "exit":
            return
        
        elif action == "list":
            # List configured models
            models = config_manager.get_models()
            
            if not models:
                console.print("[bold yellow]No models configured.[/bold yellow]")
                config_command(current_menu="models")
                return
            
            # Create a table to display models
            table = Table(title="Configured Models")
            table.add_column("Provider", style="cyan")
            table.add_column("Model Name", style="green")
            
            for model in models:
                table.add_row(model.provider.capitalize(), model.name)
            
            console.print(table)
            
            # Wait for user to press enter
            input("\nPress Enter to continue...")
            
            # Return to models menu
            config_command(current_menu="models")
        
        elif action == "add_gemini":
            # Add Gemini model
            if not config_manager.config.gemini.enabled or not config_manager.config.gemini.api_key:
                console.print("[bold yellow]Gemini API is not configured or enabled. Please configure it first.[/bold yellow]")
                config_command(current_menu="models")
                return
            
            # Get available Gemini models
            console.print("[bold]Fetching available Gemini models...[/bold]")
            available_models = gemini_client.get_available_models()
            
            if not available_models:
                console.print("[bold red]Failed to fetch Gemini models. Check your API key and internet connection.[/bold red]")
                config_command(current_menu="models")
                return
            
            # Create model choices
            model_choices = [
                {"name": model, "value": model} 
                for model in available_models
            ]
            
            # Add back and exit options
            model_choices.append({"name": "⬅️ Back", "value": "back"})
            model_choices.append({"name": "🚪 Exit", "value": "exit"})
            
            # Prompt for model selection
            questions = [
                {
                    "type": "list",
                    "name": "model",
                    "message": "Select a Gemini model to add:",
                    "choices": model_choices
                }
            ]
            
            answers = inquirer_prompt(questions)
            selected_model = answers["model"]
            
            if selected_model == "back":
                config_command(current_menu="models")
                return
            elif selected_model == "exit":
                return
            
            # Add the selected model to configuration
            config_manager.add_model(selected_model, "gemini")
            console.print(f"[bold green]Added {selected_model} to configuration.[/bold green]")
            
            # Return to models menu
            config_command(current_menu="models")
        
        elif action == "add_openrouter":
            # Add OpenRouter model
            if not config_manager.config.openrouter.enabled or not config_manager.config.openrouter.api_key:
                console.print("[bold yellow]OpenRouter API is not configured or enabled. Please configure it first.[/bold yellow]")
                config_command(current_menu="models")
                return
            
            # Get available OpenRouter models
            console.print("[bold]Fetching available OpenRouter models...[/bold]")
            available_models = openrouter_client.get_available_models()
            
            if not available_models:
                console.print("[bold red]Failed to fetch OpenRouter models. Check your API key and internet connection.[/bold red]")
                config_command(current_menu="models")
                return
            
            # Create model choices with more details
            model_choices = [
                {"name": f"{model['name']} ({model['id']})", "value": model['id']} 
                for model in available_models
            ]
            
            # Add back and exit options
            model_choices.append({"name": "⬅️ Back", "value": "back"})
            model_choices.append({"name": "🚪 Exit", "value": "exit"})
            
            # Prompt for model selection with fuzzy search
            questions = [
                {
                    "type": "fuzzy",
                    "name": "model",
                    "message": "Search and select an OpenRouter model to add:",
                    "choices": model_choices
                }
            ]
            
            answers = inquirer_prompt(questions)
            selected_model = answers["model"]
            
            if selected_model == "back":
                config_command(current_menu="models")
                return
            elif selected_model == "exit":
                return
            
            # Add the selected model to configuration
            config_manager.add_model(selected_model, "openrouter")
            console.print(f"[bold green]Added {selected_model} to configuration.[/bold green]")
            
            # Return to models menu
            config_command(current_menu="models")
        
        elif action == "remove":
            # Remove model
            models = config_manager.get_models()
            
            if not models:
                console.print("[bold yellow]No models configured.[/bold yellow]")
                config_command(current_menu="models")
                return
            
            # Create choices for model removal
            model_choices = [
                {"name": f"{model.provider.capitalize()}: {model.name}", "value": model.name}
                for model in models
            ]
            
            # Add back and exit options
            model_choices.append({"name": "⬅️ Back", "value": "back"})
            model_choices.append({"name": "🚪 Exit", "value": "exit"})
            
            # Prompt for model selection with fuzzy search if there are many models
            if len(model_choices) > 10:
                questions = [
                    {
                        "type": "fuzzy",
                        "name": "model",
                        "message": "Search and select a model to remove:",
                        "choices": model_choices
                    }
                ]
            else:
                questions = [
                    {
                        "type": "list",
                        "name": "model",
                        "message": "Select a model to remove:",
                        "choices": model_choices
                    }
                ]
            
            answers = inquirer_prompt(questions)
            selected_model = answers["model"]
            
            if selected_model == "back":
                config_command(current_menu="models")
                return
            elif selected_model == "exit":
                return
            
            # Remove the selected model
            config_manager.remove_model(selected_model)
            console.print(f"[bold green]Removed {selected_model} from configuration.[/bold green]")
            
            # Return to models menu
            config_command(current_menu="models")


@app.command(name="test-webdav")
def test_webdav():
    """Test WebDAV connection."""
    if not webdav_handler.is_configured():
        console.print("[bold red]WebDAV is not configured. Run 'chat2webdav config' first.[/bold red]")
        return
    
    if webdav_handler.ensure_folder_exists():
        console.print("[bold green]WebDAV connection successful![/bold green]")
    else:
        console.print("[bold red]WebDAV connection failed.[/bold red]")


if __name__ == "__main__":
    app()
