# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands
- Run the agent: `python agent`
- Interactive mode: `python agent> [prompt]`
- Command-line mode: `python agent [prompt]`
- Clean context: `python agent -- --clean`
- RAG query: `python agent -- --rag <collection> <query>`
- Run tests: `cd ai-code-sandbox && pytest tests/test_sandbox.py`

## Code Style
- **Imports**: stdlib first, third-party second, local modules last
- **Naming**: PascalCase (classes), snake_case (functions/methods), UPPER_CASE (constants)
- **Private methods**: Prefix with underscore (_method_name)
- **Types**: Use typing module for annotations on params and return values
- **Docs**: Triple-quote docstrings for classes/methods, @todo for improvements
- **Formatting**: 4-space indentation, ~80 char line length
- **Strings**: Double quotes for context, single for simple strings
- **Error handling**: Specific exceptions with proper logging
- **Structure**: Class-based organization, async/await for concurrency
- **Config**: JSON files with sensible defaults