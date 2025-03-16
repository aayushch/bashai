# Natural Language Command Tool/Agent

A command-line tool that interprets natural language commands and executes them as system operations using a Local Language Model (LLM). This tool can also search the internet, fetch information from webpages, and analyze web content.

## Features

- Natural language processing of system commands
- Internet search capabilities
- Web content analysis and extraction
- Browser-based rendering for JavaScript-heavy websites
- Interactive shell mode and command-line mode
- Context-aware command history
- Secure operation handling with user confirmations
- Local LLM integration
- Persistent context management
- Notification system

## Requirements

- Python 3.7+
- Local LLM server running on http://localhost:1234/v1 (tested with LM Studio)
- An LLM model which supports tool usage
- Required Python packages:
  - aiohttp
  - sqlite3
  - psutil
  - typing
  - beautifulsoup4
  - duckduckgo-search
  - nltk
  - playwright (for browser-based web page rendering)
- Includes `ai_code_sandbox` as a submodule to execute python code in a sandbox.

## Installation

1. Clone the repository
2. Create a soft link for ai_code_sandbox:
```bash
cs bashai
ln -s ai-code-sandbox/ai_code_sandbox
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install playwright browser depending on your platform and preference.
```bash
python3 -m playwright install chromium
python3 -m playwright install firefox
python3 -m playwright install webkit
```

5. Contexts and security configuration are maintained in `~/.bashai` folder
6. Logs are generated in `/tmp`
7. Contexts are maintained per `shell` and are auto cleaned up if the shell
is unused for a prolonged period of time. Context can also be manually cleared.
See below.

## Usage

### Interactive Shell Mode

```bash
python agent
```

### Command Line Mode
```bash
python agent <your prompt>
```
OR
```bash
agent <your prompt>
```
if you modify the `#!` in the agent and `chmod +x` it.

### Clean Context
Clears the context associated with the current shell.
```bash
python agent -- --clean
```

## Examples

```bash
# As a shell
$ python agent
agent> create a new file called test.txt
agent> show me the last 5 lines of /var/log/syslog
agent> search the web for latest Linux kernel features
agent> analyze the content from https://example.com/article
agent> fetch content from spa-webapp.com using browser rendering

# As a command
$ python agent "create a backup of my-file.txt"
$ python agent "what is the current weather in San Francisco"
$ python agent "summarize the main points from https://example.com/blog-post"
$ tail -100 /var/log/syslog | agent analyse the logs
```

## Security

The tool includes security measures for potentially dangerous operations:
- User confirmation for destructive operations
- Process isolation
- Context cleanup
- Error handling

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

[Aayush Chawla]
