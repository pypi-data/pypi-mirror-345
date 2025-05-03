import json

import boto3


def get_secret(name: str, region: str = "us-east-1") -> dict[str, str]:
    """Logs into the default AWS CLI session and returns a secret value."""
    client = boto3.Session().client(service_name="secretsmanager", region_name=region)
    secret = client.get_secret_value(SecretId=name)["SecretString"]
    return json.loads(secret)
