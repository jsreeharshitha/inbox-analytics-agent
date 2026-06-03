from tools.bq_mcp import query_response_metrics, search_emails_by_category
import json

def analyze_group_response_time(group_name: str, contact_emails: list):
    """
    Orchestrator: Fetches metrics for a group and calculates averages.
    """
    raw_data = query_response_metrics(contact_emails)
    data = json.loads(raw_data)
    
    if not data:
        return f"No response data found for group: {group_name}"
        
    # Logic for grouping and averaging would go here
    return data

def find_emails_for_unsubscribe(preferences: str):
    """
    Orchestrator: Uses preferences to search and flag emails.
    """
    # 1. Parse preferences (e.g. 'baby products')
    # 2. Search BigQuery
    results = search_emails_by_category(preferences)
    return results
