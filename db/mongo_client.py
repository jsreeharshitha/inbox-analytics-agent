from pymongo import MongoClient
from pymongo.server_api import ServerApi
from config import settings

_mongo_client = None

def get_client():
    """Initializes and returns the MongoDB client, caching it for reuse."""
    global _mongo_client
    if _mongo_client is None:
        try:
            # Use ServerApi for version stability if connecting to Atlas
            _mongo_client = MongoClient(
                settings.MONGO_URI, 
                server_api=ServerApi('1'),
                serverSelectionTimeoutMS=5000  # 5 second timeout
            )
            # Test connection
            _mongo_client.admin.command('ping')
            print("[*] Successfully connected to MongoDB Atlas.")
        except Exception as e:
            print(f"[!] MongoDB Connection Error: {str(e)}")
            # Fallback for local dev if needed, or re-raise
            raise e
    return _mongo_client

def get_collection(collection_name=None):
    """Initializes and returns a MongoDB collection."""
    client = get_client()
    db = client[settings.DB_NAME]
    name = collection_name or settings.COLLECTION_NAME
    return db[name]
