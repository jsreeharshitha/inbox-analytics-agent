import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from mcp.server.fastmcp import FastMCP
from db.mongo_client import get_collection
from config import settings
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

mcp = FastMCP("InboxAnalyticsGmail")

def get_gmail_service(user_email: str):
    """Initializes the Gmail API service using stored credentials."""
    try:
        collection = get_collection("UserSessions")
        user_session = collection.find_one({"user_email": user_email})
        if not user_session or "credentials" not in user_session:
            raise Exception(f"No credentials found for {user_email}")

        creds_data = user_session["credentials"]
        creds = Credentials(
            token=creds_data.get("access_token"),
            refresh_token=creds_data.get("refresh_token"),
            token_uri=creds_data.get("token_uri"),
            client_id=creds_data.get("client_id"),
            client_secret=creds_data.get("client_secret")
        )

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            collection.update_one(
                {"user_email": user_email},
                {"$set": {
                    "credentials.access_token": creds.token,
                    "credentials.expiry": creds.expiry.isoformat() if creds.expiry else None
                }}
            )

        return build('gmail', 'v1', credentials=creds, cache_discovery=False)
    except Exception as e:
        print(f"Gmail Auth Error: {str(e)}")
        raise e

@mcp.tool()
def get_contact_list(user_email: str) -> list:
    """
    Retrieves a list of unique email addresses the user has interacted with recently.
    Used to populate the UI selection for response time analytics.
    """
    try:
        service = get_gmail_service(user_email)
        results = service.users().messages().list(userId='me', maxResults=100).execute()
        messages = results.get('messages', [])
        
        contacts = set()
        for msg in messages:
            detail = service.users().messages().get(userId='me', id=msg['id'], format='metadata', metadataHeaders=['From', 'To']).execute()
            headers = detail.get('payload', {}).get('headers', [])
            for h in headers:
                if h['name'] in ['From', 'To']:
                    val = h['value']
                    # Simple regex or split to extract email
                    if '<' in val:
                        email = val.split('<')[1].split('>')[0]
                    else:
                        email = val.strip()
                    if email != user_email:
                        contacts.add(email)
        
        return sorted(list(contacts))
    except Exception as e:
        print(f"Error fetching contacts: {str(e)}")
        return []

def send_analytics_email(user_email: str, subject: str, body_html: str, images: list = None):
    """
    Sends an email with HTML content and optional embedded images.
    """
    try:
        service = get_gmail_service(user_email)
        
        message = MIMEMultipart('related')
        message['to'] = user_email
        message['subject'] = subject
        
        msg_alternative = MIMEMultipart('alternative')
        message.attach(msg_alternative)
        
        msg_text = MIMEText(body_html, 'html')
        msg_alternative.attach(msg_text)
        
        # Attach images
        if images:
            for i, img_data in enumerate(images):
                img_binary = base64.b64decode(img_data['image'])
                msg_image = MIMEImage(img_binary)
                msg_image.add_header('Content-ID', f'<image{i}>')
                message.attach(msg_image)
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        return "Email sent successfully."
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return f"Error: {str(e)}"
