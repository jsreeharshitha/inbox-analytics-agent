from fastapi import FastAPI, Request, HTTPException
from toolbox import analyze_group_response_time, find_emails_for_unsubscribe
from tools.bq_mcp import query_response_metrics, search_emails_by_category, vector_search_emails
import os

app = FastAPI(title="Inbox Analytics Agent")

# Map of available tools for the MCP interface
TOOLS = {
    "query_response_metrics": query_response_metrics,
    "search_emails_by_category": search_emails_by_category,
    "vector_search_emails": vector_search_emails,
    "analyze_group_response_time": analyze_group_response_time,
    "find_emails_for_unsubscribe": find_emails_for_unsubscribe
}

@app.get("/mcp")
async def mcp_discovery():
    """Discovery endpoint for the MCP server."""
    return {
        "mcp_server": "InboxAnalytics",
        "status": "active",
        "available_tools": list(TOOLS.keys())
    }

@app.post("/mcp/call")
async def call_mcp_tool(request: Request):
    """
    Standard endpoint to execute an MCP tool.
    Matches the pattern used in Smart Email Manager.
    """
    try:
        body = await request.json()
        tool_name = body.get("tool")
        arguments = body.get("arguments", {})
        
        if tool_name not in TOOLS:
            raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found.")
        
        # Execute the tool or orchestrator
        result = TOOLS[tool_name](**arguments)
        return {"status": "success", "result": result}
    except Exception as e:
        print(f"Inbox-Analytics Tool Error ({tool_name}): {str(e)}")
        return {"status": "error", "message": str(e)}

@app.get("/")
async def root():
    return {"message": "Inbox Analytics Agent is active.", "status": "active"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8081))
    uvicorn.run(app, host="0.0.0.0", port=port)
