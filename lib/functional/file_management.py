import hashlib


def calculate_md5_sum(file_name):
    md5_hash = hashlib.md5()
    with open(file_name,  "rb") as f:
        # Read and update hash in chunks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            md5_hash.update(byte_block)
        return md5_hash.hexdigest()

