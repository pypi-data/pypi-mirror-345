# Chat2WebDAV

A CLI tool for saving LLM chat conversations to WebDAV.

## Features

- Save chat conversations to a WebDAV server (Nextcloud)
- Support for multiple LLM providers:
  - Google Gemini
  - OpenRouter (with access to Claude, GPT, Llama, Mistral models)
- Fully synchronous implementation for better stability
- Terminal-based interface with rich markdown rendering
- Configurable system prompts
- Model selection with favorites and search functionality
- HTTP proxy support
- Automatic conversation saving
- Conversation topic management


## Usage

```bash
# Start a new chat
uvx chat2webdav chat

# Configure settings
uvx chat2webdav config

# Test WebDAV connection
uvx chat2webdav test-webdav
```

## Chat Commands

During a chat session, you can use the following commands:

- `/help` - Show help information
- `/config` or `/setting` - Configure settings
- `/clear` - Clear the current conversation
- `/save` - Save the conversation to WebDAV
- `/prompt` - Select a different system prompt
- `/exit` or `/quit` - Exit the chat

## Configuration

Configuration is stored in one of these locations (in order of precedence):
- Current directory: `chat2webdav.conf`
- Package directory
- User's home directory: `$HOME/.chat2webdav.conf`

You can configure:
- WebDAV connection details (URL, username, password, folder)
- API keys for Gemini and OpenRouter
- System prompts with customizable content
- HTTP/HTTPS proxies
- Model management (add, remove, select models)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
