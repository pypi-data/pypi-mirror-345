from finalsa.s3.client.interface.client import S3Client
from botocore.config import Config
from typing import Optional
import logging
import boto3


class S3ClientImpl(S3Client):

    def __init__(
        self,
    ) -> None:
        config = Config(signature_version='s3v4')
        self.client = boto3.client('s3', config=config)
        self.logger = logging.getLogger("finalsa.clients")

    def get_object(self, bucket: str, key: str) -> bytes:
        self.logger.info(f"Getting object from bucket {bucket} with key {key}")
        response = self.client.get_object(Bucket=bucket, Key=key)
        return response['Body'].read()

    def put_object(self, bucket: str, key: str, data: bytes, content_type: str = 'application/octet-stream'):
        self.logger.info(f"Putting object to bucket {bucket} with key {key}")
        self.client.put_object(Bucket=bucket, Key=key, Body=data,
                               ContentType=content_type)

    def delete_object(self, bucket: str, key: str):
        self.logger.info(f"Deleting object from bucket {bucket} with key {key}")
        self.client.delete_object(Bucket=bucket, Key=key)

    def list_objects(self, bucket: str) -> list:
        self.logger.info(f"Listing objects from bucket {bucket}")
        response = self.client.list_objects(Bucket=bucket)
        return response['Contents']

    def list_buckets(self) -> list:
        self.logger.info("Listing buckets")
        response = self.client.list_buckets()
        return response['Buckets']

    def create_bucket(self, bucket: str):
        self.logger.info(f"Creating bucket {bucket}")
        self.client.create_bucket(Bucket=bucket)

    def delete_bucket(self, bucket: str):
        self.logger.info(f"Deleting bucket {bucket}")
        self.client.delete_bucket(Bucket=bucket)

    def get_bucket_location(self, bucket: str) -> str:
        self.logger.info(f"Getting location of bucket {bucket}")
        response = self.client.get_bucket_location(Bucket=bucket)
        return response['LocationConstraint']

    def get_signed_url(
            self,
            bucket: str,
            key: str,
            expiration: int,
            method: Optional[str] = None,
            content_type: Optional[str] = None) -> str:
        self.logger.info(f"Getting signed url for bucket {bucket} with key {key}")
        if method is None:
            method = 'get_object'
        if content_type is not None:
            content_type = content_type
        params = {
            'Bucket': bucket,
            'Key': key
        }
        if content_type is not None:
            params['ContentType'] = content_type
        url = self.client.generate_presigned_url(
            ClientMethod=method,
            Params=params,
            ExpiresIn=expiration)
        return url
