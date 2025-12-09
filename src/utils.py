import boto3
import json
import datetime

def log(message):
    timestamp = datetime.datetime.utcnow().isoformat()
    print(f"[{timestamp}] {message}")

def get_secret(secret_name):
    log(f"Retrieving secret: {secret_name}")

    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_name)

    data = json.loads(response["SecretString"])
    return data["value"]
