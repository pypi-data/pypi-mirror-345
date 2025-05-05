from finalsa.s3.client.interface import S3Client
from .models import Document
from typing import Optional


class S3ClientTest(S3Client):

    def __init__(self) -> None:
        self.buckets = {}

    def get_object(self, bucket: str, key: str) -> Document:
        return self.buckets[bucket][key]

    def put_object(self, bucket: str, key: str, data: bytes, content_type: str = 'application/octet-stream'):
        if bucket not in self.buckets:
            self.buckets[bucket] = {}
        self.buckets[bucket][key] = Document(value=data, content_type=content_type)

    def delete_object(self, bucket: str, key: str):
        del self.buckets[bucket][key]

    def list_objects(self, bucket: str) -> list:
        return self.buckets[bucket].keys()

    def list_buckets(self) -> list:
        return self.buckets.keys()

    def create_bucket(self, bucket: str):
        self.buckets[bucket] = {}

    def delete_bucket(self, bucket: str):
        del self.buckets[bucket]

    def get_bucket_location(self, bucket: str) -> str:
        return "us-east-1"

    def get_signed_url(self, bucket: str, key: str, expiration: int, _: Optional[str] = "") -> str:
        return f"https://s3.amazonaws.com/{bucket}/{key}?Expires={expiration}"

    def clear(self):
        self.buckets = {}
