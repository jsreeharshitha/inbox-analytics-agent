from mcp.server.fastmcp import FastMCP
from google.cloud import bigquery
import os

mcp = FastMCP("InboxAnalyticsTools")
client = bigquery.Client(project=os.getenv("PROJECT_ID", "grah-2026"))

@mcp.tool()
def query_response_metrics(contact_emails: list = None) -> str:
    """
    Queries the v_response_analytics view for response time metrics.
    Can be filtered by a list of contact emails.
    """
    query = "SELECT * FROM `mongo_sync_smart_email_manger.v_response_analytics`"
    if contact_emails:
        emails_str = ", ".join([f"'{e}'" for e in contact_emails])
        query += f" WHERE responder IN ({emails_str}) OR original_sender IN ({emails_str})"
    
    query_job = client.query(query)
    results = query_job.to_dataframe()
    return results.to_json(orient="records")

@mcp.tool()
def search_emails_by_category(category_keyword: str) -> str:
    """
    Search for emails in BigQuery based on a category or semantic keyword.
    Useful for finding 'baby product' or 'educational' emails.
    """
    query = f"""
    SELECT subject, sender, snippet, processed_at 
    FROM `mongo_sync_smart_email_manger.EmailData_Enriched`
    WHERE subject LIKE '%{category_keyword}%' OR content LIKE '%{category_keyword}%'
    LIMIT 20
    """
    query_job = client.query(query)
    results = query_job.to_dataframe()
    return results.to_json(orient="records")
