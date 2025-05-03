"""
Tests for the ExcelJet API client.
"""

import pytest
import responses
from unittest.mock import patch
import json
import time

from exceljet_client import ExceljetClient
from exceljet_client.models import (
    BackdropNode,
    ContentType,
    NodeIDListResponse,
    BulkNodeCreationResponse
)
from exceljet_client.exceptions import (
    AuthenticationError,
    NodeNotFoundError,
    InvalidRequestError,
    ConflictError
)


@pytest.fixture
def client():
    """Create a client for testing."""
    return ExceljetClient(
        api_key="your_api_key_here",
        base_url="http://localhost:8000/api/v1"
    )


@pytest.fixture
def mock_node():
    """Create a test node."""
    return BackdropNode(
        nid=123,
        title="Test Node",
        type="function",
        path="functions/test-node",
        created=int(time.time()),
        changed=int(time.time()),
        status=True,
        body="Test node body"
    )


class TestExceljetClient:
    """Test suite for the ExceljetClient class."""

    def test_init(self):
        """Test client initialization."""
        client = ExceljetClient(api_key="your_api_key_here", base_url="http://localhost:8000/api/v1")
        assert client.api_key == "your_api_key_here"
        assert client.base_url == "http://localhost:8000/api/v1"
        assert client.timeout == 30
        assert client.session.headers["X-API-KEY"] == "your_api_key_here"
        assert client.session.headers["Content-Type"] == "application/json"

    @responses.activate
    def test_list_nodes(self, client):
        """Test listing nodes."""
        # Mock response
        responses.add(
            responses.GET,
            "http://localhost:8000/api/v1/nodes/",
            json={
                "items": [
                    {
                        "nid": 1,
                        "title": "Test Node 1",
                        "content_type": "function",
                        "path": "functions/test-1",
                        "changed": 1620000000
                    }
                ],
                "count": 1
            },
            status=200
        )

        # Call the method
        result = client.list_nodes()

        # Check the result
        assert isinstance(result, NodeIDListResponse)
        assert result.count == 1
        assert len(result.items) == 1
        assert result.items[0].nid == 1
        assert result.items[0].title == "Test Node 1"

    @responses.activate
    def test_get_node(self, client):
        """Test getting a node."""
        # Mock response
        responses.add(
            responses.GET,
            "http://localhost:8000/api/v1/nodes/123",
            json={
                "nid": 123,
                "title": "Test Node",
                "type": "function",
                "path": "functions/test-node",
                "created": 1620000000,
                "changed": 1620000000,
                "status": True,
                "body": "Test node body"
            },
            status=200
        )

        # Call the method
        result = client.get_node(123)

        # Check the result
        assert result.nid == 123
        assert result.title == "Test Node"
        assert result.type == "function"

    @responses.activate
    def test_get_node_not_found(self, client):
        """Test getting a non-existent node."""
        # Mock response
        responses.add(
            responses.GET,
            "http://localhost:8000/api/v1/nodes/999",
            json={"detail": "Node with ID 999 not found"},
            status=404
        )

        # Call the method - should raise NodeNotFoundError
        with pytest.raises(NodeNotFoundError):
            client.get_node(999)

    @responses.activate
    def test_create_node(self, client, mock_node):
        """Test creating a node."""
        # Mock response
        node_data = mock_node.model_dump()
        responses.add(
            responses.POST,
            "http://localhost:8000/api/v1/nodes/",
            json=node_data,
            status=201
        )

        # Call the method
        result = client.create_node(mock_node)

        # Check the result
        assert result.nid == mock_node.nid
        assert result.title == mock_node.title
        assert result.type == mock_node.type

    @responses.activate
    def test_create_node_conflict(self, client, mock_node):
        """Test creating a node that already exists."""
        # Mock response
        responses.add(
            responses.POST,
            "http://localhost:8000/api/v1/nodes/",
            json={"detail": "A node with this nid already exists"},
            status=409
        )

        # Call the method - should raise ConflictError
        with pytest.raises(ConflictError):
            client.create_node(mock_node)

    @responses.activate
    def test_create_nodes_bulk(self, client, mock_node):
        """Test bulk node creation."""
        # Mock response
        responses.add(
            responses.POST,
            "http://localhost:8000/api/v1/nodes/bulk",
            json={
                "created": 1,
                "node_ids": [mock_node.nid]
            },
            status=201
        )

        # Call the method
        result = client.create_nodes_bulk([mock_node])

        # Check the result
        assert isinstance(result, BulkNodeCreationResponse)
        assert result.created == 1
        assert result.node_ids == [mock_node.nid]

    @responses.activate
    def test_update_node(self, client, mock_node):
        """Test updating a node."""
        # Mock response
        node_data = mock_node.model_dump()
        responses.add(
            responses.PUT,
            f"http://localhost:8000/api/v1/nodes/{mock_node.nid}",
            json=node_data,
            status=200
        )

        # Call the method
        result = client.update_node(mock_node.nid, mock_node)

        # Check the result
        assert result.nid == mock_node.nid
        assert result.title == mock_node.title

    @responses.activate
    def test_delete_node(self, client):
        """Test deleting a node."""
        # Mock response
        responses.add(
            responses.DELETE,
            "http://localhost:8000/api/v1/nodes/123",
            status=204
        )

        # Call the method - should not raise any exceptions
        client.delete_node(123)

    @responses.activate
    def test_delete_node_not_found(self, client):
        """Test deleting a non-existent node."""
        # Mock response
        responses.add(
            responses.DELETE,
            "http://localhost:8000/api/v1/nodes/999",
            json={"detail": "Node with ID 999 not found"},
            status=404
        )

        # Call the method - should raise NodeNotFoundError
        with pytest.raises(NodeNotFoundError):
            client.delete_node(999)

    @responses.activate
    def test_authentication_error(self, client):
        """Test authentication failure."""
        # Mock response
        responses.add(
            responses.GET,
            "http://localhost:8000/api/v1/nodes/",
            json={"detail": "Invalid API key"},
            status=401
        )

        # Call the method - should raise AuthenticationError
        with pytest.raises(AuthenticationError):
            client.list_nodes()

    @responses.activate
    def test_get_node_markdown(self, client):
        """Test getting a node as markdown."""
        # Mock response
        markdown_content = "# Test Node\n\nThis is a test node."
        responses.add(
            responses.GET,
            "http://localhost:8000/api/v1/nodes/123/markdown",
            body=markdown_content,
            status=200,
            content_type="text/plain"
        )

        # Call the method
        result = client.get_node_markdown(123)

        # Check the result
        assert result == markdown_content

    @responses.activate
    def test_get_page_markdown(self, client):
        """Test getting a page by path with markdown format."""
        # Mock response
        responses.add(
            responses.GET,
            "http://localhost:8000/api/v1/pages/test-page",
            body="# Test Page\n\nThis is a test page in markdown format.",
            status=200,
            content_type="text/markdown"
        )

        # Call the method
        result = client.get_page("test-page")

        # Check the result
        assert isinstance(result, str)
        assert "# Test Page" in result

    @responses.activate
    def test_get_page_json(self, client):
        """Test getting a page by path with JSON format."""
        # Mock response
        responses.add(
            responses.GET,
            "http://localhost:8000/api/v1/pages/test-page?format=json",
            json={
                "nid": 123,
                "title": "Test Page",
                "type": "page",
                "path": "test-page",
                "created": 1620000000,
                "changed": 1620000000,
                "status": True,
                "body": "This is a test page"
            },
            status=200
        )

        # Call the method
        result = client.get_page("test-page", format="json")

        # Check the result
        assert result.nid == 123
        assert result.title == "Test Page"
        assert result.type == "page"

    @responses.activate
    def test_get_page_not_found(self, client):
        """Test getting a non-existent page."""
        # Mock response
        responses.add(
            responses.GET,
            "http://localhost:8000/api/v1/pages/non-existent",
            json={"detail": "Page with path 'non-existent' not found"},
            status=404
        )

        # Call the method - should raise NodeNotFoundError
        with pytest.raises(NodeNotFoundError):
            client.get_page("non-existent")

    @responses.activate
    def test_get_pages_bulk(self, client):
        """Test getting multiple pages in bulk."""
        # Mock response
        responses.add(
            responses.POST,
            "http://localhost:8000/api/v1/pages/bulk",
            json={
                "pages": {
                    "page1": {
                        "nid": 123,
                        "title": "Test Page 1",
                        "type": "function",
                        "path": "page1",
                        "created": 1620000000,
                        "changed": 1620000000,
                        "status": True,
                        "body": "Test page 1 body"
                    },
                    "page2": {
                        "nid": 124,
                        "title": "Test Page 2",
                        "type": "function",
                        "path": "page2",
                        "created": 1620000000,
                        "changed": 1620000000,
                        "status": True,
                        "body": "Test page 2 body"
                    },
                    "non-existent": {
                        "error": "Page with path 'non-existent' not found"
                    }
                }
            },
            status=200
        )

        # Call the method
        result = client.get_pages_bulk(["page1", "page2", "non-existent"])

        # Check the result
        assert len(result) == 3
        assert result["page1"]["nid"] == 123
        assert result["page1"]["title"] == "Test Page 1"
        assert result["page2"]["nid"] == 124
        assert result["page2"]["title"] == "Test Page 2"
        assert "error" in result["non-existent"]
        assert result["non-existent"]["error"] == "Page with path 'non-existent' not found"

    @responses.activate
    def test_get_pages_bulk_markdown(self, client):
        """Test getting multiple pages in bulk with markdown format."""
        # Mock response
        responses.add(
            responses.POST,
            "http://localhost:8000/api/v1/pages/bulk",
            json={
                "pages": {
                    "page1": "# Test Page 1\n\nTest page 1 body",
                    "page2": "# Test Page 2\n\nTest page 2 body",
                    "non-existent": {
                        "error": "Page with path 'non-existent' not found"
                    }
                }
            },
            status=200
        )

        # Call the method
        result = client.get_pages_bulk(["page1", "page2", "non-existent"], format="markdown")

        # Check the result
        assert len(result) == 3
        assert result["page1"] == "# Test Page 1\n\nTest page 1 body"
        assert result["page2"] == "# Test Page 2\n\nTest page 2 body"
        assert "error" in result["non-existent"]
        assert result["non-existent"]["error"] == "Page with path 'non-existent' not found" 