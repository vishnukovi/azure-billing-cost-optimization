from azure.storage.blob import BlobServiceClient
import os
import json

BLOB_CONNECTION_STRING = os.environ["BLOB_CONNECTION_STRING"]
CONTAINER_NAME = "archivedbillingrecords"

blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

def upload_to_blob(blob_name, data):
    blob_client = container_client.get_blob_client(blob=blob_name + ".json")
    blob_client.upload_blob(json.dumps(data), overwrite=True)

def download_from_blob(blob_name):
    blob_client = container_client.get_blob_client(blob=blob_name + ".json")
    try:
        blob_data = blob_client.download_blob()
        return json.loads(blob_data.readall())
    except:
        return None
