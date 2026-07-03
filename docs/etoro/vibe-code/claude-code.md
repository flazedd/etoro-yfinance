> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Claude Code

> Integrate the eToro Public API into Claude Code using MCP

Claude Code is an agentic coding tool that lives in your terminal. You can connect it to the **eToro Public API MCP server** so it can discover routes and execute API calls while you build.

## Configuration

### Recommended — install the skill

Easiest path. The skill handles MCP registration, auth, and the demo-vs-real safety rules. In a Claude Code session, paste:

```text theme={null}
Please install the skill at https://mcp.public-api.etoro.com/skill and follow the instructions.
```

The skill at [mcp.public-api.etoro.com/skill](https://mcp.public-api.etoro.com/skill) walks Claude Code through the exact `claude mcp add` command, authentication headers, and the rules for money-moving routes.

### Manual setup

Run the following command in your terminal to add the eToro Public API MCP server:

```bash theme={null}
claude mcp add --transport http etoro-public-api https://mcp.public-api.etoro.com
```

<Note>
  This command registers the MCP server with Claude Code, allowing it to query the live OpenAPI document and execute Public API calls during your coding sessions.
</Note>

## Verification

To confirm that the MCP server has been added successfully, run:

```bash theme={null}
claude mcp list
```

You should see `etoro-public-api` in the list of available MCP servers.

## Usage

Once configured, you can ask Claude Code questions about the eToro Public API directly from your terminal.

**Examples:**

* `claude "How do I authenticate with the eToro WebSocket API?"`
* `claude "Generate a Python script to place a market order using the eToro API"`

Claude Code will use the MCP connection's `get-all-routes` and `get-route-spec` tools to read the live OpenAPI document and provide accurate answers and code snippets.
