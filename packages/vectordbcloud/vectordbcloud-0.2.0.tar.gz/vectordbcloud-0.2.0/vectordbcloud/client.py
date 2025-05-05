import os
import json
import time
import logging
from typing import Dict, List, Any, Optional, Union, Tuple, ContextManager
from contextlib import contextmanager
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .models import (
    Context,
    QueryResult,
    Subscription,
    UsageLimits,
    DeploymentResult,
    GraphRAGResult,
    OCRResult,
)
from .exceptions import (
    VectorDBCloudError,
    AuthenticationError,
    RateLimitError,
    ResourceNotFoundError,
    ValidationError,
    ServerError,
)

logger = logging.getLogger("vectordbcloud")


class VectorDBCloud:
    """
    Client for the VectorDBCloud API.
    
    This client provides access to the VectorDBCloud platform for vector database
    management, embeddings, and context management with ECP.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.vectordbcloud.com",
        timeout: int = 60,
        max_retries: int = 3,
    ):
        """
        Initialize a VectorDBCloud client.
        
        Args:
            api_key: API key for authentication. If not provided, will look for
                VECTORDBCLOUD_API_KEY environment variable.
            base_url: Base URL for the API.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retries for failed requests.
        """
        self.api_key = api_key or os.environ.get("VECTORDBCLOUD_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key must be provided or set as VECTORDBCLOUD_API_KEY environment variable"
            )
        
        self.base_url = base_url
        self.timeout = timeout
        self._ecp_token = None
        
        # Set up session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"vectordbcloud-python/0.2.0",
        }
        
        if self._ecp_token:
            headers["X-ECP-Token"] = self._ecp_token
        
        return headers
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and handle errors."""
        try:
            response_json = response.json()
        except ValueError:
            response_json = {"error": "Invalid JSON response"}
        
        if response.status_code >= 400:
            error_message = response_json.get("error", "Unknown error")
            
            if response.status_code == 401:
                raise AuthenticationError(f"Authentication failed: {error_message}")
            elif response.status_code == 404:
                raise ResourceNotFoundError(f"Resource not found: {error_message}")
            elif response.status_code == 422:
                raise ValidationError(f"Validation error: {error_message}")
            elif response.status_code == 429:
                raise RateLimitError(f"Rate limit exceeded: {error_message}")
            elif response.status_code >= 500:
                raise ServerError(f"Server error: {error_message}")
            else:
                raise VectorDBCloudError(f"API error: {error_message}")
        
        return response_json
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make a request to the API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        # If files are provided, don't use JSON
        if files:
            headers.pop("Content-Type", None)
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                files=files,
                headers=headers,
                timeout=self.timeout,
            )
        else:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=headers,
                timeout=self.timeout,
            )
        
        return self._handle_response(response)
    
    # ECP Token Management
    
    def set_ecp_token(self, token: str) -> None:
        """
        Set the ECP token for subsequent requests.
        
        Args:
            token: ECP token string
        """
        self._ecp_token = token
    
    def get_ecp_token(self) -> Optional[str]:
        """
        Get the current ECP token.
        
        Returns:
            Current ECP token or None if not set
        """
        return self._ecp_token
    
    def clear_ecp_token(self) -> None:
        """Clear the current ECP token."""
        self._ecp_token = None
    
    @contextmanager
    def context(self, metadata: Dict[str, Any]) -> ContextManager:
        """
        Context manager for ECP context.
        
        Creates a new context, sets the ECP token, and clears it when done.
        
        Args:
            metadata: Context metadata
            
        Yields:
            Context object
        """
        context = self.create_context(metadata=metadata)
        self.set_ecp_token(context.token)
        try:
            yield context
        finally:
            self.clear_ecp_token()
    
    # Context Management
    
    def create_context(self, metadata: Dict[str, Any]) -> Context:
        """
        Create a new context.
        
        Args:
            metadata: Context metadata
            
        Returns:
            Context object
        """
        response = self._request(
            method="POST",
            endpoint="/v1/contexts",
            data={"metadata": metadata},
        )
        
        return Context(
            id=response["id"],
            token=response["token"],
            metadata=response["metadata"],
            created_at=response["created_at"],
            expires_at=response["expires_at"],
        )
    
    def get_context(self, context_id: str) -> Context:
        """
        Get a context by ID.
        
        Args:
            context_id: Context ID
            
        Returns:
            Context object
        """
        response = self._request(
            method="GET",
            endpoint=f"/v1/contexts/{context_id}",
        )
        
        return Context(
            id=response["id"],
            token=response["token"],
            metadata=response["metadata"],
            created_at=response["created_at"],
            expires_at=response["expires_at"],
        )
    
    # Vector Operations
    
    def store_vectors(
        self,
        vectors: List[List[float]],
        metadata: List[Dict[str, Any]],
        context_id: Optional[str] = None,
        collection_name: str = "default",
    ) -> Dict[str, Any]:
        """
        Store vectors in the vector database.
        
        Args:
            vectors: List of vector embeddings
            metadata: List of metadata dictionaries
            context_id: Optional context ID
            collection_name: Collection name
            
        Returns:
            Response data
        """
        data = {
            "vectors": vectors,
            "metadata": metadata,
            "collection_name": collection_name,
        }
        
        if context_id:
            data["context_id"] = context_id
        
        response = self._request(
            method="POST",
            endpoint="/v1/vectors/store",
            data=data,
        )
        
        return response
    
    def query_vectors(
        self,
        query_vector: List[float],
        context_id: Optional[str] = None,
        collection_name: str = "default",
        top_k: int = 10,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[QueryResult]:
        """
        Query vectors from the vector database.
        
        Args:
            query_vector: Query vector embedding
            context_id: Optional context ID
            collection_name: Collection name
            top_k: Number of results to return
            filter: Optional filter for metadata
            
        Returns:
            List of query results
        """
        data = {
            "query_vector": query_vector,
            "collection_name": collection_name,
            "top_k": top_k,
        }
        
        if context_id:
            data["context_id"] = context_id
        
        if filter:
            data["filter"] = filter
        
        response = self._request(
            method="POST",
            endpoint="/v1/vectors/query",
            data=data,
        )
        
        return [
            QueryResult(
                id=result["id"],
                score=result["score"],
                metadata=result["metadata"],
                vector=result.get("vector"),
            )
            for result in response["results"]
        ]
    
    def delete_vectors(
        self,
        vector_ids: List[str],
        context_id: Optional[str] = None,
        collection_name: str = "default",
    ) -> Dict[str, Any]:
        """
        Delete vectors from the vector database.
        
        Args:
            vector_ids: List of vector IDs to delete
            context_id: Optional context ID
            collection_name: Collection name
            
        Returns:
            Response data
        """
        data = {
            "vector_ids": vector_ids,
            "collection_name": collection_name,
        }
        
        if context_id:
            data["context_id"] = context_id
        
        response = self._request(
            method="DELETE",
            endpoint="/v1/vectors",
            data=data,
        )
        
        return response
    
    # Collection Management
    
    def create_collection(
        self,
        collection_name: str,
        vector_dimension: int,
        metric: str = "cosine",
        db_type: str = "pgvector",
    ) -> Dict[str, Any]:
        """
        Create a new collection.
        
        Args:
            collection_name: Collection name
            vector_dimension: Vector dimension
            metric: Distance metric (cosine, euclidean, dot)
            db_type: Vector database type
            
        Returns:
            Response data
        """
        data = {
            "collection_name": collection_name,
            "vector_dimension": vector_dimension,
            "metric": metric,
            "db_type": db_type,
        }
        
        response = self._request(
            method="POST",
            endpoint="/v1/collections",
            data=data,
        )
        
        return response
    
    def list_collections(self) -> List[Dict[str, Any]]:
        """
        List all collections.
        
        Returns:
            List of collections
        """
        response = self._request(
            method="GET",
            endpoint="/v1/collections",
        )
        
        return response["collections"]
    
    def delete_collection(self, collection_name: str) -> Dict[str, Any]:
        """
        Delete a collection.
        
        Args:
            collection_name: Collection name
            
        Returns:
            Response data
        """
        response = self._request(
            method="DELETE",
            endpoint=f"/v1/collections/{collection_name}",
        )
        
        return response
    
    # Embedding Generation
    
    def generate_embeddings(
        self,
        texts: List[str],
        model: str = "qwen-gte",
    ) -> List[List[float]]:
        """
        Generate embeddings for texts.
        
        Args:
            texts: List of texts
            model: Embedding model name
            
        Returns:
            List of embeddings
        """
        data = {
            "texts": texts,
            "model": model,
        }
        
        response = self._request(
            method="POST",
            endpoint="/v1/embeddings/generate",
            data=data,
        )
        
        return response["embeddings"]
    
    def generate_multi_vector_embeddings(
        self,
        texts: List[str],
        model: str = "qwen-gte",
        chunk_size: int = 512,
        chunk_overlap: int = 50,
    ) -> List[List[List[float]]]:
        """
        Generate multi-vector embeddings for texts.
        
        Args:
            texts: List of texts
            model: Embedding model name
            chunk_size: Chunk size for text splitting
            chunk_overlap: Chunk overlap for text splitting
            
        Returns:
            List of lists of embeddings
        """
        data = {
            "texts": texts,
            "model": model,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
        }
        
        response = self._request(
            method="POST",
            endpoint="/v1/embeddings/generate-multi",
            data=data,
        )
        
        return response["embeddings"]
    
    # Subscription Management
    
    def get_subscription(self) -> Subscription:
        """
        Get current subscription.
        
        Returns:
            Subscription object
        """
        response = self._request(
            method="GET",
            endpoint="/v1/subscription",
        )
        
        return Subscription(
            plan_id=response["plan_id"],
            status=response["status"],
            current_period_start=response["current_period_start"],
            current_period_end=response["current_period_end"],
            features=response["features"],
        )
    
    def check_limits(self) -> UsageLimits:
        """
        Check usage limits.
        
        Returns:
            Usage limits object
        """
        response = self._request(
            method="GET",
            endpoint="/v1/subscription/limits",
        )
        
        return UsageLimits(
            vector_count=response["vector_count"],
            vector_limit=response["vector_limit"],
            api_calls=response["api_calls"],
            api_call_limit=response["api_call_limit"],
            storage_used=response["storage_used"],
            storage_limit=response["storage_limit"],
            approaching_limit=response.get("approaching_limit", False),
            approaching_limit_type=response.get("approaching_limit_type"),
        )
    
    # Cloud Deployment
    
    def deploy_to_aws(
        self,
        account_id: str,
        region: str,
        resources: List[Dict[str, Any]],
    ) -> DeploymentResult:
        """
        Deploy to AWS.
        
        Args:
            account_id: AWS account ID
            region: AWS region
            resources: List of resources to deploy
            
        Returns:
            Deployment result object
        """
        data = {
            "account_id": account_id,
            "region": region,
            "resources": resources,
        }
        
        response = self._request(
            method="POST",
            endpoint="/v1/deploy/aws",
            data=data,
        )
        
        return DeploymentResult(
            deployment_id=response["deployment_id"],
            status=response["status"],
            resources=response["resources"],
        )
    
    # GraphRAG Integration
    
    def graph_rag_query(
        self,
        query: str,
        context_id: Optional[str] = None,
        max_hops: int = 3,
        include_sources: bool = True,
    ) -> GraphRAGResult:
        """
        Perform a GraphRAG query.
        
        Args:
            query: Query string
            context_id: Optional context ID
            max_hops: Maximum number of hops in the graph
            include_sources: Whether to include sources in the result
            
        Returns:
            GraphRAG result object
        """
        data = {
            "query": query,
            "max_hops": max_hops,
            "include_sources": include_sources,
        }
        
        if context_id:
            data["context_id"] = context_id
        
        response = self._request(
            method="POST",
            endpoint="/v1/graph-rag/query",
            data=data,
        )
        
        return GraphRAGResult(
            answer=response["answer"],
            sources=response.get("sources", []),
            graph=response.get("graph", {}),
        )
    
    # OCR Processing
    
    def process_document(
        self,
        file_path: str,
        ocr_engine: str = "doctr",
        extract_tables: bool = True,
        extract_forms: bool = True,
    ) -> OCRResult:
        """
        Process a document with OCR.
        
        Args:
            file_path: Path to the document file
            ocr_engine: OCR engine to use
            extract_tables: Whether to extract tables
            extract_forms: Whether to extract forms
            
        Returns:
            OCR result object
        """
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f)}
            data = {
                "ocr_engine": ocr_engine,
                "extract_tables": json.dumps(extract_tables),
                "extract_forms": json.dumps(extract_forms),
            }
            
            response = self._request(
                method="POST",
                endpoint="/v1/ocr/process",
                data=data,
                files=files,
            )
        
        return OCRResult(
            text=response["text"],
            tables=response.get("tables", []),
            forms=response.get("forms", []),
            pages=response.get("pages", []),
        )
