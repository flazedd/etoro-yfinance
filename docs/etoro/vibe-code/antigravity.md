> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Antigravity

> Integrate the eToro Public API into Antigravity IDE

Antigravity is an agent-first IDE designed for autonomous execution and vibe coding. You can connect its agents to the **eToro Public API MCP server** so they can discover routes and execute API calls.

## Configuration

### Recommended — install the skill

The skill handles MCP registration, auth, and the demo-vs-real safety rules. In Antigravity, ask the agent:

```text theme={null}
Please install the skill at https://mcp.public-api.etoro.com/skill and follow the instructions.
```

The skill at [mcp.public-api.etoro.com/skill](https://mcp.public-api.etoro.com/skill) walks Antigravity through the exact `mcp_config.json` entry, authentication, and the rules for money-moving routes.

### Manual setup

<Steps>
  <Step title="Locate MCP Configuration">
    Navigate to your home directory and find the `.antigravity` folder. Look for (or create) the `mcp_config.json` file.
  </Step>

  <Step title="Configure mcp_config.json">
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

  <Step title="Restart Antigravity">
    Restart the IDE to apply the changes.
  </Step>
</Steps>

## Usage

Once configured, you can issue natural language commands to your agents involving the eToro Public API.

**Examples:**

* "Create a Python script that connects to the eToro WebSocket API using the authentication method described in the docs."
* "Explain the JSON structure for a market order from the eToro API reference."

The agents will use the MCP server's `get-all-routes` and `get-route-spec` tools to read the live OpenAPI document and implement the requested features.
