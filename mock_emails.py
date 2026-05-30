import uuid
import random
from datetime import datetime, timezone

def generate_mock_emails(count=50):
    subjects = [
        "Urgent: Project Update Required", "Invoice for last month", "Weekly Sync Meeting",
        "Welcome to the team!", "Subscription renewal notice", "Feedback on your recent submission",
        "Security Alert: New login detected", "Lunch on Friday?", "Bug report #402", "API token rotation"
    ]
    senders = [
        "boss@company.com", "billing@saas.io", "hr@startup.co", "noreply@cloudprovider.com",
        "colleague.dev@engineering.org", "support@tooling.net", "friend@domain.xyz"
    ]
    snippets = [
        "Hi team, we need to quickly review the milestones for the upcoming release...",
        "Your invoice is attached. Please process payment by the end of the week...",
        "Just a reminder that our recurring sync is scheduled for tomorrow at 10 AM...",
        "Please welcome our newest engineer to the repository group...",
        "This is a pre-notification that your premium tier will auto-renew shortly...",
    ]

    mock_documents = []

    for _ in range(count):
        # Generate a mock 1024-dimension vector embedding (floats between -1.0 and 1.0)
        # simulating Vertex AI output
        mock_embedding = [round(random.uniform(-1.0, 1.0), 4) for _ in range(1024)]
        
        doc = {
            "subject": random.choice(subjects) + f" (Ref: {random.randint(100, 999)})",
            "sender": random.choice(senders),
            "message_id": f"msg_{uuid.uuid4().hex[:16]}",
            "vector_embedding": mock_embedding,
            "label": "unclassified",
            "email_semantic_score": 0.0,
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "snippet": random.choice(snippets)
        }
        mock_documents.append(doc)
        
    return mock_documents

# Generate the 50 emails
emails_data = generate_mock_emails(50)
print(f"Successfully generated {len(emails_data)} mock documents.")

from pymongo import MongoClient
import certifi

# Replace with your actual Atlas connection string (ensure password and dbname are correct)
CONNECTION_STRING = "mongodb+srv://dbUser:dbUserPassword@email-cluster.lytm53b.mongodb.net/?appName=email-cluster"

try:
    # Connect to Atlas
    client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())
    db = client["smart-email-manger"]
    collection = db["EmailData"]
    
    # Bulk insert the 50 generated records
    result = collection.insert_many(emails_data)
    print(f"Success! Inserted {len(result.inserted_ids)} documents into smart-email-manger.EmailData.")
    
except Exception as e:
    print(f"An error occurred: {e}")