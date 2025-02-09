# Natural Language Command Tool/Agent

A command-line tool that interprets natural language commands and executes them as system operations using a Local Language Model (LLM).

## Features

- Natural language processing of system commands
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
4. Contexts and security configuration are maintained in `~/.bashai` folder
5. Logs are generated in `/tmp`
6. Contexts are maintained per `shell` and are auto cleaned up if the shell
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
python agent-- --clean
```

## Examples

```bash
# As a shell
$ python agent
nl> create a new file called test.txt
nl> show me the last 5 lines of /var/log/syslog

# As a command
$ python agent "create a backup of my-file.txt"
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
