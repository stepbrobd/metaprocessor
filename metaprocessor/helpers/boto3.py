import boto3
import metaprocessor.helpers.config


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
