import json
import base64
import h5py
import numpy as np
import time

# Sample data
data = np.random.rand(10000000)  # 1 million float values

# Save as base64 encoded JSON
json_start = time.time()
json_data = json.dumps({"data": base64.b64encode(data.tobytes()).decode()})
with open("data.json", "w") as f:
    json.dump(json_data, f)
json_save_time = time.time() - json_start

# Save as HDF5
h5_start = time.time()
with h5py.File("data.h5", "w") as f:
    f.create_dataset("data", data=data)
h5_save_time = time.time() - h5_start

# Load from base64 encoded JSON
json_load_start = time.time()
with open("data.json", "r") as f:
    json_loaded = json.load(f)
    loaded_data = np.frombuffer(base64.b64decode(json.loads(json_loaded)["data"]))
json_load_time = time.time() - json_load_start

# Load from HDF5
h5_load_start = time.time()
with h5py.File("data.h5", "r") as f:
    h5_loaded = f["data"][:]
h5_load_time = time.time() - h5_load_start

print(f"JSON save time: {json_save_time:.4f} seconds")
print(f"HDF5 save time: {h5_save_time:.4f} seconds")
print(f"JSON load time: {json_load_time:.4f} seconds")
print(f"HDF5 load time: {h5_load_time:.4f} seconds")
