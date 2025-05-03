Run these

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirement.txt
```

Then to run the MCP Inspector and your MCP server code: 

```bash
mcp dev bus_mgmt_dolt_mcp_server/bus_mgmt_dolt_mcp_server.py
```

Or you can do this:

```bash
uv run bus_mgmt_dolt_mcp_server/bus_mgmt_dolt_mcp_server.py
```

To run the test code do this:

```bash
uv run test_client.py
```
