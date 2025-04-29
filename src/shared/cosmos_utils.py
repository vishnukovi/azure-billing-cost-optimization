from azure.cosmos import CosmosClient
import os
from datetime import datetime, timedelta

COSMOS_ENDPOINT = os.environ["COSMOS_ENDPOINT"]
COSMOS_KEY = os.environ["COSMOS_KEY"]
DATABASE_NAME = "BillingDB"
CONTAINER_NAME = "BillingRecords"

client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
container = client.get_database_client(DATABASE_NAME).get_container_client(CONTAINER_NAME)

def get_old_records(older_than_days=90):
    cutoff_date = (datetime.utcnow() - timedelta(days=older_than_days)).isoformat()
    query = f"SELECT * FROM c WHERE c.timestamp < '{cutoff_date}'"
    return list(container.query_items(query=query, enable_cross_partition_query=True))

def get_record_by_id(record_id):
    try:
        return container.read_item(item=record_id, partition_key=record_id)
    except:
        return None

def delete_record(record_id):
    try:
        container.delete_item(item=record_id, partition_key=record_id)
    except:
        pass
