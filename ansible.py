import os
import httpx
from mcp.server.fastmcp import FastMCP
from typing import Any

AAP_URL = os.getenv("AAP_URL")
AAP_TOKEN = os.getenv("AAP_TOKEN")
TRANSPORT = os.getenv("MCP_TRANSPORT", "stdio")  # "stdio" or "streamable-http"
HOST = os.getenv("MCP_HOST", "0.0.0.0")
PORT = int(os.getenv("MCP_PORT", "8000"))

if not AAP_TOKEN:
    raise ValueError("AAP_TOKEN is required")

HEADERS = {
    "Authorization": f"Bearer {AAP_TOKEN}",
    "Content-Type": "application/json"
}

mcp = FastMCP("ansible")

async def make_request(url: str, method: str = "GET", json: dict = None) -> Any:
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.request(method, url, headers=HEADERS, json=json)
        if response.status_code not in [200, 201]:
            return f"Error {response.status_code}: {response.text}"
        return response.json() if "application/json" in response.headers.get("Content-Type", "") else response.text

@mcp.tool()
async def list_inventories() -> Any:
    """List all inventories in AAP."""
    return await make_request(f"{AAP_URL}/inventories/")

@mcp.tool()
async def list_job_templates() -> Any:
    """List all job templates in AAP."""
    return await make_request(f"{AAP_URL}/job_templates/")

@mcp.tool()
async def list_jobs() -> Any:
    """List recent jobs in AAP."""
    return await make_request(f"{AAP_URL}/jobs/")

@mcp.tool()
async def get_job_status(job_id: int) -> Any:
    """Get status and output of a specific job."""
    return await make_request(f"{AAP_URL}/jobs/{job_id}/")

@mcp.tool()
async def launch_job(template_id: int, extra_vars: dict = None) -> Any:
    """Launch a job template by ID with optional extra variables."""
    payload = {"extra_vars": extra_vars or {}}
    return await make_request(f"{AAP_URL}/job_templates/{template_id}/launch/", "POST", payload)

@mcp.tool()
async def list_hosts() -> Any:
    """List all hosts in AAP inventory."""
    return await make_request(f"{AAP_URL}/hosts/")

if __name__ == "__main__":
    if TRANSPORT == "streamable-http":
        print(f"Starting AAP MCP server in streamable-http mode on {HOST}:{PORT}")
        mcp.run(transport="streamable-http", host=HOST, port=PORT)
    else:
        mcp.run(transport="stdio")
