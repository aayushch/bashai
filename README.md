# Natural Language Command Tool/Agent

A command-line tool which integrates with terminal/shell and interprets natural language commands and executes them as system operations using a Local Language Model (LLM). This tool can also search the internet, fetch information from webpages, and analyze web content.

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
- RAG (Retrieval Augmented Generation) support for enhanced contextual responses
  - Create and manage document collections
  - Semantic search across indexed documents
  - Context-aware responses using local knowledge base

## Requirements

- Python 3.7+
- Local LLM server running on http://localhost:1234/v1 (tested with LM Studio)
- An LLM model which supports tool usage (Recommended Model: Qwen2.5-14B-Instruct)
- An embedding model (Recommended: text-embedding-nomic-embed-text-v1.5-embedding)
- Required Python packages:
  - docker
  - setuptools
  - twine
  - pytest
  - aiohttp
  - psutil
  - beautifulsoup4
  - duckduckgo-search
  - nltk
  - playwright (for browser-based web page rendering)
  - chromadb
  - langchain
  - langchain_core
  - langchain_community
  - sentence_transformers
  - pypdf
  - jq
  - unstructured
  - pdfminer.six
  - pi_heif
  - unstructured_pytesseract
  - pdf2image
  - pytesseract
  - opencv-python
  - tesserocr
  - unstructured-inference (Has some issues on Ubuntu ARM 64)
- Includes `ai_code_sandbox` as a submodule to execute python code in a sandbox.

## Installation

1. Clone the repository
2. Create a soft link for ai_code_sandbox:
```bash
cd bashai
git submodule update --init
ln -s ai-code-sandbox/ai_code_sandbox
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```
Note: If you have an "externally-managed-environment" you might need to create
a virtual environment for python, for your pip to work.
```bash
python3 -m venv .
source bin/activate
```

4. Install playwright browser depending on your platform and preference.
```bash
python3 -m playwright install chromium
python3 -m playwright install firefox
python3 -m playwright install webkit
```

5. Install Tesseract.

Linux:
```bash
sudo apt install tesseract
```
MacOS:
```bash
brew install tesseract
```

## Details

1. Contexts and security configuration are maintained in `~/.bashai` folder
2. Configs can be overridden by creating a `config.json` file under the `~/.bashai` directory. Sample configs:
```json
{
  "llm": {
    "api_url": "http://localhost:1234/v1",
    "model": "local-model",
    "temperature": 0.7,
    "max_tokens": 4096
  },
  "context": {
    "max_length": 4000,
    "max_age_hours": 24
  },
  "logger": {
    "level": 10
  },
  "browser": "webkit",
  "rag": {
    "provider": "huggingface",
    "model": "all-MiniLM-L6-v2",
    "data_directory": "~/.bashai/embeddings",
    "chunk_size": 500,
    "chunk_overlap": 50,
    "distance_threshold": 0.7
  }
}
```

3. Logs are generated in `/tmp`
4. Contexts are maintained per `shell` and are auto cleaned up if the shell
   is unused for a prolonged period of time. Context can also be manually cleared.
   See the "Clean Context" section below.

## Usage
- Make sure LM Studio is running and the LLM and embedding model is loaded.

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
if you add `agent` to the PATH and `chmod +x` it (recommended).

### RAG Operations
Create a new collection from documents:
```bash
agent "create a RAG collection called 'docs' from the ./documentation folder"
```

Query using RAG context:
```bash
agent "using the 'docs' collection, explain how to configure the logging system"
```

List available collections:
```bash
agent "list all RAG collections"
```

Delete a collection:
```bash
agent "delete the RAG collection named 'docs'"
```

### Clean Context
Clears the context associated with the current shell.
```bash
agent -- --clean
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
agent> create a RAG collection called 'python-docs' from ./python/docs
agent> using python-docs collection, explain the asyncio module

# As a command
$ agent "create a backup of my-file.txt"
$ agent "what is the current weather in San Francisco"
$ agent "summarize the main points from https://example.com/blog-post"
$ tail -100 /var/log/syslog | agent analyze the logs
$ agent "index my-project-docs/ as a RAG collection called 'project'"
```

## Configuration

The tool can be configured via `~/.bashai/config.json`. Here are the available options:

```json
{
  "llm": {
    "api_url": "http://localhost:1234/v1",
    "model": "local-model",
    "temperature": 0.7,
    "max_tokens": 4096
  },
  "context": {
    "max_length": 4000,
    "max_age_hours": 24
  },
  "logger": {
    "level": 10
  },
  "browser": "webkit",
  "rag": {
    "provider": "huggingface",
    "model": "all-MiniLM-L6-v2",
    "data_directory": "~/.bashai/embeddings",
    "chunk_size": 500,
    "chunk_overlap": 50
  }
}
```

### RAG Configuration Options
- `provider`: Embedding model provider (currently supports 'huggingface')
- `model`: The embedding model to use for document indexing
- `data_directory`: Where to store the embeddings and collections
- `chunk_size`: Size of text chunks for document splitting
- `chunk_overlap`: Overlap between consecutive chunks
- `distance_threshold`: Similarity threshold for retrieval (0-1)

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
mail@aay.sh
