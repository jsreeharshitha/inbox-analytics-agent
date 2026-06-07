import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# Google Cloud Project Info
PROJECT_ID = os.getenv("PROJECT_ID", "grah-2026")
DATASET_ID = "fivetran_mongo_smart_email_manager"
TABLE_ID = "EmailData_Enriched_Live"

# MongoDB Info (Optional if using BQ only)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
DB_NAME = "smart_email_manager"
COLLECTION_NAME = "EmailData"
PROJECT_ID = os.getenv("PROJECT_ID", "grah-2026")