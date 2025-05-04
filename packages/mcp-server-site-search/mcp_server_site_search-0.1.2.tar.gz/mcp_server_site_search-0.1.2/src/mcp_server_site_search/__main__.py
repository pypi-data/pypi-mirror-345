from .site_search import mcp

def main():
    print("Starting Site Search MCP server...")
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()