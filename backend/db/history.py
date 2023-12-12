# import time
# import hashlib
# from typing import List
# from db.connect import client, fs
#
# history_collection = client["History"]
#
#
# def compute_sha256(file_storage) -> str:
#     """Compute and return the SHA-256 hash of a file's contents."""
#     sha256 = hashlib.sha256()
#
#     for chunk in iter(lambda: file_storage.read(4096), b""):
#         sha256.update(chunk)
#
#     file_storage.seek(0)
#
#     return sha256.hexdigest()
#
#
# def compute_sha256_file(path: str) -> str:
#     sha256 = hashlib.sha256()
#
#     with open(path, 'rb') as f:
#         for chunk in iter(lambda: f.read(4096), b""):
#             sha256.update(chunk)
#         f.seek(0)
#
#     return sha256.hexdigest()
#
#
# def input_file_exists(fp: str) -> bool:
#     return history_collection.find_one({"fingerprint": fp})
#
#
# def insert_history_document(fp: str, file_id: str, assembly: str, tissue: str, algorithms: List[str]) -> str:
#     result = history_collection.insert_one({
#         "fingerprint": fp,
#         "file": file_id,  # file_id of .zip
#         "assembly": assembly,
#         "tissue": tissue,
#         "algorithms": algorithms,
#         "date": time.time()
#     })
#
#     return result.inserted_id
#
#
# # Inserts results zip and returns stored file_id from GridFS
# def insert_result_zip(path: str, input_hash: str) -> str:
#     with open(path, "rb") as f:
#         file_id = fs.put(f, filename=f"{input_hash}.zip")
#         return file_id
#
#
# def get_existing_file(file_id):
#     return fs.get(file_id)
#
#
# def get_existing_file_from_hash(fp: str):
#     file = input_file_exists(fp)
#     if not file:
#         return None
#     return get_existing_file(file["file"])
#
#
# def get_multiple_history_meta(ids: List[str]):
#     return history_collection.find({'fingerprint': {'$in': ids}})
