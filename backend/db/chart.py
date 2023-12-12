import time
import hashlib
from typing import List
from db.connect import client, fs

chart_collection = client["Chart"]


def compute_combined_sha256(file_storage, assembly: str, organ: str, algorithms: List[str]) -> str:
    # Compute and return the SHA-256 hash of the combined contents of file_storage, assembly, organ, and algorithms.
    sha256 = hashlib.sha256()

    # Process file_storage
    for chunk in iter(lambda: file_storage.read(4096), b""):
        sha256.update(chunk)

    # Add assembly, organ, and each string in algorithms to the hash
    sha256.update(assembly.encode())
    sha256.update(organ.encode())
    for algorithm in algorithms:
        sha256.update(algorithm.encode())

    # Reset file_storage pointer, for future use
    file_storage.seek(0)

    return sha256.hexdigest()


def input_selection_exists(fp: str):
    return chart_collection.find_one({"fingerprint": fp})


def insert_history(fp: str, data: str, assembly: str, tissue: str, algorithms: List[str], result) -> str:
    with open(result, 'rb') as f:
        resultFile_id = fs.put(f)

    result = chart_collection.insert_one({
        "fingerprint": fp,
        "data": data,  # JSON data
        "assembly": assembly,
        "tissue": tissue,
        "algorithms": algorithms,
        "date": time.time(),
        "result_file": resultFile_id,
    })

    return result.inserted_id


# Inserts results zip and returns stored file_id from GridFS
def insert_result_zip(path: str, input_hash: str) -> str:
    with open(path, "rb") as f:
        file_id = fs.put(f, filename=f"{input_hash}.zip")
        return file_id


def get_existing_result(fp):
    return chart_collection.get(fp)


def get_existing_file_from_hash(fp: str):
    result = input_selection_exists(fp)
    if not result:
        return None
    return result["data"]


def get_multiple_history(ids: List[str], query = "", page = 1):
    filter = {
        'fingerprint': {'$in': ids},
        '$or': [
            {'tissue': {'$regex': query}},
            {'assembly': {'$regex': query}},
        ]
        }
    
    return chart_collection.find(filter).skip((page - 1) * 10).limit(10), chart_collection.count_documents(filter)


def get_zip_file(fp):
    file_data = chart_collection.find_one({'fingerprint': fp})
    if file_data and 'result_file' in file_data:
        file_id = file_data['result_file']
        file = fs.get(file_id)
        return file
    else:
        return None
