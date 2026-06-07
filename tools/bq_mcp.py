from mcp.server.fastmcp import FastMCP
from google.cloud import bigquery
import os
import json

mcp = FastMCP("InboxAnalyticsTools")
client = bigquery.Client(project=os.getenv("PROJECT_ID", "grah-2026"))

@mcp.tool()
def query_response_metrics(contact_emails: list = None) -> str:
    """
    Queries the v_response_analytics view for response time metrics.
    Can be filtered by a list of contact emails.
    """
    from config import settings
    # For now, we still use the view for response time metrics
    query = f"SELECT * FROM `{settings.PROJECT_ID}.mongo_sync_smart_email_manger.v_response_analytics`"
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
    """
    from config import settings
    query = f"""
    SELECT subject, sender, snippet, processed_at 
    FROM `{settings.PROJECT_ID}.{settings.DATASET_ID}.{settings.TABLE_ID}`
    WHERE subject LIKE '%{category_keyword}%' OR content LIKE '%{category_keyword}%'
    LIMIT 20
    """
    query_job = client.query(query)
    results = query_job.to_dataframe()
    return results.to_json(orient="records")

@mcp.tool()
def vector_search_emails(embedding: list, keywords: list = None) -> str:
    """
    Performs a Hybrid Vector Search in BigQuery using cosine similarity + Keyword Boosting.
    """
    from config import settings
    embedding_str = str(embedding)
    
    # Construct Keyword Match logic if provided
    keyword_clause = "0.0"
    if keywords:
        likes = [f"LOWER(e.subject) LIKE '%{k.lower()}%' OR LOWER(e.content) LIKE '%{k.lower()}%'" for k in keywords]
        keyword_clause = f"CASE WHEN ({' OR '.join(likes)}) THEN 0.20 ELSE 0.0 END"

    query = f"""
    WITH target AS (
      SELECT {embedding_str} as target_vec
    ),
    similarities AS (
      SELECT 
        e.subject, e.sender, e.content as snippet, e.processed_at,
        -- AI Similarity
        (
          SELECT SUM(a*b) 
          FROM UNNEST(e.ml_generate_embedding_result) a WITH OFFSET i 
          JOIN UNNEST(t.target_vec) b WITH OFFSET j ON i = j
        ) / (
          (SELECT SQRT(SUM(pow(a, 2))) FROM UNNEST(e.ml_generate_embedding_result) a) * 
          (SELECT SQRT(SUM(pow(b, 2))) FROM UNNEST(t.target_vec) b)
        ) as ai_similarity,
        -- Keyword Boost
        {keyword_clause} as keyword_boost
      FROM `{settings.PROJECT_ID}.{settings.DATASET_ID}.{settings.TABLE_ID}` e, target t
    )
    SELECT *, (ai_similarity + keyword_boost) as similarity 
    FROM similarities 
    WHERE (ai_similarity + keyword_boost) IS NOT NULL
    ORDER BY similarity DESC
    LIMIT 10
    """
    
    query_job = client.query(query)
    results = query_job.to_dataframe()
    return results.to_json(orient="records")
