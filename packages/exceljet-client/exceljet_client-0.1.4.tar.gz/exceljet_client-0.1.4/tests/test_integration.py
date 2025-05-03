"""
Integration tests for the ExcelJet API client.

These tests require a running ExcelJet API server on localhost:8000.
"""

import os
import pytest
import time
from typing import Generator

from exceljet_client import ExceljetClient
from exceljet_client.models import BackdropNode, ContentType
from exceljet_client.exceptions import (
    NodeNotFoundError,
    ConflictError
)

# Skip all tests in this module if the SKIP_INTEGRATION_TESTS environment variable is set
pytestmark = pytest.mark.skipif(
    os.environ.get("SKIP_INTEGRATION_TESTS", "").lower() == "true",
    reason="Integration tests are disabled"
)

# Define the base URL for integration tests
INTEGRATION_BASE_URL = os.environ.get("EXCELJET_API_URL", "http://localhost:8000/api/v1")
INTEGRATION_API_KEY = os.environ.get("EXCELJET_API_KEY", "your_api_key_here")


# Check if the API server is available
def is_api_server_available() -> bool:
    """Check if the API server is available and responding."""
    client = ExceljetClient(
        api_key=INTEGRATION_API_KEY,
        base_url=INTEGRATION_BASE_URL
    )
    print(f"Checking API health at {INTEGRATION_BASE_URL}...")
    return client.health_check()


# Set up comprehensive skip reason with helpful troubleshooting information
def get_skip_reason():
    """Get a detailed skip reason with troubleshooting information."""
    if os.environ.get("SKIP_INTEGRATION_TESTS", "").lower() == "true":
        return "Integration tests are disabled (SKIP_INTEGRATION_TESTS=true)"
    
    reason = "API server is not available at " + INTEGRATION_BASE_URL
    reason += "\nIntegration tests require a running server. Please ensure:"
    reason += "\n  1. The API server is running at " + INTEGRATION_BASE_URL
    reason += "\n  2. The server has a valid /health endpoint"
    reason += "\n  3. Your network allows connections to the server"
    return reason


# Skip all tests if the API server is not available
pytestmark = pytest.mark.skipif(
    os.environ.get("SKIP_INTEGRATION_TESTS", "").lower() == "true" or not is_api_server_available(),
    reason=get_skip_reason()
)

@pytest.fixture
def integration_client() -> ExceljetClient:
    """Create a client connected to a real API server for integration testing."""
    print(f"INTEGRATION_BASE_URL: {INTEGRATION_BASE_URL}")
    client = ExceljetClient(
        api_key=INTEGRATION_API_KEY,
        base_url=INTEGRATION_BASE_URL
    )
    return client


@pytest.fixture
def test_node() -> BackdropNode:
    """Create a test node for integration testing."""
    timestamp = int(time.time())
    return BackdropNode(
        nid=1000000 + timestamp % 1000,  # Generate a unique ID
        title=f"Integration Test Node {timestamp}",
        type="function",
        path=f"functions/integration-test-{timestamp}",
        created=timestamp,
        changed=timestamp,
        status=True,
        body=f"Integration test node created at {timestamp}"
    )


@pytest.fixture
def created_node(integration_client, test_node) -> Generator[BackdropNode, None, None]:
    """
    Fixture that creates a node for testing and deletes it after the test.
    
    This ensures tests don't pollute the database even if they fail.
    """
    # Create the node
    node = integration_client.create_node(test_node)
    
    # Yield the node for use in tests
    yield node
    
    # Clean up after the test
    try:
        integration_client.delete_node(node.nid)
    except NodeNotFoundError:
        # If the node doesn't exist, it was likely deleted by the test
        pass


class TestIntegration:
    """Integration test suite that runs against a real API server."""

    def test_server_connection(self, integration_client):
        """Test that we can connect to the server and list nodes."""
        # Simply list nodes to verify connection works
        response = integration_client.list_nodes()
        assert response is not None
        assert hasattr(response, "count")
        assert hasattr(response, "items")

    def test_create_and_get_node(self, integration_client, test_node):
        """Test creating a node and then retrieving it."""
        try:
            # Create a new node
            created = integration_client.create_node(test_node)
            assert created.nid == test_node.nid
            assert created.title == test_node.title
            
            # Get the node we just created
            retrieved = integration_client.get_node(test_node.nid)
            assert retrieved.nid == test_node.nid
            assert retrieved.title == test_node.title
            assert retrieved.type == test_node.type
            assert retrieved.body == test_node.body
        finally:
            # Clean up
            try:
                integration_client.delete_node(test_node.nid)
            except NodeNotFoundError:
                pass

    def test_node_update(self, integration_client, created_node):
        """Test updating a node."""
        # Update the node
        updated_title = f"{created_node.title} - Updated"
        updated_node = BackdropNode(
            nid=created_node.nid,
            title=updated_title,
            type=created_node.type,
            path=created_node.path,
            created=created_node.created,
            changed=int(time.time()),
            status=created_node.status,
            body=f"{created_node.body} - Updated content"
        )
        
        result = integration_client.update_node(created_node.nid, updated_node)
        assert result.nid == created_node.nid
        assert result.title == updated_title
        
        # Verify the update took effect
        retrieved = integration_client.get_node(created_node.nid)
        assert retrieved.title == updated_title

    def test_node_deletion(self, integration_client, test_node):
        """Test creating and then deleting a node."""
        # Create a node
        created = integration_client.create_node(test_node)
        assert created.nid == test_node.nid
        
        # Delete the node
        integration_client.delete_node(test_node.nid)
        
        # Verify it's gone
        with pytest.raises(NodeNotFoundError):
            integration_client.get_node(test_node.nid)

    def test_bulk_operations(self, integration_client):
        """Test bulk create, update, and delete operations."""
        timestamp = int(time.time())
        # Create test nodes
        nodes = [
            BackdropNode(
                nid=2000000 + timestamp % 1000 + i,
                title=f"Bulk Test Node {i}",
                type="function",
                path=f"functions/bulk-test-{timestamp}-{i}",
                created=timestamp,
                changed=timestamp,
                status=True,
                body=f"Bulk test node {i} created at {timestamp}"
            )
            for i in range(3)
        ]
        
        try:
            # Bulk create
            result = integration_client.create_nodes_bulk(nodes)
            assert result.created == len(nodes)
            assert len(result.node_ids) == len(nodes)
            
            # Get one to verify
            retrieved = integration_client.get_node(nodes[0].nid)
            assert retrieved.nid == nodes[0].nid
            
            # Bulk update
            for node in nodes:
                node.title = f"{node.title} - Updated"
            
            update_result = integration_client.update_nodes_bulk(nodes)
            assert update_result.updated == len(nodes)
            
            # Delete the nodes
            node_ids = [node.nid for node in nodes]
            delete_result = integration_client.delete_nodes_bulk(node_ids)
            assert delete_result.deleted == len(nodes)
            
            # Verify they're gone
            with pytest.raises(NodeNotFoundError):
                integration_client.get_node(nodes[0].nid)
                
        finally:
            # Clean up any remaining nodes
            for node in nodes:
                try:
                    integration_client.delete_node(node.nid)
                except NodeNotFoundError:
                    pass

    def test_get_page_by_path(self, integration_client : ExceljetClient):
        """Test retrieving content by path."""
        # First, create a page node with a specific path
        timestamp = int(time.time())
        test_path = f"/test-page-path-{timestamp}"
        
        # The API now normalizes paths, so we don't need to worry about leading slashes
        page_node = BackdropNode(
            nid=3000000 + timestamp % 1000,
            title=f"Test Page for Path Testing",
            type="page",
            path=test_path,
            created=timestamp,
            changed=timestamp,
            status=True,
            body="This is a test page for retrieving content by path."
        )
        
        try:
            # Create the page
            created = integration_client.create_node(page_node)
            assert created.nid == page_node.nid
            
            # Get the page by path (should work with the updated API)
            page_json = integration_client.get_page(test_path, format="json")
            assert page_json.nid == page_node.nid
            assert page_json.title == page_node.title
            assert test_path in page_json.path
            
            # Get the page as markdown
            page_markdown = integration_client.get_page(test_path)
            assert isinstance(page_markdown, str)
            assert "test page for retrieving content by path" in page_markdown.lower()
            
        finally:
            # Clean up
            try:
                integration_client.delete_node(page_node.nid)
            except NodeNotFoundError:
                pass
    
    def test_get_pages_bulk(self, integration_client: ExceljetClient):
        """Test retrieving multiple pages in bulk."""
        # Create multiple test pages with specific paths
        timestamp = int(time.time())
        test_pages = []
        
        # Create 3 test pages with unique paths
        for i in range(3):
            path = f"/test-bulk-page-{timestamp}-{i}"
            page = BackdropNode(
                nid=4000000 + timestamp % 1000 + i,
                title=f"Bulk Test Page {i}",
                type="page",
                path=path,
                created=timestamp,
                changed=timestamp,
                status=True,
                body=f"This is test page {i} for bulk retrieval testing."
            )
            test_pages.append(page)
        
        try:
            # Create all the pages
            for page in test_pages:
                integration_client.create_node(page)
            
            # Get list of paths to retrieve
            paths = [page.path for page in test_pages]
            
            # Test JSON bulk retrieval
            result_json = integration_client.get_pages_bulk(paths)
            assert len(result_json) == len(test_pages)
            
            # Verify each page was retrieved correctly
            for i, page in enumerate(test_pages):
                assert page.path in result_json or page.path.lstrip('/') in result_json
                
                # Get the actual key that was used (with or without leading slash)
                key = page.path if page.path in result_json else page.path.lstrip('/')
                
                # Verify the content
                page_data = result_json[key]
                assert page_data["nid"] == page.nid
                assert page_data["title"] == page.title
                assert "test page" in page_data["body"].lower()
            
            # Test markdown bulk retrieval
            result_md = integration_client.get_pages_bulk(paths, format="markdown")
            assert len(result_md) == len(test_pages)
            
            # Verify markdown content for each page
            for page in test_pages:
                key = page.path if page.path in result_md else page.path.lstrip('/')
                assert isinstance(result_md[key], str)
                assert page.title in result_md[key] or f"# {page.title}" in result_md[key]
            
            # Test with a mix of existing and non-existent paths
            mixed_paths = paths + ["/non-existent-page-path"]
            mixed_result = integration_client.get_pages_bulk(mixed_paths)
            
            # Verify we get all existing pages plus an error for the non-existent one
            assert len(mixed_result) == len(mixed_paths)
            
            # Check for non-existent page with leading slash
            non_existent_path = "/non-existent-page-path"
            assert non_existent_path in mixed_result
            assert "error" in mixed_result[non_existent_path]
            assert "not found" in mixed_result[non_existent_path]["error"]
            
        finally:
            # Clean up all created pages
            for page in test_pages:
                try:
                    integration_client.delete_node(page.nid)
                except NodeNotFoundError:
                    pass
    
    def test_delete_all_nodes(self, integration_client):
        """Test deleting all nodes."""

    def test_markdown_export(self, integration_client, created_node):
        """Test getting a node as markdown."""
        markdown = integration_client.get_node_markdown(created_node.nid)
        assert markdown is not None
        assert isinstance(markdown, str)
        assert created_node.title in markdown or created_node.body in markdown 