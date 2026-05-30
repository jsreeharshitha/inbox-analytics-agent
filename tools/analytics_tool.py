import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from google.cloud import bigquery
import os
import base64
from io import BytesIO

# --- CONFIGURATION ---
PROJECT_ID = "grah-2026"
DATASET_ID = "mongo_sync_smart_email_manger"
TABLE_ID = "EmailData_Enriched"

def get_response_time_analytics():
    """
    Queries BigQuery to calculate average response times and returns two base64 encoded graphs.
    1. Average Response Time by Category (Semantic Label)
    2. Response Time Trend over the week
    """
    client = bigquery.Client(project=PROJECT_ID)
    
    # In a real scenario, we would join threads to find response times.
    # For this hackathon/mock data, we will simulate the calculation based on semantic scores
    # or categories found in the enriched table.
    
    query = f"""
    SELECT 
        subject,
        sender,
        processed_at,
        -- Simulating a 'response_time_hours' for the mock data
        ABS(MOD(ABS(FARM_FINGERPRINT(message_id)), 24)) as response_time_hours,
        -- Grouping by a simulated category based on subject keywords
        CASE 
            WHEN LOWER(subject) LIKE '%invoice%' THEN 'Finance'
            WHEN LOWER(subject) LIKE '%update%' THEN 'Project'
            WHEN LOWER(subject) LIKE '%meeting%' THEN 'Calendar'
            ELSE 'General'
        END as category
    FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
    LIMIT 100
    """
    
    df = client.query(query).to_dataframe()
    df['processed_at'] = pd.to_datetime(df['processed_at'])
    
    # --- GRAPH 1: Average Response Time by Category ---
    plt.figure(figsize=(10, 6))
    sns.set_theme(style="whitegrid")
    category_avg = df.groupby('category')['response_time_hours'].mean().reset_index()
    ax1 = sns.barplot(x='category', y='response_time_hours', data=category_avg, palette="viridis")
    plt.title('Average Response Time by Category (Hours)', fontsize=14)
    plt.ylabel('Hours')
    plt.xlabel('Category')
    
    # Save to base64
    buf1 = BytesIO()
    plt.savefig(buf1, format='png')
    graph1_base64 = base64.b64encode(buf1.getvalue()).decode('utf-8')
    plt.close()

    # --- GRAPH 2: Response Time Trend (Daily) ---
    plt.figure(figsize=(10, 6))
    df['date'] = df['processed_at'].dt.date
    daily_avg = df.groupby('date')['response_time_hours'].mean().reset_index()
    sns.lineplot(x='date', y='response_time_hours', data=daily_avg, marker='o', color='coral')
    plt.title('Daily Average Response Time Trend', fontsize=14)
    plt.ylabel('Avg Hours')
    plt.xlabel('Date')
    plt.xticks(rotation=45)
    
    # Save to base64
    buf2 = BytesIO()
    plt.savefig(buf2, format='png')
    graph2_base64 = base64.b64encode(buf2.getvalue()).decode('utf-8')
    plt.close()

    return {
        "status": "success",
        "charts": [
            {"title": "Response Time by Category", "image": graph1_base64},
            {"title": "Daily Trend", "image": graph2_base64}
        ],
        "summary": {
            "overall_avg": round(df['response_time_hours'].mean(), 2),
            "fastest_category": category_avg.loc[category_avg['response_time_hours'].idxmin(), 'category'],
            "slowest_category": category_avg.loc[category_avg['response_time_hours'].idxmax(), 'category']
        }
    }

if __name__ == "__main__":
    # Test execution
    try:
        results = get_response_time_analytics()
        print(f"Successfully generated {len(results['charts'])} charts.")
        print(f"Overall Average Response Time: {results['summary']['overall_avg']} hours")
    except Exception as e:
        print(f"Error: {e}")
