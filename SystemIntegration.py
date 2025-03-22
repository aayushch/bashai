# Copyright (c) 2025
# Licensed under the MIT License.
# See LICENSE file in the root directory of this source tree.
#
# Created by: [Aayush Chawla]
# Created on: February 7, 2025

from typing import List, Dict, Any
from Logger import Logger, Colors
import asyncio
import aiohttp
# import json
import re
import base64
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from duckduckgo_search import DDGS
from ai_code_sandbox import AICodeSandbox
import nltk
# Playwright will be imported dynamically to avoid startup dependency
# import traceback


class Functions:
    @staticmethod
    def get() -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Search the internet for information on a topic",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query"
                            },
                            "max_results": {
                                "type": "number",
                                "description": "Maximum number of results to return (default 5)"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "fetch_webpage",
                    "description": "Fetch and extract content from a webpage using a browser that can execute JavaScript",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL of the webpage to fetch"
                            },
                            "wait_for_selector": {
                                "type": "string",
                                "description": "Optional CSS selector to wait for before extracting content"
                            },
                            "timeout": {
                                "type": "number",
                                "description": "Maximum seconds to wait for the page to load (default 30)"
                            },
                            "include_links": {
                                "type": "boolean",
                                "description": "Whether to include links found on the page (default false)"
                            }
                        },
                        "required": ["url"]
                    }
                }
            },
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
                    "name": "write_file",
                    "description": "Write the specified data into the file at the provided path",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path to the file in which to write the data"
                            },
                            "data": {
                                "type": "string",
                                "description": "The data to write to the file"
                            }
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
            process = await asyncio.create_subprocess_shell(
                cmd_str,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(process.communicate(),
                                                    timeout)
            result = {
                "status": "success" if process.returncode == 0 else "error",
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
                out = result["stdout"]
                if len(out) > 1024:
                    out = out[:77] + "...<truncated>..." + out[-26:]
                self.logger.info("Command success:\n"
                                 f"  > {cmd_str}\n  > {out}")

            return result

        except asyncio.TimeoutError:
            self.logger.error(f"Command timed out: {cmd_str}")
            process.kill()
            return {
                "status": "error",
                "success": False,
                "error": f"Command timed out after {timeout} seconds"
            }
        except Exception as e:
            self.logger.error(f"Error executing command `{cmd_str}`: {str(e)}")
            return {
                "status": "error",
                "success": False,
                "error": str(e)
            }


class SystemCommands:
    """Implements system commands using the CommandExecutor."""

    def __init__(self, logger: Logger, config: Dict[str, Any]):
        self.executor = CommandExecutor(logger)
        self.config = config
        self.logger = logger
        self.sandbox = None
        self.session = None
        self.playwright_installed = False

        # Try to initialize NLTK resources at startup
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
        except Exception as e:
            self.logger.warning(f"NLTK resource download failed: {str(e)}")

    async def _ensure_playwright(self):
        """Ensure Playwright is installed with browser binaries."""
        # Assume the playwright is installed.
        return True

        # if self.playwright_installed:
        #     return True

        # try:
        #     # Import dynamically to avoid startup dependency
        #     import playwright
        #     from playwright.async_api import async_playwright

        #     # Check if browsers are installed and install if needed
        #     try:
        #         process = await asyncio.create_subprocess_shell(
        #             "playwright install chromium",
        #             stdout=asyncio.subprocess.PIPE,
        #             stderr=asyncio.subprocess.PIPE
        #         )
        #         stdout, stderr = await process.communicate()

        #         if process.returncode != 0:
        #             self.logger.warning(
        #                 f"Failed to install Playwright browsers: {stderr.decode()}")
        #             return False

        #         self.playwright_installed = True
        #         return True

        #     except Exception as e:
        #         self.logger.warning(
        #             f"Failed to install Playwright browsers: {str(e)}")
        #         return False

        # except ImportError:
        #     self.logger.warning(
        #         "Playwright is not installed. Web page rendering "
        #         "will not be available.")
        #     return False

    def __enter__(self):
        return self

    async def _ensure_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.sandbox:
            self.sandbox.close()

        if self.session and not self.session.closed:
            asyncio.create_task(self.session.close())

    async def create_file(self, path: str) -> Dict[str, Any]:
        return await self.executor.execute(["touch", path])

    async def read_file(self, path: str) -> Dict[str, Any]:
        print(f"{Colors.FG.yellow}\nRead: {path}{Colors.reset}")
        return await self.executor.execute(["cat", path])

    async def write_file(self, path: str, data: str) -> Dict[str, Any]:
        print(f"{Colors.FG.yellow}\nWrite: {path}{Colors.reset}")
        return await self.executor.execute(["echo", f"'{data}'", ">|", path])

    async def delete_file(self, path: str) -> Dict[str, Any]:
        print(f"{Colors.FG.yellow}\nDelete: {path}{Colors.reset}")
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
        """
        Execute a system command with optional arguments.

        Args:
            command: The command to execute
            args: Optional list of command line arguments

        Returns:
            Dict containing:
                success: Boolean indicating if command succeeded
                stdout: Command's stdout output
                stderr: Command's stderr output
                return_code: Command's return code
        """
        # Some models may send the command and the args as a string. Some may
        # set an empty args list as a string '[]'. We will sanitize these
        # cases here before executing.
        # First split the command if it contains command line args.
        components = command.split()

        # Now check we received a valid args as a list
        if isinstance(args, list):
            # args is a valid type. Extend the command.
            components.extend(args)

        # Get the base command and use rest as args.
        command = components.pop(0)

        # Execute with sanitized inputs.
        return await self.executor.execute([command, *components])

    async def execute_code(self, code: str) -> Dict[str, Any]:
        """
        Execute Python code in a sandboxed environment.

        Args:
            code: String containing Python code to execute

        Returns:
            Dict containing:
                success: Boolean indicating if code executed successfully
                stdout: Code's stdout output
                stderr: Code's stderr output (empty if successful)
                return_code: Return code (0 if successful)
        """
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
        """
        Compile source code using gcc/g++.

        Args:
            source: Path to the source code file
            output: Path for the compiled output file
            compiler: Compiler to use ('gcc' or 'g++')
            flags: Optional list of compiler flags

        Returns:
            Dict containing:
                success: Boolean indicating if compilation succeeded
                stdout: Compiler's stdout output
                stderr: Compiler's stderr output
                return_code: Compiler's return code
        """
        command = [compiler, source, "-o", output]
        if flags:
            # The model sometime adds a redundant -o flag in the response.
            # Since we handle -o vai the `output` param, drop any occurrence
            # of -o from the flags.
            flags = [item for item in flags if item != "-o"]
            command.extend(flags)
        return await self.executor.execute(command)

    async def fetch_url(
        self, url: str, output: str = None,
        headers: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Fetch content from a URL using curl.

        Args:
            url: URL to fetch content from
            output: Optional path to save the fetched content
            headers: Optional dict of HTTP headers to include in request

        Returns:
            Dict containing:
                success: Boolean indicating if fetch succeeded
                stdout: Curl's stdout output (response content if no output file)
                stderr: Curl's stderr output
                return_code: Curl's return code
        """
        command = ["curl"]
        if headers:
            for key, value in headers.items():
                command.extend(["-H", f"{key}: {value}"])
        if output:
            command.extend(["-o", output])
        command.append(url)
        return await self.executor.execute(command)

    async def web_search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Search the web using DuckDuckGo and return structured results.

        Args:
            query: The search query
            max_results: Maximum number of results to return (default 5)

        Returns:
            Dict containing search results with URLs, titles, and snippets
        """
        self.logger.info(f"Performing web search for: {query}")
        print(f"{Colors.FG.yellow}\nWeb Search: {query}{Colors.reset}")
        if not query.strip():
            return {
                "status": "error",
                "success": False,
                "error": "Empty search query"
            }

        try:
            ddgs = DDGS()
            results = list(ddgs.text(query, max_results=max_results))

            formatted_results = []
            for result in results:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", "")
                })

            return {
                "status": "success",
                "success": True,
                "results": formatted_results,
                "query": query,
                "total_results": len(formatted_results)
            }

        except Exception as e:
            self.logger.error(f"Web search error: {str(e)}")
            return {
                "status": "error",
                "success": False,
                "error": f"Failed to perform web search: {str(e)}"
            }

    async def fetch_webpage(self, url: str, include_links: bool = False) -> Dict[str, Any]:
        """
        Fetch a webpage, extract and process its content using BeautifulSoup (for static websites).

        Args:
            url: URL of the webpage to fetch
            include_links: Whether to include links found on the page

        Returns:
            Dict containing the processed content and metadata
        """
        self.logger.info(f"Fetching webpage (static method): {url}")

        try:
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError(f"Invalid URL: {url}")

            # Get session and fetch content
            session = await self._ensure_session()
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }

            async with session.get(url, headers=headers, timeout=30) as response:
                if response.status != 200:
                    return {
                        "status": "error",
                        "success": False,
                        "error": f"Failed to fetch URL (status code {response.status})"
                    }

                content_type = response.headers.get('Content-Type', '')
                if 'text/html' not in content_type.lower():
                    return {
                        "status": "error",
                        "success": False,
                        "error": f"URL does not contain HTML content: {content_type}"
                    }

                html = await response.text()

            # Parse with BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')

            # Remove script, style and other non-content elements
            for element in soup(['script', 'style', 'meta', 'noscript', 'iframe']):
                element.decompose()

            # Extract title
            title = soup.title.string if soup.title else "Untitled"

            # Extract main content
            # First attempt to get article content
            article_content = ""
            article_tags = soup.find_all(['article', 'main', 'div', 'section'])
            for tag in article_tags:
                if tag.get_text(strip=True):
                    article_content = tag.get_text(separator=' ', strip=True)
                    break

            # If no article content found, use body
            if not article_content:
                article_content = soup.body.get_text(
                    separator=' ', strip=True) if soup.body else ""

            # Process text to remove extra whitespace
            article_content = re.sub(r'\s+', ' ', article_content).strip()

            # Process text using NLTK to extract sentences if available
            processed_content = article_content
            try:
                from nltk.tokenize import sent_tokenize
                sentences = sent_tokenize(article_content)
                # Use only meaningful sentences (more than 5 words)
                meaningful_sentences = [
                    s for s in sentences if len(s.split()) > 5]
                processed_content = " ".join(meaningful_sentences)
            except Exception as e:
                self.logger.warning(f"NLTK processing failed: {str(e)}")

            # Collect links if requested
            links = []
            if include_links:
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if href.startswith(('http://', 'https://')):
                        full_url = href
                    else:
                        full_url = urljoin(url, href)

                    link_text = link.get_text(strip=True)
                    # Avoid empty or single-character links
                    if link_text and len(link_text) > 1:
                        links.append({
                            "url": full_url,
                            "text": link_text
                        })

            # Create a summary of the processed content
            summary = processed_content[:1000] + "..." if len(
                processed_content) > 1000 else processed_content

            return {
                "status": "success",
                "success": True,
                "url": url,
                "title": title,
                "content": processed_content,
                "summary": summary,
                "links": links if include_links else []
            }

        except aiohttp.ClientError as e:
            self.logger.error(
                f"Network error while fetching webpage: {str(e)}")
            return {
                "status": "error",
                "success": False,
                "error": f"Network error: {str(e)}"
            }
        except Exception as e:
            self.logger.error(f"Error fetching webpage: {str(e)}")
            return {
                "status": "error",
                "success": False,
                "error": f"Failed to process webpage: {str(e)}"
            }

    async def fetch_webpage_rendered(
        self, url: str, wait_for_selector: str = None,
        timeout: int = 30, include_links: bool = False
    ) -> Dict[str, Any]:
        """
        Fetch a webpage using a real browser with JS execution capabilities.

        Args:
            url: URL of the webpage to fetch
            wait_for_selector: CSS selector to wait for before extracting content
            timeout: Maximum seconds to wait for page load
            include_links: Whether to include links found on the page

        Returns:
            Dict containing the processed content and metadata
        """
        self.logger.info(f"Fetching webpage with browser automation: {url}")
        print(f"{Colors.FG.yellow}\nFetch URL: {url}{Colors.reset}")

        # Check if Playwright is installed and ready
        if not await self._ensure_playwright():
            return {
                "status": "error",
                "success": False,
                "error": "Browser automation is not available. Please install playwright: pip install playwright && playwright install chromium"
            }

        try:
            # Import here to avoid dependency at startup
            from playwright.async_api import async_playwright

            async with async_playwright() as p:

                # Launch the configured browser
                if self.config["browser"] == "chromium":
                    browser = await p.chromium.launch(headless=True)
                elif self.config["browser"] == "firefox":
                    browser = await p.firefox.launch(headless=True)
                elif self.config["browser"] == "webkit":
                    browser = await p.webkit.launch(headless=True)

                page = await browser.new_page()

                # Set user agent to avoid bot detection
                await page.set_extra_http_headers({
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                })

                # Navigate to the URL with timeout
                await page.goto(url, timeout=timeout * 1000, wait_until="networkidle")

                # Wait for specific content if selector provided
                if wait_for_selector:
                    await page.wait_for_selector(wait_for_selector, timeout=timeout * 1000)
                else:
                    # Default wait a moment for JS to execute
                    await asyncio.sleep(2)

                # Get page title
                title = await page.title()

                # Extract the fully rendered HTML content
                html_content = await page.content()

                # Get main content text
                body_text = await page.evaluate("""() => {
                    // Remove script, style elements
                    const scripts = document.querySelectorAll('script, style, noscript, iframe');
                    scripts.forEach(s => s.remove());

                    // Try to find main content area
                    const article = document.querySelector('article, main, [role="main"]');
                    if (article) {
                        return article.innerText;
                    }
                    return document.body.innerText;
                }""")

                # Extract links if requested
                links = []
                if include_links:
                    link_elements = await page.query_selector_all('a[href]')
                    for link in link_elements:
                        href = await link.get_attribute('href')
                        text = await link.text_content()
                        if href and text and len(text.strip()) > 1:
                            full_url = href if href.startswith(
                                ('http://', 'https://')) else urljoin(url, href)
                            links.append({
                                "url": full_url,
                                "text": text.strip()
                            })

                # Take a screenshot for potential further analysis
                screenshot = await page.screenshot(type="jpeg", quality=50)
                screenshot_base64 = base64.b64encode(
                    screenshot).decode('utf-8')

                # Close browser
                await browser.close()

                # Process text to remove extra whitespace
                processed_content = re.sub(r'\s+', ' ', body_text).strip()

                # Process text using NLTK to extract sentences if available
                try:
                    from nltk.tokenize import sent_tokenize
                    sentences = sent_tokenize(processed_content)
                    # Use only meaningful sentences (more than 5 words)
                    meaningful_sentences = [
                        s for s in sentences if len(s.split()) > 5]
                    processed_content = " ".join(meaningful_sentences)
                except Exception as e:
                    self.logger.warning(f"NLTK processing failed: {str(e)}")

                # Create a summary
                summary = processed_content[:1000] + "..." if len(
                    processed_content) > 1000 else processed_content

                return {
                    "status": "success",
                    "success": True,
                    "url": url,
                    "title": title,
                    "content": processed_content,
                    "summary": summary,
                    "links": links if include_links else [],
                    "screenshot_available": True
                }

        except Exception as e:
            self.logger.error(f"Error fetching webpage with browser: {str(e)}")
            return {
                "status": "error",
                "success": False,
                "error": f"Failed to process webpage with browser: {str(e)}"
            }
