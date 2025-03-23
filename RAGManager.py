# Copyright (c) 2025
# Licensed under the MIT License.
# See LICENSE file in the root directory of this source tree.
#
# Created by: [Aayush Chawla]
# Created on: March 23, 2025

from typing import Dict, List, Optional, Union, Any
import os
import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    TextLoader, PyPDFLoader, DirectoryLoader, CSVLoader
)
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings
import logging
import json
import requests
import numpy as np


class LMStudioEmbeddings(Embeddings):
    """Wrapper around LM Studio's local embeddings API."""

    def __init__(
        self,
        api_url: str = "http://localhost:1234/v1/embeddings",
        batch_size: int = 32,
        model: str = "embedding-model",
        logger=None
    ):
        """Initialize the LMStudioEmbeddings.

        Args:
            api_url: URL of the LM Studio embeddings API
            batch_size: Batch size for embedding requests
            model: Model identifier for LM Studio
            logger: Optional logger instance
        """
        self.api_url = api_url
        self.batch_size = batch_size
        self.model = model
        self.logger = logger

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents using LM Studio API"""
        embeddings = []

        # Process texts in batches to avoid overwhelming the API
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i+self.batch_size]
            if self.logger:
                self.logger.info(
                    f"Embedding batch {i//self.batch_size + 1}, "
                    f"size: {len(batch)}")

            try:
                response = requests.post(
                    self.api_url,
                    headers={"Content-Type": "application/json"},
                    json={"input": batch, "model": self.model}
                )
                response.raise_for_status()
                data = response.json()

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

    def embed_query(self, text: str) -> List[float]:
        """Embed a single text using LM Studio API"""
        embeddings = self.embed_documents([text])
        return embeddings[0] if embeddings else [0.0] * 1536


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
        if self.embedding_provider.lower() == "lmstudio":
            self.logger.info(
                f"Using LM Studio embeddings from {self.lm_studio_url}")
            self.embeddings = LMStudioEmbeddings(
                api_url=self.lm_studio_url,
                logger=logger
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
            return DirectoryLoader(
                source_path,
                glob="**/*.*",
                loader_cls=TextLoader
            )
        elif source_path.endswith('.pdf'):
            return PyPDFLoader(source_path)
        elif source_path.endswith('.csv'):
            return CSVLoader(source_path)
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
            vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=self.embeddings,
                persist_directory=collection_path
            )

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
            self.logger.error(f"Error creating collection: {str(e)}")
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

            # Load the vector store
            vectorstore = Chroma(
                persist_directory=collection_path,
                embedding_function=self.embeddings
            )

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
            self.logger.error(f"Error retrieving context: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to retrieve context: {str(e)}"
            }
