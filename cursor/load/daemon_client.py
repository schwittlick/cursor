import requests
import msgpack
from cursor.path import Path
from cursor.position import Position
from cursor.collection import Collection
from cursor.timer import timing


@timing
def query_cursor_service(min_vertices=0, max_vertices=None, limit=25):
    url = "http://localhost:8000/query_paths"
    payload = {
        "min_vertices": min_vertices,
        "max_vertices": max_vertices,
        "limit": limit,
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        # Deserialize the MessagePack data
        serialized_paths = msgpack.unpackb(response.content)

        # Convert the serialized data back to Path objects
        paths = []
        for serialized_path in serialized_paths:
            path = Path()
            for x, y, timestamp in serialized_path["vertices"]:
                path.add_position(Position(x, y, timestamp))
            path.properties = serialized_path["properties"]
            paths.append(path)

        # Create a Collection from the paths
        result_collection = Collection.from_path_list(paths)
        return result_collection
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


if __name__ == "__main__":
    # Example usage
    result = query_cursor_service(min_vertices=50, limit=1000)
    if result:
        print(result)
        # for path in result:
        # print(f"Path with {len(path)} vertices:")
        # print(f"  Start: {path.start_pos()}")
        # print(f"  End: {path.end_pos()}")
        # print(f"  Properties: {path.properties}")
        # Process the result as needed
