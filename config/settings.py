import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Google Cloud Project Info
PROJECT_ID = os.getenv("PROJECT_ID", "grah-2026")
DATASET_ID = "mongo_sync_smart_email_manger"
TABLE_ID = "EmailData_Enriched"

# MongoDB Info (Optional if using BQ only)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "smart-email-manger"
COLLECTION_NAME = "EmailData"
