# nova-act-mcp
[![PyPI](https://img.shields.io/pypi/v/nova-act-mcp-server)](https://pypi.org/project/nova-act-mcp-server/)

**nova‑act‑mcp‑server** is a zero‑install [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) server that exposes [Amazon Nova Act](https://nova.amazon.com/act) browser‑automation tools.

## What's New in v0.2.5
- Added compatibility with NovaAct SDK 0.9+ by normalizing log directory handling
- Improved test organization with clear markers for unit, mock, smoke and e2e tests
- Moved mock HTML creation logic from production code to test helpers
- Fixed several syntax errors and incomplete code blocks
- Added SCREENSHOT_QUALITY constant for consistent compression settings

## Quick start (uvx)

Add it to your MCP client configuration:

```jsonc
{
  "mcpServers": {
    "nova-act-mcp-server": {
      "command": "uvx",
      "args": ["nova-act-mcp-server@latest"],
      "env": { "NOVA_ACT_API_KEY": "<your_api_key>" }
    }
  }
}
```

That's all you need to start controlling browsers from any MCP‑compatible client such as Claude Desktop or VS Code.

## Local development (optional)

```bash
git clone https://github.com/madtank/nova-act-mcp.git
cd nova-act-mcp
uv sync
uv run nova_mcp.py
```

## License
[MIT](LICENSE)
