import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from google.cloud import bigquery
import os
import base64
from io import BytesIO

# --- CONFIGURATION ---
PROJECT_ID = os.getenv("PROJECT_ID", "grah-2026")
DATASET_ID = "mongo_sync_smart_email_manger"
VIEW_ID = "v_response_analytics"

def generate_base64_chart(fig):
    """Utility to convert a matplotlib figure to base64."""
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def get_response_time_analytics(user_email: str, contact_emails: list):
    """
    Generates 4 graphs for Response Time Analytics:
    1. Recipient Response Time by Day
    2. Recipient Response Time by Hour
    3. My Response Time by Day
    4. My Response Time by Hour
    """
    client = bigquery.Client(project=PROJECT_ID)
    
    # Filter view by the user and the selected contacts
    contacts_str = ", ".join([f"'{e}'" for e in contact_emails])
    
    query = f"""
    SELECT * 
    FROM `{PROJECT_ID}.{DATASET_ID}.{VIEW_ID}`
    WHERE (original_sender = '{user_email}' AND responder IN ({contacts_str}))
       OR (responder = '{user_email}' AND original_sender IN ({contacts_str}))
    """
    
    df = client.query(query).to_dataframe()
    if df.empty:
        return {"status": "error", "message": "No data found for the selected contacts."}

    # Split into two dataframes: Recipient to Reply vs Me to Reply
    # Recipient to Reply: I sent the original email (original_sender = user_email)
    recipient_df = df[df['original_sender'] == user_email]
    
    # Me to Reply: Recipient sent the original email (responder = user_email)
    me_df = df[df['responder'] == user_email]

    charts = []
    sns.set_theme(style="whitegrid")

    # --- 1. Recipient Response by Day ---
    if not recipient_df.empty:
        print("[*] Generating Chart 1: Recipient Response by Day...")
        fig1, ax1 = plt.subplots(figsize=(8, 4))
        day_avg = recipient_df.groupby(['day_num', 'day_of_week'])['response_time_hours'].mean().reset_index().sort_values('day_num')
        sns.barplot(x='day_of_week', y='response_time_hours', data=day_avg, ax=ax1, palette="Blues_d")
        ax1.set_title('Recipient Response Time by Day')
        ax1.set_ylabel('Avg Hours')
        charts.append({"title": "Recipient: By Day", "image": generate_base64_chart(fig1)})
        print("[+] Chart 1 finalized.")

        # --- 2. Recipient Response by Hour ---
        print("[*] Generating Chart 2: Recipient Response by Hour...")
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        hour_avg = recipient_df.groupby('hour_of_day')['response_time_hours'].mean().reset_index().sort_values('hour_of_day')
        sns.lineplot(x='hour_of_day', y='response_time_hours', data=hour_avg, ax=ax2, marker='o', color='blue')
        ax2.set_title('Recipient Response Time by Hour')
        ax2.set_ylabel('Avg Hours')
        charts.append({"title": "Recipient: By Hour", "image": generate_base64_chart(fig2)})
        print("[+] Chart 2 finalized.")

    # --- 3. My Response by Day ---
    if not me_df.empty:
        print("[*] Generating Chart 3: My Response by Day...")
        fig3, ax3 = plt.subplots(figsize=(8, 4))
        day_avg_me = me_df.groupby(['day_num', 'day_of_week'])['response_time_hours'].mean().reset_index().sort_values('day_num')
        sns.barplot(x='day_of_week', y='response_time_hours', data=day_avg_me, ax=ax3, palette="Oranges_d")
        ax3.set_title('My Response Time by Day')
        ax3.set_ylabel('Avg Hours')
        charts.append({"title": "Me: By Day", "image": generate_base64_chart(fig3)})
        print("[+] Chart 3 finalized.")

        # --- 4. My Response by Hour ---
        print("[*] Generating Chart 4: My Response by Hour...")
        fig4, ax4 = plt.subplots(figsize=(8, 4))
        hour_avg_me = me_df.groupby('hour_of_day')['response_time_hours'].mean().reset_index().sort_values('hour_of_day')
        sns.lineplot(x='hour_of_day', y='response_time_hours', data=hour_avg_me, ax=ax4, marker='o', color='orange')
        ax4.set_title('My Response Time by Hour')
        ax4.set_ylabel('Avg Hours')
        charts.append({"title": "Me: By Hour", "image": generate_base64_chart(fig4)})
        print("[+] Chart 4 finalized.")

    print(f"[*] All {len(charts)} charts successfully generated.")
    return {
        "status": "success",
        "charts": charts,
        "metrics": {
            "recipient_avg": round(float(recipient_df['response_time_hours'].mean()), 2) if not recipient_df.empty else 0,
            "me_avg": round(float(me_df['response_time_hours'].mean()), 2) if not me_df.empty else 0
        }
    }
