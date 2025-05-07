# 🚀 AskNeedl MCP Server Setup

## For Claude Desktop
### Install `askneedl-mcp-server`:

```bash
pip install askneedl-mcp-server
```
<!-- add insruction to install package in same env as the python executable -->
**Note**: Make sure to use the python executable from the same environment where you are installing the `askneedl-mcp-server`. Steps to locate the python executable are mentioned below.

### Finding `<YOUR-PYTHON-EXECUTABLE-PATH>`:

Before running the commands below, activate the environment where you have installed the `askneedl-mcp-server` package. No need to activate the environment if you are using the system python.

**For macOS/Linux**

Open the terminal and run:
```bash
which python
```

**For Windows**

Open the command prompt and run:
```bash
where python
```


### Get your Needl API Key and UUID:

Contact Needl support(support@needl.ai) to get your API key and user UUID.

### Configure claude desktop:

Add the below code to the respective  `claude_desktop_config.json` file: (example `.config/Claude/claude_desktop_config.json` for linux):
```json
{
    "mcpServers": {
		"askneedl-mcp-server": {
			"command": <YOUR-PYTHON-EXECUTABLE-PATH>,
			"args": [
			"-m",
			"askneedl_mcp_server"
			],
			"shell": true,
			"env": {
				"NEEDL_API_KEY": <YOUR-NEEDL-API-KEY>,
				"USER_UUID": <YOUR-PUBLIC-UUID>,
				"env": "prod"
			}
		}
	}
}
```

## For local development and debugging:
### Run the server:
```bash
python -m askneedl_mcp_server
```

### Install `uv`:
- Refer this - https://docs.astral.sh/uv/getting-started/installation/

For macOS and Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

For windows:
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

(If you are facing installation errors, please refer the the uv installation guide(referenced above) for troubleshooting)