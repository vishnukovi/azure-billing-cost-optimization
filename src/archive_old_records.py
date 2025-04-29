from shared.cosmos_utils import get_old_records, delete_record
from shared.blob_utils import upload_to_blob

def main(mytimer):
    old_records = get_old_records(older_than_days=90)
    for record in old_records:
        upload_to_blob(record['id'], record)
        delete_record(record['id'])
