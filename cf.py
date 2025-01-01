import json
import requests
from typing import List, Dict, Optional, Any
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

class CloudflareWorkerClient:
    def __init__(
            self,
            worker_url: str,
            api_token: str,
            embedding_function: Optional[Any] = None,
    ):
        """
        Initialize the Cloudflare Worker client.

        Args:
            worker_url: The URL of your deployed Worker (e.g., 'https://langchain-colbie.username.workers.dev')
            api_token: Your Cloudflare API token
            embedding_function: The embedding function to use for converting text to vectors.ts
        """
        self.worker_url = worker_url.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        self.embedding_function = embedding_function

    def add_documents(
            self,
            documents: List[Document],
            ids: Optional[List[str]] = None
    ) -> Dict:
        """
        Add documents to the vector store through the Worker.

        Args:
            documents: List of Document objects to add
            ids: Optional list of IDs for the documents
        """
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]

        texts = [doc.page_content for doc in documents]
        embeddings = self.embedding_function.embed_documents(texts)
        metadatas = [doc.metadata for doc in documents]

        response = requests.post(
            f"{self.worker_url}/add-vectors.ts",
            headers=self.headers,
            json={
                'documents': texts,
                'embeddings': embeddings,
                'metadatas': metadatas,
                'ids': ids
            }
        )
        response.raise_for_status()
        return response.json()

    def query(
            self,
            query_text: str,
            n_results: int = 10,
            filter: Optional[Dict] = None
    ) -> Dict:
        """
        Query the vector store through the Worker.

        Args:
            query_text: The text to search for
            n_results: Number of results to return
            filter: Optional metadata filter
        """
        query_embedding = self.embedding_function.embed_query(query_text)

        response = requests.post(
            f"{self.worker_url}/query",
            headers=self.headers,
            json={
                'query_embedding': query_embedding,
                'n_results': n_results,
                'filter': filter
            }
        )
        response.raise_for_status()
        return response.json()

    def delete_vectors(self, ids: List[str]) -> Dict:
        """
        Delete vectors.ts from the store through the Worker.

        Args:
            ids: List of vector IDs to delete
        """
        response = requests.delete(
            f"{self.worker_url}/delete",
            headers=self.headers,
            json={'ids': ids}
        )
        response.raise_for_status()
        return response.json()

    def get_vectors(
            self,
            ids: Optional[List[str]] = None,
            where: Optional[Dict] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            include: Optional[List[str]] = None
    ) -> Dict:
        """
        Get vectors.ts from the store through the Worker.

        Args:
            ids: Optional list of vector IDs to get
            where: Optional filter for metadata
            limit: Optional limit on the number of vectors.ts to return
            offset: Optional offset for pagination
            include: Optional list of fields to include in the response
        """
        response = requests.post(
            f"{self.worker_url}/get-vectors.ts",
            headers=self.headers,
            json={
                'ids': ids,
                'where': where,
                'limit': limit,
                'offset': offset,
                'include': include
            }
        )
        response.raise_for_status()
        return response.json()

    def update_vectors(
            self,
            ids: List[str],
            documents: List[Document],
            embeddings: Optional[List[List[float]]] = None,  # Type hint added
    ) -> Dict:
        """
        Update vectors.ts in the store through the Worker.

        Args:
            ids: List of vector IDs to update
            documents: List of Document objects with updated content
            embeddings: Optional list of updated embeddings
        """
        if embeddings is None:
            texts = [doc.page_content for doc in documents]
            embeddings = self.embedding_function.embed_documents(texts)

        metadatas = [doc.metadata for doc in documents]

        response = requests.put(
            f"{self.worker_url}/update-vectors.ts",
            headers=self.headers,
            json={
                'ids': ids,
                'documents': [doc.page_content for doc in documents],
                'embeddings': embeddings,
                'metadatas': metadatas
            }
        )
        response.raise_for_status()
        return response.json()

    def peek(self, n: int = 10) -> Dict:
        """
        Peek at a sample of vectors.ts from the store through the Worker.

        Args:
            n: Number of vectors.ts to peek at
        """
        response = requests.get(
            f"{self.worker_url}/peek?n={n}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def visualize(self, n: int = 100) -> str:
        """
        Fetch visualization data from the Worker.

        Args:
            n: Number of vectors.ts to include in the visualization data
        """
        response = requests.get(
            f"{self.worker_url}/visualize?n={n}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.text  # Return the HTML content directly