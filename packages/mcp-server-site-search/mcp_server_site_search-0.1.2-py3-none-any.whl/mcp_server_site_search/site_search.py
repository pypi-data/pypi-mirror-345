from typing import Any
import asyncio
import httpx
from urllib.parse import quote
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("CUHKSZ-Site-Search")

# Constants
SITE_SEARCH_BASE_URL = "http://gpu.betterspace.top:8089/api"
SITE_ID = "cuhksz_demo"
USER_AGENT = "CUHKSZ-Site-Search-app/1.0"

async def make_search_request(url: str) -> dict[str, Any] | None:
    """Make a request to the Site Search with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

def format_result(result: dict[str, Any]) -> str:
    """Format an result into a readable string."""
    return f"""
Title: {result.get('title', 'Unknown')}
Description: {result.get('description', 'No description available')}
Content: {result.get('content', 'Unknown')}
Reference: {result.get('url', 'No specific url reference provided')}
Time: {result.get('updated_at', 'Unknown')}
ID: {result.get('id', 'Unknown')}
"""

@mcp.tool()
async def site_search(query: str) -> str:
    """Get relative information from CUHKSZ based on query.you must tell user reference **link** and **id** so that
    user can read more about the document.

    Args:
        query: query related to CUHKSZ
    """
    page = 1
    top_k = 10
    mimetype = ""
    similarity_cutoff = 0.4
    rerank = True
    encoded_query = quote(query)
    url = f"{SITE_SEARCH_BASE_URL}/semantic-search/?q={encoded_query}&site_id={SITE_ID}&page={page}&top_k={top_k}&mimetype={mimetype}&similarity_cutoff={similarity_cutoff}&rerank={rerank}"
    data = await make_search_request(url)
    if not data or "results" not in data:
        return "Unable to fetch info or no info found."

    if not data["results"]:
        return "No active results found."

    results = [format_result(result) for result in data["results"]]
    return "\n---\n".join(results)

@mcp.tool()
async def search_document(id: str) -> str:
    """After calling site search, if user are intrest in specific part, you need find the document id then Get detailed document based on id.
    to better answer user's question.

    Args:
        id: id of the document
    """
    url = f"{SITE_SEARCH_BASE_URL}/sites/cuhksz_demo/documents/{id}/"
    data = await make_search_request(url)
    if not data or "clean_content" not in data:
        return "Unable to fetch document or no document found."
    return "\n---\n"+data["clean_content"]

async def test():
    query = input("请输入搜索关键词:")
    result = await site_search(query)
    print(result)
    id = input("请输入文档id:")
    result = await search_document(id)
    print(result)

if __name__ == "__main__":
    asyncio.run(test())