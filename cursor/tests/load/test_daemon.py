import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import msgpack
from cursor.collection import Collection
from cursor.path import Path
from cursor.position import Position

# Import the FastAPI app
from cursor.load.daemon import app, loaded_collections
from cursor.load.daemon_client import query_cursor_service

# Create a test client
client = TestClient(app)


# Daemon server tests
def test_query_paths_empty():
    # Mock the loaded_collections to be empty
    with patch("cursor.load.daemon.loaded_collections", []):
        response = client.post("/query_paths", json={"min_vertices": 1, "limit": 10})
        assert response.status_code == 404
        assert response.json() == {"detail": "No paths found matching the criteria"}


def test_query_paths_success():
    # Create a mock collection with some paths
    mock_collection = Collection()
    path1 = Path()
    path1.add_position(Position(0, 0, 0))
    path1.add_position(Position(1, 1, 1))
    path2 = Path()
    path2.add_position(Position(0, 0, 0))
    path2.add_position(Position(1, 1, 1))
    path2.add_position(Position(2, 2, 2))
    mock_collection.add(path1)
    mock_collection.add(path2)

    # Mock the loaded_collections
    with patch("cursor.load.daemon.loaded_collections", [mock_collection]):
        response = client.post("/query_paths", json={"min_vertices": 2, "limit": 10})
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/x-msgpack"

        # Deserialize the MessagePack data
        deserialized_data = msgpack.unpackb(response.content)
        assert len(deserialized_data) == 2
        assert len(deserialized_data[0]["vertices"]) == 2
        assert len(deserialized_data[1]["vertices"]) == 3


def test_query_paths_limit():
    # Create a mock collection with some paths
    mock_collection = Collection()
    for i in range(5):
        path = Path()
        path.add_position(Position(0, 0, 0))
        path.add_position(Position(1, 1, 1))
        mock_collection.add(path)

    # Mock the loaded_collections
    with patch("cursor.load.daemon.loaded_collections", [mock_collection]):
        response = client.post("/query_paths", json={"min_vertices": 1, "limit": 3})
        assert response.status_code == 200

        # Deserialize the MessagePack data
        deserialized_data = msgpack.unpackb(response.content)
        assert len(deserialized_data) == 3


# Client tests
def test_query_cursor_service_success(monkeypatch):
    # Mock the requests.post method
    class MockResponse:
        def __init__(self):
            self.status_code = 200
            self.content = msgpack.packb(
                [
                    {"vertices": [(0, 0, 0), (1, 1, 1)], "properties": {}},
                    {"vertices": [(0, 0, 0), (1, 1, 1), (2, 2, 2)], "properties": {}},
                ]
            )

    def mock_post(*args, **kwargs):
        return MockResponse()

    # Apply the mock
    monkeypatch.setattr("requests.post", mock_post)

    # Call the function
    result = query_cursor_service(min_vertices=2, limit=10)

    # Check the result
    assert isinstance(result, Collection)
    assert len(result) == 2
    assert len(result[0]) == 2
    assert len(result[1]) == 3


def test_query_cursor_service_error(monkeypatch):
    # Mock the requests.post method
    class MockResponse:
        def __init__(self):
            self.status_code = 404
            self.text = "No paths found matching the criteria"

    def mock_post(*args, **kwargs):
        return MockResponse()

    # Apply the mock
    monkeypatch.setattr("requests.post", mock_post)

    # Call the function
    result = query_cursor_service(min_vertices=100, limit=10)

    # Check the result
    assert result is None


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__])
