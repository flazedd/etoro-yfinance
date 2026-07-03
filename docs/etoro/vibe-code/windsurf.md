> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Windsurf

> Integrate the eToro Public API into Windsurf IDE

Windsurf is an AI-powered IDE by Codeium that allows for "flow" state coding. You can connect the Cascade assistant to the **eToro Public API MCP server** so it can discover routes and execute API calls.

## Configuration

### Recommended — install the skill

The skill handles MCP registration, auth, and the demo-vs-real safety rules. Ask Cascade:

```text theme={null}
Please install the skill at https://mcp.public-api.etoro.com/skill and follow the instructions.
```

The skill at [mcp.public-api.etoro.com/skill](https://mcp.public-api.etoro.com/skill) walks Cascade through the exact `mcp_config.json` entry, authentication, and the rules for money-moving routes.

### Manual setup

<Steps>
  <Step title="Locate MCP Configuration">
    Navigate to your home directory and find the `.windsurf` folder. Look for (or create) the `mcp_config.json` file.
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

  <Step title="Restart Windsurf">
    Restart the IDE to apply the changes.
  </Step>
</Steps>

## Usage

You can reference the documentation in your conversation with Cascade.

**Example queries:**

* "How do I subscribe to real-time quotes using the eToro WebSocket?"
* "@eToro Docs What are the rate limits for the REST API?"

Cascade will use the MCP server's `get-all-routes` and `get-route-spec` tools to read the live OpenAPI document and help generate code.
