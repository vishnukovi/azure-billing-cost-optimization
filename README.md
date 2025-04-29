
# Azure Serverless Cost Optimization for Billing Records

## Overview
This solution archives billing records older than 3 months from Cosmos DB to Azure Blob Storage to reduce costs. The API layer transparently fetches from Blob Storage when needed.

## Components
- Azure Cosmos DB: Active billing records (< 3 months)
- Azure Blob Storage: Archived billing records (>= 3 months)
- Azure Function:
  - archive_old_records.py: Moves old data to Blob
  - retrieve_billing_record.py: Retrieves data from Cosmos DB or Blob

## How It Works
1. A timer-triggered Azure Function runs daily to move old records to Blob.
2. Retrieval logic first checks Cosmos DB, then falls back to Blob if needed.

🗂 Project Structure
azure-cost-optimization/
├── src/
│   ├── archive_old_records.py             # Timer Function to archive old billing data
│   ├── retrieve_billing_record.py         # Function to retrieve record (from Cosmos or Blob)
│   └── shared/
│       ├── cosmos_utils.py
│       └── blob_utils.py
├── requirements.txt                       # Python dependencies
├── README.md                              # Assignment guide

