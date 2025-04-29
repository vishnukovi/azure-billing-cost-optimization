from shared.cosmos_utils import get_record_by_id
from shared.blob_utils import download_from_blob

def get_billing_record(record_id):
    record = get_record_by_id(record_id)
    if not record:
        record = download_from_blob(record_id)
    return record
