# Copyright (c) 2025
# Licensed under the MIT License.
# See LICENSE file in the root directory of this source tree.
#
# Created by: [Aayush Chawla]
# Created on: March 23, 2025

import numpy as np
import requests
import json
import logging
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import (
    BSHTMLLoader,
    CSVLoader,
    DirectoryLoader,
    Docx2txtLoader,
    JSONLoader,
    PyPDFLoader,
    TextLoader,
    UnstructuredExcelLoader,
    UnstructuredImageLoader,
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredXMLLoader,
    UnstructuredEmailLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from chromadb.config import Settings
import chromadb
from typing import Dict, List, Optional, Union, Any
import os
import glob


class MultiFormatDirectoryLoader(DirectoryLoader):
    """
    Custom directory loader that applies different document loaders based on
    file extensions.  Extends langchain's DirectoryLoader to automatically use
    the appropriate loader for each file type.
    """

    def __init__(self, path: str, silent_errors: bool = True,
                 load_hidden: bool = False, recursive: bool = False,
                 show_progress: bool = False, use_multithreading: bool = False,
                 max_concurrency: Optional[int] = None, config=None):
        """
        Initialize with the directory path and loading parameters.

        Args:
            path: Path to the directory
            silent_errors: Whether to silently ignore errors (True) or raise
                           them (False)
            load_hidden: Whether to load hidden files
            recursive: Whether to recursively search in subdirectories
            show_progress: Whether to show a progress bar
            use_multithreading: Whether to use multithreading for loading
            max_concurrency: Maximum number of threads to use if multithreading
        """
        ignored = config["rag"]["ignored_dirs"]
        super().__init__(
            path=path,
            glob="**/*",  # Default glob to match all files
            loader_cls=None,  # We'll set this per file in load()
            silent_errors=silent_errors,
            load_hidden=config["rag"]["load_hidden"],
            recursive=recursive,
            show_progress=show_progress,
            use_multithreading=use_multithreading,
            max_concurrency=max_concurrency,
            exclude=[f"**/{dir}/**" for dir in ignored]
        )
        self.config = config

    def load(self) -> List:
        """
        Load all documents from the directory with appropriate loaders based on
        file extensions.

        Returns:
            List of loaded documents
        """
        all_documents = []

        # Define file patterns and their corresponding loaders
        format_loaders = {
            # PDF files
            "**/*.pdf": PyPDFLoader,

            # Word documents
            "**/*.doc": UnstructuredWordDocumentLoader,
            "**/*.docx": UnstructuredWordDocumentLoader,

            # Excel files
            "**/*.xls": UnstructuredExcelLoader,
            "**/*.xlsx": UnstructuredExcelLoader,

            # PowerPoint files
            "**/*.ppt": UnstructuredPowerPointLoader,
            "**/*.pptx": UnstructuredPowerPointLoader,

            # HTML/XML files
            "**/*.html": UnstructuredXMLLoader,
            "**/*.htm": UnstructuredXMLLoader,
            "**/*.xml": UnstructuredXMLLoader,

            # Image files
            "**/*.jpg": UnstructuredImageLoader,
            "**/*.jpeg": UnstructuredImageLoader,
            "**/*.png": UnstructuredImageLoader,

            # Email files
            "**/*.eml": UnstructuredEmailLoader,
            "**/*.msg": UnstructuredEmailLoader,
        }

        # Process each file type with its specific loader
        for glob_pattern, loader_class in format_loaders.items():
            # Create a temporary DirectoryLoader for this specific file type
            temp_loader = DirectoryLoader(
                path=self.path,
                glob=glob_pattern,
                loader_cls=loader_class,
                silent_errors=self.silent_errors,
                load_hidden=self.load_hidden,
                recursive=self.recursive,
                show_progress=self.show_progress,
                use_multithreading=self.use_multithreading,
                max_concurrency=self.max_concurrency,
                exclude=self.exclude
            )
            all_documents.extend(temp_loader.load())

        # Process all remaining files with TextLoader
        processed_files = set()
        for pattern in format_loaders.keys():
            for file_path in self._get_file_paths(pattern):
                processed_files.add(os.path.abspath(file_path))

        # Get all files and filter out the ones we've already processed
        all_files = set([os.path.abspath(f)
                        for f in self._get_file_paths("**/*.*")])
        remaining_files = all_files - processed_files

        # Process remaining files with TextLoader
        for file_path in remaining_files:
            try:
                loader = TextLoader(file_path)
                all_documents.extend(loader.load())
            except Exception as e:
                if not self.silent_errors:
                    raise e
        return all_documents

    def _get_file_paths(self, glob_pattern: str) -> List[str]:
        """
        Get file paths matching the glob pattern.

        Args:
            glob_pattern: Glob pattern to match files

        Returns:
            List of file paths
        """
        if self.recursive:
            matches = glob.glob(os.path.join(
                self.path, glob_pattern), recursive=True)
        else:
            matches = glob.glob(os.path.join(
                self.path, glob_pattern), recursive=False)

        # Filter hidden files if needed
        if not self.load_hidden:
            matches = [f for f in matches if not any(
                part.startswith('.') for part in f.split(os.path.sep)
            )]

        def not_ignored(file_path):
            # Convert path to parts (directories in the path)
            path_parts = file_path.split("/")

            # Check if any excluded directory is in the path
            ignored = self.config["rag"]["ignored_dirs"]
            return all(dir not in path_parts for dir in ignored)

        return [f for f in matches if os.path.isfile(f) and not_ignored(f)]


class LMStudioEmbeddings(Embeddings):
    """Wrapper around LM Studio's local embeddings API."""

    def __init__(
        self,
        api_url: str = "http://localhost:1234/v1/embeddings",
        batch_size: int = 32,
        model: str = "embedding-model",
        logger=None,
        session=None
    ):
        """Initialize the LMStudioEmbeddings.

        Args:
            api_url: URL of the LM Studio embeddings API
            batch_size: Batch size for embedding requests
            model: Model identifier for LM Studio
            logger: Optional logger instance
            session: Optional aiohttp session to reuse
        """
        self.api_url = api_url
        self.batch_size = batch_size
        self.model = model
        self.logger = logger
        self.session = session
        self._own_session = False

    async def _ensure_session(self):
        """Ensure we have an aiohttp session to use, creating one if needed."""
        import aiohttp
        if self.session is None:
            self.session = aiohttp.ClientSession()
            self._own_session = True
        return self.session

    async def _close_session(self):
        """Close session if we created it."""
        if self._own_session and self.session is not None:
            await self.session.close()
            self.session = None
            self._own_session = False

    async def _embed_documents_async(self, texts: List[str]) -> List[List[float]]:
        """Async implementation of document embedding."""
        import asyncio
        embeddings = []
        session = await self._ensure_session()

        # Process texts in batches to avoid overwhelming the API
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i+self.batch_size]
            if self.logger:
                self.logger.info(
                    f"Embedding batch {i//self.batch_size + 1}, "
                    f"size: {len(batch)}")

            try:
                # Add a small delay between batches to avoid overwhelming the server
                if i > 0:
                    await asyncio.sleep(0.5)
                    
                async with session.post(
                    self.api_url,
                    headers={"Content-Type": "application/json"},
                    json={"input": batch, "model": self.model}
                ) as response:
                    if response.status != 200:
                        raise Exception(f"API returned status code {response.status}")
                    
                    data = await response.json()
                    
                    # Extract embeddings from response
                    batch_embeddings = [item["embedding"] for item in data["data"]]
                    embeddings.extend(batch_embeddings)

            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error in embedding batch: {str(e)}")
                # In case of failure, return zero embeddings as fallback
                for _ in batch:
                    # Standard embedding dimension
                    embeddings.append([0.0] * 1536)

        return embeddings

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents using LM Studio API"""
        import asyncio
        
        # We're in an async context, should just return the coroutine
        # and let the caller await it directly
        if asyncio.get_event_loop().is_running():
            if self.logger:
                self.logger.info("Already in async context, returning coroutine")
            # Return a dummy coroutine that returns fallback embeddings
            async def _run_embed():
                try:
                    return await self._embed_documents_async(texts)
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Async embedding error: {str(e)}")
                    return [[0.0] * 1536] * len(texts)
            return asyncio.ensure_future(_run_embed())
            
        # We're not in an async context, create a new event loop
        try:
            # Create a new loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                embeddings = loop.run_until_complete(self._embed_documents_async(texts))
                if self._own_session:
                    loop.run_until_complete(self._close_session())
                return embeddings
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Fatal error in embedding: {str(e)}")
                # Return zero embeddings as fallback
                return [[0.0] * 1536] * len(texts)
            finally:
                loop.close()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Event loop error: {str(e)}")
            # Return zero embeddings as fallback
            return [[0.0] * 1536] * len(texts)

    def embed_query(self, text: str) -> List[float]:
        """Embed a single text using LM Studio API"""
        import asyncio
        
        # If we're in an async context
        if asyncio.get_event_loop().is_running():
            # Create an awaitable wrapper
            async def _run_embed_query():
                result = await self._embed_documents_async([text])
                return result[0] if result else [0.0] * 1536
                
            return asyncio.ensure_future(_run_embed_query())
        else:
            # Use normal sync approach
            embeddings = self.embed_documents([text])
            return embeddings[0] if embeddings else [0.0] * 1536


# Define a global embeddings class that can be used across methods
class SimpleLMStudioEmbeddings:
    """Simple synchronous wrapper for LM Studio embeddings - keeps everything local"""
    
    def __init__(self, api_url, model, batch_size=10, logger=None):
        self.api_url = api_url
        self.model = model
        self.batch_size = batch_size
        self.logger = logger
        
    def embed_documents(self, texts):
        """Process documents in batches with simple synchronous requests"""
        import requests
        import time
        
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:min(i+self.batch_size, len(texts))]
            
            if self.logger:
                self.logger.info(f"Embedding batch {i//self.batch_size + 1}, size: {len(batch)}")
            
            # Allow some time between batches
            if i > 0:
                time.sleep(0.5)
                
            try:
                # Make synchronous request to local LLM
                response = requests.post(
                    self.api_url,
                    headers={"Content-Type": "application/json"},
                    json={"input": batch, "model": self.model},
                    timeout=60  # Longer timeout
                )
                
                if response.status_code != 200:
                    raise Exception(f"API returned status code {response.status_code}")
                    
                data = response.json()
                batch_embeddings = [item["embedding"] for item in data["data"]]
                all_embeddings.extend(batch_embeddings)
                
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error embedding batch: {str(e)}")
                # Provide fallback embeddings
                for _ in batch:
                    all_embeddings.append([0.0] * 1536)
        
        return all_embeddings
        
    def embed_query(self, text):
        """Embed a single query"""
        result = self.embed_documents([text])
        return result[0] if result else [0.0] * 1536


class RAGManager:
    def __init__(self, logger, config: Dict[str, Any]):
        self.logger = logger
        self.config = config
        self.data_dir = os.path.expanduser(
            self.config["rag"]["data_directory"])
        self.collections_metadata_path = os.path.join(
            self.data_dir, "collections.json")
        os.makedirs(self.data_dir, exist_ok=True)

        # Store embedding configuration
        self.embedding_provider = self.config["rag"]["provider"]
        self.lm_studio_url = f'{self.config["llm"]["api_url"]}/embeddings'

        # Initialize embedding model based on provider
        # Get the shared aiohttp session if one is available
        self.shared_session = None
        try:
            # See if we can access the shared session from SystemCommands
            import sys
            for module in sys.modules.values():
                if hasattr(module, 'agent') and hasattr(module.agent, 'llm_client') and \
                   hasattr(module.agent.llm_client, 'session'):
                    self.shared_session = module.agent.llm_client.session
                    self.logger.info("Using shared aiohttp session from LLMClient")
                    break
        except Exception as e:
            self.logger.warning(f"Could not access shared session: {e}")
            
        if self.embedding_provider.lower() == "lmstudio":
            self.logger.info(
                f"Using LM Studio embeddings from {self.lm_studio_url}")
            self.embeddings = LMStudioEmbeddings(
                api_url=self.lm_studio_url,
                logger=logger,
                session=self.shared_session
            )
        else:
            self.logger.info("Using HuggingFace embeddings (all-MiniLM-L6-v2)")
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.config["rag"]["model"],
                cache_folder=os.path.join(self.data_dir, "models")
            )

        # Initialize collections metadata
        if os.path.exists(self.collections_metadata_path):
            with open(self.collections_metadata_path, 'r') as f:
                self.collections = json.load(f)
        else:
            self.collections = {}
            self._save_collections_metadata()

    def _save_collections_metadata(self):
        with open(self.collections_metadata_path, 'w') as f:
            json.dump(self.collections, f)

    def _get_document_loader(self, source_path: str):
        """Get the appropriate document loader based on file type"""
        if os.path.isdir(source_path):
            return MultiFormatDirectoryLoader(path=source_path, recursive=True,
                                              config=self.config)
        elif source_path.endswith('.csv'):
            return CSVLoader(file_path=source_path)
        elif source_path.endswith('.docx') or source_path.endswith('.doc'):
            return Docx2txtLoader(file_path=source_path)
        elif source_path.endswith('.json'):
            return JSONLoader(file_path=source_path)
        elif source_path.endswith('.pdf'):
            return PyPDFLoader(file_path=source_path)
        elif source_path.endswith('.xlsx') or source_path.endswith('.xls'):
            return UnstructuredExcelLoader(file_path=source_path)
        elif (source_path.endswith('.jpg') or source_path.endswith('.png') or
              source_path.endswith('.jpeg')):
            return UnstructuredImageLoader(file_path=source_path)
        elif source_path.endswith('.pptx') or source_path.endswith('.ppt'):
            return UnstructuredPowerPointLoader(file_path=source_path)
        elif source_path.endswith('.xml') or source_path.endswith('.html'):
            return UnstructuredXMLLoader(file_path=source_path)
        elif source_path.endswith('.eml') or source_path.endswith('.msg'):
            return UnstructuredEmailLoader(file_path=source_path)
        else:
            # Default to text loader
            return TextLoader(source_path)

    async def create_collection(self, collection_name: str,
                                source_path: str) -> Dict:
        """
        Process documents and create embeddings in a named collection
        """
        try:
            self.logger.info(
                f"Creating collection '{collection_name}' from {source_path}")

            # Check if collection already exists
            if collection_name in self.collections:
                return {
                    "status": "error",
                    "message": f"Collection '{collection_name}' already exists"
                }

            # Validate source path
            if not os.path.exists(source_path):
                return {
                    "status": "error",
                    "message": f"Source path '{source_path}' does not exist"
                }

            # Load documents
            loader = self._get_document_loader(source_path)
            documents = loader.load()

            # Split documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config["rag"]["chunk_size"],
                chunk_overlap=self.config["rag"]["chunk_overlap"]
            )
            splits = text_splitter.split_documents(documents)

            # Create vectorstore
            collection_path = os.path.join(self.data_dir, collection_name)
            
            # Use simpler synchronous approach with local LLM for embeddings
            self.logger.info("Using local LM Studio for embeddings - simplifying process")
            
            # Use our global SimpleLMStudioEmbeddings class
            
            # Create our simple embeddings wrapper using the LM Studio URL
            safe_embeddings = SimpleLMStudioEmbeddings(
                api_url=self.lm_studio_url,
                model="embedding-model",
                logger=self.logger
            )
            
            # Process in manageable batches to prevent memory issues
            import asyncio
            import tempfile
            import shutil
            
            # Create temporary working directory
            temp_dir = tempfile.mkdtemp(dir=os.path.dirname(collection_path))
            self.logger.info(f"Using temporary directory for processing: {temp_dir}")
            
            try:
                # Process in smaller batches with controlled batch size
                batch_size = 5  # Small batch size for stability
                total_batches = (len(splits) + batch_size - 1) // batch_size
                
                for i in range(0, len(splits), batch_size):
                    batch = splits[i:min(i+batch_size, len(splits))]
                    current_batch = i // batch_size + 1
                    self.logger.info(f"Processing document batch {current_batch}/{total_batches}")
                    
                    # Add delay between batches to allow system breathing room
                    if i > 0:
                        await asyncio.sleep(1)
                    
                    try:
                        # Use our local embeddings
                        db = Chroma.from_documents(
                            documents=batch,
                            embedding=safe_embeddings,
                            persist_directory=temp_dir,
                            client_settings=Settings(anonymized_telemetry=False)
                        )
                        # Explicitly call persist on the Chroma instance
                        try:
                            # Different versions of Chroma have different persistence methods
                            if hasattr(db, "persist"):
                                db.persist()
                            elif hasattr(db, "_persist"):
                                db._persist()
                            else:
                                self.logger.warning("No persist method found on Chroma, collection may not be saved")
                        except Exception as persist_error:
                            self.logger.error(f"Error persisting batch: {str(persist_error)}")
                    except Exception as batch_error:
                        self.logger.error(f"Error processing batch {current_batch}: {str(batch_error)}")
                        # Continue with next batch
                
                # Move completed index to final location
                self.logger.info("Processing complete, moving to final location")
                if os.path.exists(collection_path):
                    shutil.rmtree(collection_path)
                shutil.move(temp_dir, collection_path)
                
                # Open final vectorstore without explicitly setting embeddings
                # This avoids issues with embeddings initialization
                try:
                    vectorstore = Chroma(
                        persist_directory=collection_path,
                        client_settings=Settings(anonymized_telemetry=False)
                    )
                except Exception as e:
                    self.logger.error(f"Error opening vector store: {e}")
                    # Try alternative approach with embeddings explicitly set
                    vectorstore = Chroma(
                        persist_directory=collection_path,
                        embedding_function=safe_embeddings,
                        client_settings=Settings(anonymized_telemetry=False)
                    )
                
                self.logger.info(f"Collection created at {collection_path}")
                
            except Exception as e:
                self.logger.error(f"Error during collection creation: {str(e)}")
                import traceback
                self.logger.error(traceback.format_exc())
                
                # Clean up temporary directory
                if os.path.exists(temp_dir):
                    try:
                        shutil.rmtree(temp_dir)
                    except Exception as cleanup_error:
                        self.logger.error(f"Error cleaning up temp dir: {cleanup_error}")
                
                # Re-raise to be handled by the outer catch
                raise

            # Update metadata
            self.collections[collection_name] = {
                "path": collection_path,
                "source": source_path,
                "document_count": len(documents),
                "chunk_count": len(splits)
            }
            self._save_collections_metadata()

            return {
                "status": "success",
                "message": (f"Created collection '{collection_name}' with "
                            f"{len(splits)} chunks from {len(documents)} "
                            "documents")
            }

        except Exception as e:
            import traceback
            self.logger.error(f"Error creating collection: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "status": "error",
                "message": f"Failed to create collection: {str(e)}"
            }

    async def delete_collection(self, collection_name: str) -> Dict:
        """Delete a collection"""
        try:
            if collection_name not in self.collections:
                return {
                    "status": "error",
                    "message": f"Collection '{collection_name}' does not exist"
                }

            collection_path = self.collections[collection_name]["path"]

            # Delete the actual files
            import shutil
            if os.path.exists(collection_path):
                shutil.rmtree(collection_path)

            # Remove from metadata
            del self.collections[collection_name]
            self._save_collections_metadata()

            return {
                "status": "success",
                "message": f"Deleted collection '{collection_name}'"
            }

        except Exception as e:
            self.logger.error(f"Error deleting collection: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to delete collection: {str(e)}"
            }

    async def list_collections(self) -> Dict:
        """List all available collections"""
        return {
            "status": "success",
            "collections": self.collections
        }

    async def retrieve_context(self, query: str, collection_name: str,
                               top_k: int = 3) -> Dict:
        """
        Retrieve relevant context from the specified collection
        """
        try:
            if collection_name not in self.collections:
                return {
                    "status": "error",
                    "message": f"Collection '{collection_name}' does not exist"
                }

            collection_path = self.collections[collection_name]["path"]

            # Use our simplified local LM Studio embeddings for retrieval
            # This keeps everything local while avoiding async issues
            safe_embeddings = SimpleLMStudioEmbeddings(
                api_url=self.lm_studio_url,
                model="embedding-model",
                logger=self.logger
            )

            # Load the vector store with safe embeddings
            vectorstore = Chroma(
                persist_directory=collection_path,
                embedding_function=safe_embeddings,
                client_settings=Settings(anonymized_telemetry=False)
            )
            
            self.logger.info(f"Searching collection '{collection_name}' for: {query}")

            # Retrieve documents
            docs = vectorstore.similarity_search(query, k=top_k)

            contexts = []
            for doc in docs:
                contexts.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })

            return {
                "status": "success",
                "contexts": contexts
            }

        except Exception as e:
            import traceback
            self.logger.error(f"Error retrieving context: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "status": "error",
                "message": f"Failed to retrieve context: {str(e)}"
            }
