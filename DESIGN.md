# BashAI Design Document

## Overview

BashAI is a natural language command-line interface that allows users to interact with their system using natural language. The application leverages LLMs (Large Language Models) to interpret user requests, execute appropriate system commands, and maintain conversation context between interactions.

## Architecture

BashAI follows a modular, asynchronous architecture with several key components:

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│    BashAI   │─────▶│  LLM Client │─────▶│ LLM API     │
└─────┬───────┘      └─────────────┘      └─────────────┘
      │                                           ▲
      │                                           │
      ▼                                           │
┌─────────────┐      ┌─────────────┐      ┌──────┴──────┐
│ContextManager│◀────▶│SecurityManager│    │ Function    │
└─────┬───────┘      └───────┬─────┘      │ Execution   │
      │                      │            └─────────────┘
      │                      │                   ▲
      │                      │                   │
      ▼                      ▼                   │
┌─────────────┐      ┌─────────────┐      ┌─────┴───────┐
│   Logger    │      │SystemCommands│─────▶│AICodeSandbox│
└─────────────┘      └─────┬───────┘      └─────────────┘
                           │
                           ▼
                     ┌─────────────┐
                     │ RAGManager  │
                     └─────────────┘
```

### Core Components

1. **BashAI (Main Controller)**
   - Initializes and coordinates all other components
   - Manages command processing flow
   - Handles user interaction modes (interactive shell, command-line)

2. **LLMClient**
   - Manages communication with the LLM API
   - Formats requests to the LLM and processes responses
   - Handles function calling API interactions

3. **ContextManager**
   - Stores conversation history in SQLite databases
   - Manages context window size and token usage
   - Automatically cleans up old contexts

4. **SecurityManager**
   - Classifies operations by type (READ, WRITE, DELETE, MODIFY)
   - Identifies dangerous operations that require user confirmation
   - Manages security configuration via JSON files

5. **SystemCommands**
   - Implements system-level commands/functions that can be called by the LLM
   - Provides consistent interfaces for file operations, command execution, web searches, etc.
   - Acts as a mediator between LLM function calls and actual system operations

6. **RAGManager**
   - Implements Retrieval Augmented Generation capabilities
   - Manages document collections using vector databases
   - Handles creation, deletion, and querying of collections

7. **AICodeSandbox**
   - Provides isolated code execution via Docker containers
   - Limits resources and restricts network access for security
   - Manages lifecycle of sandboxed environments

8. **Logger**
   - Provides colored logging with multiple severity levels
   - Logs to both console and files

## Data Flow

1. User inputs a command or query through one of three interfaces:
   - Interactive shell mode: `agent> [prompt]`
   - Command-line mode: `python agent [prompt]`
   - RAG query mode: `python agent -- --rag <collection> <query>`

2. BashAI processes the command:
   - Adds system prompt and relevant context from past interactions
   - Passes the formatted prompt to LLMClient

3. LLMClient communicates with the LLM API:
   - Sends formatted prompt with available functions
   - Receives response that may contain function calls

4. If the response contains function calls:
   - SecurityManager checks if the operations require confirmation
   - If confirmed (or not required), SystemCommands executes the functions
   - Results are added to the context and returned to LLMClient

5. The process repeats recursively if needed, with LLM interpreting function results
   - Final results are shown to user and stored in ContextManager

## Security Model

Security is a key consideration in BashAI with multiple protection layers:

1. **Operation Classification**
   - All operations are classified by type (READ, WRITE, DELETE, MODIFY)
   - Potentially dangerous operations require explicit user confirmation

2. **Sandboxed Code Execution**
   - Python code execution happens in isolated Docker containers
   - Network access is disabled by default
   - Resource limits are applied (CPU, memory)

3. **Configuration-Based Security**
   - Security rules are defined in JSON configuration files
   - Defaults are secure with user confirmation required for destructive operations

## Configuration System

BashAI uses a hierarchical configuration system with sensible defaults:

1. **Primary Configuration**
   - Loaded from `~/.bashai/config.json`
   - Falls back to default values if not found

2. **Configuration Categories**
   - LLM settings (API URL, model, temperature, max tokens)
   - Context management (max length, max age)
   - Logging level
   - RAG settings (embedding provider, model, chunk sizes)
   - Browser settings for web content fetching

## RAG Implementation

The RAG (Retrieval Augmented Generation) system provides context-aware responses:

1. **Collection Management**
   - Create collections from files or directories with automatic format detection
   - Use vector embeddings for semantic search
   - Support multiple embedding providers (LM Studio, HuggingFace)

2. **Document Processing**
   - Automatic format detection for various file types
   - Text chunking with configurable sizes and overlap
   - Vector storage using Chroma database

3. **Query Processing**
   - Semantic search using vector embeddings
   - Results augment LLM prompts with relevant context

## Extension Points

BashAI is designed to be extensible in several key areas:

1. **Function Definitions**
   - New capabilities can be added by extending the Functions.DEFINITIONS dictionary
   - Corresponding implementation in SystemCommands

2. **Document Loaders**
   - Additional document formats can be supported by adding loaders to MultiFormatDirectoryLoader

3. **Embedding Providers**
   - Support for different embedding models and providers

## Future Improvements

1. **Enhanced Notification System**
   - The NotificationManager is currently minimal with placeholders for expansion

2. **Better Error Handling**
   - More specific exception types and recovery mechanisms

3. **Additional Security Features**
   - Path allow/deny lists
   - More granular permission controls

4. **Performance Optimizations**
   - Batch processing for large document collections
   - Parallel processing for system commands

5. **Expanded Web Capabilities**
   - More sophisticated web scraping
   - Support for authenticated web services