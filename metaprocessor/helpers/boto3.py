import hashlib
import os

import boto3
from tqdm import tqdm

import metaprocessor.helpers.config


class Progress:
    def __init__(self, filename: str, size: int) -> None:
        self._filename = filename
        self._size = size
        self._seen_so_far = 0
        self._progress_bar = tqdm(
            total=self._size,
            unit="B",
            unit_scale=True,
            desc=self._filename,
        )

    def __call__(self, bytes_amount: int) -> None:
        self._seen_so_far += bytes_amount
        self._progress_bar.update(bytes_amount)


def client() -> boto3.client:
    config = metaprocessor.helpers.config.read()
    return boto3.client(
        "s3",
        endpoint_url=config.get("aws", {}).get("endpoint-url"),
        region_name=config.get("aws", {}).get("region"),
        aws_access_key_id=config.get("aws", {}).get("access-key"),
        aws_secret_access_key=config.get("aws", {}).get("secret-key"),
    )


def list_objects() -> list:
    config = metaprocessor.helpers.config.read()
    return client().list_object_versions(
        Bucket=config.get("aws", {}).get("bucket"),
    )


def upload_object(
    key: str,
    file: str,
) -> None:
    config = metaprocessor.helpers.config.read()
    size = os.path.getsize(file)
    client().upload_file(
        file,
        config.get("aws", {}).get("bucket"),
        key,
        Callback=Progress(file, size),
    )


def download_object(
    key: str,
    file: str,
    size: int,
) -> None:
    config = metaprocessor.helpers.config.read()
    client().download_file(
        config.get("aws", {}).get("bucket"),
        key,
        file,
        Callback=Progress(file, size),
    )


def verify_object(filename: str, etag: str) -> bool:
    # https://zihao.me/post/calculating-etag-for-aws-s3-objects/

    et = etag[1:-1]
    if '-' in et and et == etag_checksum(filename):
        return True
    if '-' not in et and et == md5_checksum(filename):
        return True
    return False


def md5_checksum(filename: str) -> str:
    # https://zihao.me/post/calculating-etag-for-aws-s3-objects/

    m = hashlib.md5()
    with open(filename, 'rb') as f:
        for data in iter(lambda: f.read(1024 * 1024), b''):
            m.update(data)
    return m.hexdigest()


def etag_checksum(filename: str, chunk_size: int = 8 * 1024 * 1024) -> str:
    # https://zihao.me/post/calculating-etag-for-aws-s3-objects/

    md5s = []
    with open(filename, 'rb') as f:
        for data in iter(lambda: f.read(chunk_size), b''):
            md5s.append(hashlib.md5(data).digest())
    m = hashlib.md5(b"".join(md5s))
    return f'{m.hexdigest()}-{len(md5s)}'
