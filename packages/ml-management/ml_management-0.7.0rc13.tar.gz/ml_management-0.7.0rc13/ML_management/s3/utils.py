import os
from dataclasses import dataclass
from pathlib import Path


def get_upload_paths(local_path: str):
    """Return all file paths in folder."""
    if os.path.isfile(local_path):
        return [StorageFilePath(storage_path=os.path.basename(local_path), local_path=local_path)], os.stat(
            local_path
        ).st_size

    local_files = [str(path) for path in Path(local_path).rglob("*") if path.is_file()]

    upload_paths = []
    size = 0
    for local_file_path in local_files:
        storage_file_path = os.path.relpath(local_file_path, local_path)
        upload_paths.append(StorageFilePath(storage_path=storage_file_path, local_path=local_file_path))
        size += os.stat(local_file_path).st_size  # size of file, in bytes

    return upload_paths, size


def get_upload_size(local_path: str):
    """Return size of folder or file."""
    return sum(f.stat().st_size for f in Path(local_path).glob("**/*") if f.is_file())


def get_bucket_size(bucket: str, remote_paths: list, paginator):
    """Return size of bucket."""
    total_bucket_size = 0
    for remote_path in remote_paths:
        page_iterator = paginator.paginate(Bucket=bucket, Prefix=remote_path)
        for page in page_iterator:
            for obj in page.get("Contents", []):
                total_bucket_size += obj["Size"]
    return total_bucket_size


@dataclass
class StorageFilePath:
    """Define paths for file in S3 Storage."""

    local_path: str
    storage_path: str

    def __post_init__(self):
        """Check the types of variables."""
        assert isinstance(self.local_path, str)
        assert isinstance(self.storage_path, str)
