import datetime
import logging
import gzip
import json
import io
import os

import azure.functions as func
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

# Environment Variables
COSMOS_ACCOUNT_URI = f"https://{os.getenv('COSMOS_DB_ACCOUNT')}.documents.azure.com:443/"
COSMOS_DB_NAME = os.getenv('COSMOS_DB_NAME')
COSMOS_CONTAINER_NAME = os.getenv('COSMOS_CONTAINER')
STORAGE_ACCOUNT_NAME = os.getenv('STORAGE_ACCOUNT')
ARCHIVE_CONTAINER_NAME = os.getenv('ARCHIVE_CONTAINER')

# Authentication
credential = DefaultAzureCredential()

# Cosmos DB Client
cosmos_client = CosmosClient(COSMOS_ACCOUNT_URI, credential)
database = cosmos_client.get_database_client(COSMOS_DB_NAME)
container = database.get_container_client(COSMOS_CONTAINER_NAME)

# Blob Storage Client
blob_service_client = BlobServiceClient(account_url=f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/", credential=credential)
archive_container_client = blob_service_client.get_container_client(ARCHIVE_CONTAINER_NAME)

def main(timer: func.TimerRequest) -> None:
    logging.info('Billing Record Archival function started.')

    now = datetime.datetime.utcnow()
    three_months_ago = now - datetime.timedelta(days=90)

    query = f"SELECT * FROM c WHERE c.timestamp < '{three_months_ago.isoformat()}'"
    items_to_archive = container.query_items(query=query, enable_cross_partition_query=True)

    for item in items_to_archive:
        billing_id = item.get('billingId')
        if not billing_id:
            continue

        try:
            # Serialize + Compress
            data = json.dumps(item).encode('utf-8')
            compressed = io.BytesIO()
            with gzip.GzipFile(fileobj=compressed, mode='w') as f_out:
                f_out.write(data)
            compressed.seek(0)

            # Path format: YYYY/MM/billingId.json.gz
            timestamp = datetime.datetime.strptime(item['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")
            blob_path = f"{timestamp.year}/{timestamp.month:02d}/{billing_id}.json.gz"

            # Upload to Blob Storage
            archive_container_client.upload_blob(
                name=blob_path,
                data=compressed,
                overwrite=True,
                content_settings={"content_type": "application/gzip"}
            )

            # Delete from Cosmos DB
            container.delete_item(item=item['id'], partition_key=item['billingId'])

            logging.info(f"Archived billing record {billing_id}")

        except Exception as e:
            logging.error(f"Failed to archive record {billing_id}: {str(e)}")

    logging.info('Billing Record Archival function completed.')

