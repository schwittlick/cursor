from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from cursor.data import DataDirHandler
from cursor.load.loader import Loader
from cursor.collection import Collection
from cursor.path import Path
import msgpack

app = FastAPI()

# Global variable to store the loaded collections
loaded_collections: List[Collection] = []


class PathQuery(BaseModel):
    min_vertices: int = 0
    max_vertices: Optional[int] = None
    limit: int = 25
    # Add more query parameters as needed


@app.on_event("startup")
async def startup_event():
    global loaded_collections
    loader = Loader()
    # Assuming the data directory is at /path/to/data
    loader.load_all(DataDirHandler().recordings(), limit_files=10)
    loaded_collections = loader.all_collections()


@app.post("/query_paths")
async def query_paths(query: PathQuery):
    filtered_paths = []
    for collection in loaded_collections:
        for path in collection:
            if len(path) >= query.min_vertices and (
                query.max_vertices is None or len(path) <= query.max_vertices
            ):
                filtered_paths.append(path)
            if len(filtered_paths) >= query.limit:
                break
        if len(filtered_paths) >= query.limit:
            break

    if not filtered_paths:
        raise HTTPException(
            status_code=404, detail="No paths found matching the criteria"
        )

    result_collection = Collection.from_path_list(filtered_paths[: query.limit])

    # Convert paths to a serializable format
    serialized_paths = [
        {
            "vertices": [(v.x, v.y, v.timestamp) for v in path.vertices],
            "properties": path.properties,
        }
        for path in result_collection.paths
    ]

    # Serialize the result using MessagePack
    packed_data = msgpack.packb(serialized_paths)

    # Return the MessagePack data as a binary response
    return Response(content=packed_data, media_type="application/x-msgpack")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
