# mcp_server_site_search

# Site Search MCP Server

A Model Context Protocol server that provides additional information from CUHKSZ's official websites.

> Note: This server is currently in development and may not be fully functional.
> If you encounter issues like keep wating for the mcp response, try using school network and close your VPN.

### Available Tools

- `site_search`: Get relative information from CUHKSZ based on query
  - Required arguments:
      - `query`: query related to CUHKSZ
- `search_document`: Get specific document based on id
  - Required arguments:
      - `id`: id of the document

## Installation

### Using uv (recommended)

When using [`uv`](https://docs.astral.sh/uv/) no specific installation is needed. We will
use [`uvx`](https://docs.astral.sh/uv/guides/tools/) to directly run *mcp-server-site-search*.

### Using PIP

Alternatively you can install `mcp-server-site-search` via pip:

```bash
pip install mcp-server-site-search
```

After installation, you can run it as a script using:

```bash
python -m mcp_server_site_search
```

## Configuration

Add to your settings:

<details>
<summary>Using uvx</summary>

```json
{
  "mcpServers": {
    "CUHKSZ-Site-Search": {
      "command": "uvx",
      "args": ["mcp-server-site-search"]
    }
  }
}
```
</details>

<details>
<summary>Using docker</summary>

```json
{
  "mcpServers": {
    "CUHKSZ-Site-Search": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "masonwen/mcp-cuhksz-search:latest"]
    }
  }
}
```
</details>

<details>
<summary>Using pip</summary>

```json
{
  "mcpServers": {
    "CUHKSZ-Site-Search": {
      "command": "python",
      "args": ["-m", "mcp_server_site_search"]
    }
  }
}
```
</details>