import os
from fastapi import FastAPI, Request, HTTPException
from tools.analytics_tool import get_response_time_analytics
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Inbox Analytics Agent API")

@app.get("/mcp")
async def mcp_discovery():
    return {
        "mcp_server": "InboxAnalytics",
        "status": "active",
        "available_tools": ["get_response_time_analytics"]
    }

@app.post("/mcp/call")
async def call_mcp_tool(request: Request):
    try:
        body = await request.json()
        tool_name = body.get("tool")
        
        if tool_name == "get_response_time_analytics":
            result = get_response_time_analytics()
            return {"status": "success", "result": result}
        else:
            raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found.")
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
async def root():
    return {
        "message": "Inbox Analytics Agent is running.",
        "mode": "Analytical (BigQuery Engine)",
        "status": "active"
    }

if __name__ == "__main__":
    import uvicorn
    # Port 8081 to avoid conflict with Smart Email Manager
    port = int(os.environ.get("PORT", 8081))
    uvicorn.run(app, host="0.0.0.0", port=port)
