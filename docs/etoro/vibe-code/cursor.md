> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Cursor

> Integrate the eToro Public API into Cursor using MCP

You can connect Cursor to the **eToro Public API MCP server** so its AI can discover routes, read the live OpenAPI schema, and execute API calls while you build.

## Configuration

### Recommended — install the skill

The fastest way is to let the skill handle MCP registration, authentication, and the demo-vs-real safety rules for you. In Cursor's chat or composer, send:

```text theme={null}
Please install the skill at https://mcp.public-api.etoro.com/skill and follow the instructions.
```

The skill at [mcp.public-api.etoro.com/skill](https://mcp.public-api.etoro.com/skill) walks Cursor through the exact `mcp.json` entry, auth headers, and the rules for money-moving routes (open/close trades, transfers, etc.).

### One-click install

<a href="cursor://anysphere.cursor-deeplink/mcp/install?name=etoro-public-api&config=eyJ1cmwiOiJodHRwczovL21jcC5wdWJsaWMtYXBpLmV0b3JvLmNvbSJ9" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', backgroundColor: '#16A34A', color: 'white', padding: '12px 24px', borderRadius: '8px', textDecoration: 'none', fontWeight: '600', fontSize: '16px' }}>
  <span>Install on Cursor</span>
</a>

### Manual setup

<Steps>
  <Step title="Open Cursor Settings">
    Navigate to **Cursor Settings** > **Tools & MCP** > **Installed MCP Servers**.
  </Step>

  <Step title="Add New MCP Server">
    Click on **Add Custom MCP**. This will open the `mcp.json` configuration file.
  </Step>

  <Step title="Configure mcp.json">
    Paste the following configuration into the file:

    ```json theme={null}
    {
      "mcpServers": {
        "etoro-public-api": {
          "url": "https://mcp.public-api.etoro.com"
        }
      }
    }
    ```
  </Step>
</Steps>

## Usage

Once configured, ask Cursor anything about the eToro Public API. For example:

* "What are the parameters for placing a market order?"
* "How do I authenticate with the WebSocket API?"

Cursor will use the MCP server's `get-all-routes` and `get-route-spec` tools to read the live OpenAPI document and respond with accurate code.
