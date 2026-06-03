from tools.bq_mcp import query_response_metrics, search_emails_by_category, vector_search_emails
from tools.embedding_tool import generate_embedding
import json
import pandas as pd

# Mock User Preferences (Grounding Data)
MOCK_USER_PREFERENCES = [
    {
        "user_id": "user_12345",
        "sender_domain": "@example-vendor.com",
        "structured_rule": {
            "preferred_action": "archive",
            "target_label": "Promotions"
        },
        "llm_semantic_note": "The user typically archives emails from this vendor without reading them, unless the email subject contains the word 'Invoice' or 'Receipt'.",
        "confidence_score": 0.92,
        "last_updated": "2026-05-17T07:30:00Z"
    }
]

def analyze_group_response_time(group_name: str, contact_emails: list):
    """
    Transforms raw BigQuery metrics into structured UI data.
    Calculates Day-of-Week and Hour-of-Day averages.
    """
    raw_data = query_response_metrics(contact_emails)
    df = pd.read_json(raw_data)

    if df.empty:
        return {
            "summary": f"No data found for {group_name}",
            "metrics": {"external_avg": 0, "internal_avg": 0},
            "charts": {"by_day": [], "by_hour": []}
        }

    # Metric A: Avg Response by Day of Week
    day_avg = df.groupby(['day_num', 'day_of_week'])['response_time_hours'].mean().reset_index()
    day_avg = day_avg.sort_values('day_num')
    
    # Metric B: Avg Response by Hour
    hour_avg = df.groupby('hour_of_day')['response_time_hours'].mean().reset_index()
    hour_avg = hour_avg.sort_values('hour_of_day')

    # Metric D: Internal vs External
    external_avg = df[df['original_sender'].isin(contact_emails) == False]['response_time_hours'].mean()
    internal_avg = df[df['original_sender'].isin(contact_emails)]['response_time_hours'].mean()

    return {
        "group": group_name,
        "summary": f"Analytics for {group_name} retrieved successfully.",
        "metrics": {
            "external_responder_avg": round(float(external_avg), 2) if not pd.isna(external_avg) else 0,
            "internal_responder_avg": round(float(internal_avg), 2) if not pd.isna(internal_avg) else 0
        },
        "charts": {
            "by_day": day_avg.rename(columns={'response_time_hours': 'avg_hours'}).to_dict(orient="records"),
            "by_hour": hour_avg.rename(columns={'response_time_hours': 'avg_hours'}).to_dict(orient="records")
        }
    }

def find_emails_for_unsubscribe(preferences_note: str = None):
    """
    Orchestrator: Uses preferences and Vector Search to identify unsubscribe candidates.
    If no note provided, uses the 'llm_semantic_note' from MOCK_USER_PREFERENCES.
    """
    if not preferences_note:
        preferences_note = MOCK_USER_PREFERENCES[0]["llm_semantic_note"]
    
    # 1. Generate Embedding for the pattern described in the note
    print(f"[*] Generating embedding for pattern: {preferences_note}")
    embedding = generate_embedding(preferences_note)
    
    # 2. Perform Vector Search in BigQuery
    print("[*] Searching BigQuery for similar email patterns...")
    results_json = vector_search_emails(embedding)
    results = json.loads(results_json)
    
    return {
        "pattern_analyzed": preferences_note,
        "candidates": results,
        "summary": f"Found {len(results)} emails matching the user preference pattern semantically."
    }
