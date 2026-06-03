from fastapi import FastAPI, Request
from toolbox import analyze_group_response_time, find_emails_for_unsubscribe
from tools.bq_mcp import query_response_metrics, search_emails_by_category

app = FastAPI(title="Inbox Analytics Agent")

TOOLS = {
    "query_response_metrics": query_response_metrics,
    "search_emails_by_category": search_emails_by_category,
    "analyze_group_response_time": analyze_group_response_time,
    "find_emails_for_unsubscribe": find_emails_for_unsubscribe
}

@app.get("/mcp")
async def mcp_discovery():
    return {
        "mcp_server": "InboxAnalytics",
        "status": "active",
        "available_tools": list(TOOLS.keys())
    }

@app.get("/")
async def root():
    return {"message": "Inbox Analytics Agent is active."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
