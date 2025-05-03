"""
ExcelJet API Client Implementation
"""

from typing import Dict, List, Optional, Any, Union
import requests
from urllib.parse import urljoin

from .models import (
    BackdropNode,
    ContentType,
    NodeIDListResponse,
    NodeResponse,
    NodeCreatedResponse,
    BulkNodeCreationResponse,
    BulkNodeUpdateResponse,
    BulkNodeDeletionResponse,
    AllNodesDeletedResponse
)
from .exceptions import (
    ExceljetApiError,
    AuthenticationError,
    NodeNotFoundError,
    InvalidRequestError,
    ApiConnectionError,
    ConflictError
)


class ExceljetClient:
    """Client for interacting with the ExcelJet API"""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.exceljet.net/api/v1",
        timeout: int = 30
    ):
        """
        Initialize the ExcelJet API client.
        
        Args:
            api_key: Your ExcelJet API key
            base_url: Base URL for the API (default: https://api.exceljet.net/api/v1)
            timeout: Request timeout in seconds (default: 30)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-KEY": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """
        Make a request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API endpoint path
            params: Query parameters
            data: Request body data
            headers: Additional headers
            
        Returns:
            Parsed response data
        
        Raises:
            AuthenticationError: If authentication fails
            NodeNotFoundError: If the requested resource is not found
            InvalidRequestError: For malformed requests
            ApiConnectionError: For network connection errors
            ConflictError: When an operation conflicts with existing resources
            ExceljetApiError: For other API errors
        """
        path = path.lstrip("/")
        url = urljoin(self.base_url + "/", path)
        request_headers = {}
        if headers:
            request_headers.update(headers)
            
        # Convert Pydantic models to dicts
        if data is not None and hasattr(data, "model_dump"):
            data = data.model_dump()
            
        # Handle list of Pydantic models
        if isinstance(data, list) and all(hasattr(item, "model_dump") for item in data):
            data = [item.model_dump() for item in data]
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=request_headers,
                timeout=self.timeout
            )
            
            # Handle HTTP errors
            if response.status_code >= 400:
                self._handle_error_response(response)
                
            # Parse response based on content type
            if response.status_code == 204:  # No content
                return None
                
            if "application/json" in response.headers.get("Content-Type", ""):
                return response.json()
            
            # Handle text responses (like markdown)
            return response.text
            
        except requests.exceptions.RequestException as e:
            raise ApiConnectionError(f"Network error: {str(e)}")
    
    def _handle_error_response(self, response: requests.Response) -> None:
        """
        Handle error responses from the API.
        
        Args:
            response: The HTTP response
            
        Raises:
            AuthenticationError: For 401 responses
            NodeNotFoundError: For 404 responses
            InvalidRequestError: For 400 responses
            ConflictError: For 409 responses
            ExceljetApiError: For other error responses
        """
        status_code = response.status_code
        error_detail = None
        error_message = f"API request failed with status code {status_code}"
        
        try:
            if "application/json" in response.headers.get("Content-Type", ""):
                data = response.json()
                if "detail" in data:
                    error_detail = data["detail"]
                    if isinstance(error_detail, dict) and "message" in error_detail:
                        error_message = error_detail["message"]
                    elif isinstance(error_detail, str):
                        error_message = error_detail
        except (ValueError, KeyError):
            # If we can't parse the JSON or it doesn't have the expected structure
            # fall back to the default message
            pass
        
        if status_code == 401:
            raise AuthenticationError(
                message="Authentication failed. Check your API key.",
                status_code=status_code,
                detail=error_detail
            )
        elif status_code == 404:
            raise NodeNotFoundError(
                message=f"Resource not found: {response.url}",
                status_code=status_code,
                detail=error_detail
            )
        elif status_code == 400:
            raise InvalidRequestError(
                message=error_message,
                status_code=status_code,
                detail=error_detail
            )
        elif status_code == 409:
            conflicting_nodes = None
            if isinstance(error_detail, dict) and "conflicting_nodes" in error_detail:
                conflicting_nodes = error_detail["conflicting_nodes"]
                
            raise ConflictError(
                message=error_message,
                status_code=status_code,
                detail=error_detail,
                conflicting_nodes=conflicting_nodes
            )
        else:
            raise ExceljetApiError(
                message=error_message,
                status_code=status_code,
                detail=error_detail
            )
    
    def health_check(self) -> bool:
        """
        Check if the API server is running and accessible.
        
        Returns:
            True if the API is up and responding, False otherwise
            
        Note:
            This method does not raise exceptions on failure, it returns False instead
        """
        try:
            # Use the health check endpoint defined in the OpenAPI spec
            self._request("GET", "/health")
            return True
        except (ApiConnectionError, ExceljetApiError):
            return False
    
    # API Endpoints
    
    def list_nodes(
        self,
        content_type: Optional[ContentType] = None,
        skip: int = 0,
        limit: int = 100
    ) -> NodeIDListResponse:
        """
        Get a list of all node IDs, with optional filtering by content type.
        
        Args:
            content_type: Filter nodes by their content type
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return (default: 100)
            
        Returns:
            A NodeIDListResponse containing:
            - items: List of nodes with their ID, title, content type, and path
            - count: Total number of matching nodes
        """
        params = {"skip": skip, "limit": limit}
        if content_type:
            params["content_type"] = content_type.value
            
        data = self._request("GET", "/nodes/", params=params)
        return NodeIDListResponse(**data)
    
    def get_page(self, path: str, format: str = "markdown") -> Union[str, NodeResponse]:
        """
        Get a page (node) by its URL path.
        
        Args:
            path: The URL path/alias of the page to retrieve (with or without leading slash)
            format: The output format, either 'markdown' (default) or 'json'
            
        Returns:
            If format is 'markdown': The page content as markdown text
            If format is 'json': A NodeResponse containing the node data
            
        Raises:
            NodeNotFoundError: If the page doesn't exist
            InvalidRequestError: If the format is invalid
        """
        # Create a properly formatted endpoint path
        clean_path = path.lstrip("/")
        endpoint_path = f"pages/{clean_path}"
        
        params = {"format": format}
        data = self._request("GET", endpoint_path, params=params)
        
        if format == "json":
            return NodeResponse(**data)
        return data
    
    def get_node(self, node_id: int) -> NodeResponse:
        """
        Get a node by ID.
        
        Args:
            node_id: The node ID to retrieve
            
        Returns:
            A NodeResponse containing the node data
            
        Raises:
            NodeNotFoundError: If the node doesn't exist
        """
        data = self._request("GET", f"/nodes/{node_id}")
        return NodeResponse(**data)
    
    def get_node_markdown(self, node_id: int) -> str:
        """
        Get a node as markdown.
        
        Args:
            node_id: The node ID to retrieve
            
        Returns:
            The node content as markdown text
            
        Raises:
            NodeNotFoundError: If the node doesn't exist
        """
        return self._request("GET", f"/nodes/{node_id}/markdown")
    
    def create_node(self, node: BackdropNode) -> NodeCreatedResponse:
        """
        Create a new node.
        
        Args:
            node: The node data to create
            
        Returns:
            A NodeCreatedResponse containing the created node data
            
        Raises:
            ConflictError: If a node with the same ID already exists
            InvalidRequestError: If the node data is invalid
        """
        data = self._request("POST", "/nodes/", data=node)
        return NodeCreatedResponse(**data)
    
    def create_nodes_bulk(self, nodes: List[BackdropNode]) -> BulkNodeCreationResponse:
        """
        Create multiple nodes in bulk.
        
        Args:
            nodes: List of nodes to create
            
        Returns:
            A BulkNodeCreationResponse with:
            - created: Count of successfully created nodes
            - node_ids: List of created node IDs
            
        Raises:
            ConflictError: If any nodes have conflicting IDs
        """
        data = self._request("POST", "/nodes/bulk", data=nodes)
        return BulkNodeCreationResponse(**data)
    
    def update_node(self, node_id: int, node: BackdropNode) -> NodeCreatedResponse:
        """
        Update an existing node.
        
        Args:
            node_id: The ID of the node to update
            node: The updated node data
            
        Returns:
            A NodeCreatedResponse containing the updated node data
            
        Raises:
            NodeNotFoundError: If the node doesn't exist
            InvalidRequestError: If the update data is invalid
        """
        data = self._request("PUT", f"/nodes/{node_id}", data=node)
        return NodeCreatedResponse(**data)
    
    def update_nodes_bulk(self, nodes: List[BackdropNode]) -> BulkNodeUpdateResponse:
        """
        Update multiple nodes in bulk.
        
        Args:
            nodes: List of nodes to update
            
        Returns:
            A BulkNodeUpdateResponse with:
            - updated: Count of successfully updated nodes
            - node_ids: List of updated node IDs
            - not_found: List of node IDs that weren't found
            - invalid: List of node IDs with validation errors
        """
        data = self._request("PUT", "/nodes/bulk", data=nodes)
        return BulkNodeUpdateResponse(**data)
    
    def delete_node(self, node_id: int) -> None:
        """
        Delete a node.
        
        Args:
            node_id: The ID of the node to delete
            
        Raises:
            NodeNotFoundError: If the node doesn't exist
        """
        self._request("DELETE", f"/nodes/{node_id}")
    
    def delete_nodes_bulk(self, node_ids: List[int]) -> BulkNodeDeletionResponse:
        """
        Delete multiple nodes in bulk.
        
        Args:
            node_ids: List of node IDs to delete
            
        Returns:
            A BulkNodeDeletionResponse with:
            - deleted: Count of successfully deleted nodes
            - node_ids: List of deleted node IDs
            - not_found: List of node IDs that weren't found
        """
        data = self._request("DELETE", "/nodes/bulk", data={"node_ids": node_ids})
        return BulkNodeDeletionResponse(**data)
    
    def delete_all_nodes(self) -> AllNodesDeletedResponse:
        """
        Delete all nodes.
        
        WARNING: This is a destructive operation that removes all nodes.
        
        Returns:
            An AllNodesDeletedResponse with:
            - message: Success message
            - deleted_count: Count of deleted nodes
        """
        data = self._request("DELETE", "/nodes/all")
        return AllNodesDeletedResponse(**data)
    
    def get_pages_bulk(
        self,
        paths: List[str],
        format: str = "json"
    ) -> Dict[str, Union[str, Dict[str, Any]]]:
        """
        Get multiple pages (nodes) by their URL paths.
        
        Args:
            paths: List of page paths to retrieve
            format: The output format, either 'json' (default) or 'markdown'
            
        Returns:
            A dictionary mapping each path to its page data
            
        Raises:
            InvalidRequestError: If the request is invalid
        """
        data = self._request(
            method="POST",
            path="/pages/bulk",
            data=paths,
            params={"format": format}
        )
        # The API returns a response with a "pages" key as defined in BulkPageResponse
        return data["pages"] 