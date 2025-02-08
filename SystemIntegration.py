# Copyright (c) 2025
# Licensed under the MIT License.
# See LICENSE file in the root directory of this source tree.
#
# Created by: [Aayush Chawla]
# Created on: February 7, 2025

from typing import List, Dict, Any
from Logger import Logger
import asyncio
from ai_code_sandbox import AICodeSandbox


class Functions:
    @staticmethod
    def get() -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "create_file",
                    "description": "Create a new empty file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path to the file"
                            },
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read contents of a file from anywhere on the system",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path to the file"
                            },
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_file",
                    "description": "Delete a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path to the file"
                            },
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_directory",
                    "description": "Delete a directory and its contents",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path to the directory"
                            },
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "copy_file",
                    "description": "Copy a file from source to destination",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "source": {
                                "type": "string",
                                "description": "Source file path"
                            },
                            "destination": {
                                "type": "string",
                                "description": "Destination path"
                            }
                        },
                        "required": ["source", "destination"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "move_file",
                    "description": "Move a file from source to destination",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "source": {
                                "type": "string",
                                "description": "Source file path"
                            },
                            "destination": {
                                "type": "string",
                                "description": "Destination path"
                            }
                        },
                        "required": ["source", "destination"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_path_exists",
                    "description": "Check the existence of a file/folder",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path to the file/folder to check for existence"
                            }
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "last_n_lines",
                    "description": "Read specified number of lines from a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path to the file from which to read"
                            },
                            "count": {
                                "type": "number",
                                "description": "Number of lines from the end of the file"
                            }
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "compile_code",
                    "description": "Compile source code using gcc/g++",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "source": {
                                "type": "string",
                                "description": "Source file path"
                            },
                            "output": {
                                "type": "string",
                                "description": "Output file path"
                            },
                            "compiler": {
                                "type": "string",
                                "enum": ["gcc", "g++"],
                                "description": "Compiler to use"
                            },
                            "flags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Compiler flags"
                            }
                        },
                        "required": ["source", "output", "compiler"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "fetch_url",
                    "description": "Fetch content from a URL using curl",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to fetch"
                            },
                            "output": {
                                "type": "string",
                                "description": "Output file path (optional)"
                            },
                            "headers": {
                                "type": "object",
                                "description": "HTTP headers to include"
                            }
                        },
                        "required": ["url"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "execute_command",
                    "description": "Execute any linux command",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "The linux command to execute"
                            },
                            "args": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Command line arguments for the command"
                            }
                        },
                        "required": ["command"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "execute_code",
                    "description": "Execute python code and return whatever is printed on stdout",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "The python code to execute and print results"
                            }
                        },
                        "required": ["code"]
                    }
                }
            }
        ]


class CommandExecutor:
    """Executes system commands safely."""

    def __init__(self, logger: Logger):
        self.logger = logger

    async def execute(self,
                      command: List[str], timeout: int = 30) -> Dict[str, Any]:
        cmd_str = ' '.join(command)
        self.logger.info(f"Executing command: {cmd_str}")

        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await asyncio.wait_for(process.communicate(),
                                                    timeout)
            result = {
                "success": process.returncode == 0,
                "stdout": stdout.decode(),
                "stderr": stderr.decode(),
                "return_code": process.returncode
            }

            if not result["success"]:
                self.logger.error(
                    f"Command failed: {cmd_str}\nError: {result['stderr']}"
                )
            else:
                self.logger.info(f"Command completed successfully: {cmd_str}")

            return result

        except asyncio.TimeoutError:
            self.logger.error(f"Command timed out: {cmd_str}")
            process.kill()
            return {
                "success": False,
                "error": f"Command timed out after {timeout} seconds"
            }
        except Exception as e:
            self.logger.error(f"Error executing command {cmd_str}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


class SystemCommands:
    """Implements system commands using the CommandExecutor."""

    def __init__(self, logger: Logger):
        self.executor = CommandExecutor(logger)
        self.logger = logger
        self.sandbox = None

    def __enter__(self):
        return self

    def __exit__(self,  exc_type, exc_val, exc_tb):
        if self.sandbox:
            self.sandbox.close()

    async def create_file(self, path: str) -> Dict[str, Any]:
        return await self.executor.execute(["touch", path])

    async def read_file(self, path: str) -> Dict[str, Any]:
        return await self.executor.execute(["cat", path])

    async def delete_file(self, path: str) -> Dict[str, Any]:
        return await self.executor.execute(["rm", path])

    async def delete_directory(self, path: str) -> Dict[str, Any]:
        return await self.executor.execute(["rm", "-r", path])

    async def copy_file(self, source: str, destination: str) -> Dict[str, Any]:
        return await self.executor.execute(["cp", source, destination])

    async def move_file(self, source: str, destination: str) -> Dict[str, Any]:
        return await self.executor.execute(["mv", source, destination])

    async def check_path_exists(self, path: str) -> Dict[str, Any]:
        return await self.executor.execute(["ls", "-l", path])

    async def last_n_lines(self, path: str, count: int) -> Dict[str, Any]:
        return await self.executor.execute(["tail", "-n", f"{count}", path])

    async def execute_command(self, command: str,
                              args: List[str] = []) -> Dict[str, Any]:
        return await self.executor.execute([command, *args])

    async def execute_code(self, code: str) -> Dict[str, Any]:
        # Initialize sandbox if this is the first call
        if not self.sandbox:
            self.sandbox = AICodeSandbox(
                packages=["numpy", "pandas", "scikit-learn", "tensorflow"])

        return {
            "success": True,
            "stdout": self.sandbox.run_code(code),
            "stderr": '',
            "return_code": 0
        }

    async def compile_code(
        self, source: str, output: str, compiler: str,
        flags: List[str] = None
    ) -> Dict[str, Any]:
        command = [compiler, source, "-o", output]
        if flags:
            command.extend(flags)
        return await self.executor.execute(command)

    async def fetch_url(
        self, url: str, output: str = None,
        headers: Dict[str, str] = None
    ) -> Dict[str, Any]:
        command = ["curl"]
        if headers:
            for key, value in headers.items():
                command.extend(["-H", f"{key}: {value}"])
        if output:
            command.extend(["-o", output])
        command.append(url)
        return await self.executor.execute(command)
