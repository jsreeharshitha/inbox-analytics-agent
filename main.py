import os
from fastapi import FastAPI, Request, HTTPException
from toolbox import generate_response_time_report, generate_tiered_recommendation_report
from tools.gmail_mcp import get_contact_list
from tools.bq_mcp import query_response_metrics, search_emails_by_category, vector_search_emails

app = FastAPI(title="Inbox Analytics Agent")

@app.get("/mcp")
async def mcp_discovery():
    """Discovery endpoint for the MCP server."""
    return {
        "mcp_server": "InboxAnalytics",
        "status": "active",
        "available_tools": [
            "get_contact_list",
            "generate_response_time_report",
            "generate_tiered_recommendation_report"
        ]
    }

@app.post("/mcp/call")
async def call_mcp_tool(request: Request):
    """
    Standardized endpoint to execute an MCP tool.
    """
    try:
        body = await request.json()
        tool_name = body.get("tool")
        arguments = body.get("arguments", {})
        
        if tool_name == "get_contact_list":
            user_email = arguments.get("user_email")
            if not user_email: raise HTTPException(400, "user_email required")
            result = get_contact_list(user_email)
            return {"status": "success", "result": result}
            
        elif tool_name == "generate_response_time_report":
            user_email = arguments.get("user_email")
            contact_emails = arguments.get("contact_emails", [])
            if not user_email or not contact_emails:
                raise HTTPException(400, "user_email and contact_emails required")
            # This is a long-running task, but for the hackathon we'll run it sync
            # or in the background if needed.
            result = generate_response_time_report(user_email, contact_emails)
            return {"status": "success", "result": result}
            
        elif tool_name == "generate_tiered_recommendation_report":
            user_email = arguments.get("user_email")
            notify_tiering = arguments.get("notify_tiering", True)
            notify_unsubscribe = arguments.get("notify_unsubscribe", True)
            similarity_threshold = float(arguments.get("similarity_threshold", 0.8))
            
            if not user_email: raise HTTPException(400, "user_email required")
            result = generate_tiered_recommendation_report(user_email, notify_tiering, notify_unsubscribe, similarity_threshold)
            return {"status": "success", "result": result}
            
        else:
            raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found.")
            
    except Exception as e:
        print(f"Inbox-Analytics Tool Error ({tool_name}): {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

@app.get("/")
async def root():
    return {"message": "Inbox Analytics Agent is active.", "status": "active"}

if __name__ == "__main__":
    import uvicorn
    # Port 8080 is standard for Cloud Run, but we can override
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
