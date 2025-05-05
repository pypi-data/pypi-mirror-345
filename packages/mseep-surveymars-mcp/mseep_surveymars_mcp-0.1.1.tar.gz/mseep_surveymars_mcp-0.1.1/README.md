<div class="title-block" style="text-align: center;" align="center">

  [![SurveyMars](/assets/images/surveymars.jpg)](https://surveymars.com/)

  [![App Store](assets/images/apple-logo-transparent.png)](https://apps.apple.com/us/app/surveymars/id1301153578)
  [![Google Play](https://static.surveymars.com/static/assets/images/social-media/googleplay.png)](https://play.google.com/store/apps/details?id=com.surveypluto.app&amp;pli=1)&emsp;&emsp;
  [![Facebook](https://static.surveymars.com/static/assets/images/social-media/facebook-fill.png)](https://www.facebook.com/profile.php?id=61575183117455)
  [![Twitter](https://static.surveymars.com/static/assets/images/social-media/Twitter-fill.png)](https://x.com/surveymars)
  [![Instagram](https://static.surveymars.com/static/assets/images/social-media/instagram-fill.png)](https://www.instagram.com/surveymars_/)
  [![Youtube](https://static.surveymars.com/static/assets/images/social-media/youtube-fill.png)](https://www.youtube.com/@SurveyMars)
  
</div>

# SurveyMars MCP Server

**At <a href="https://surveymars.com">SurveyMars</a>** our mission is to make it easy for our users to gather insights quickly and effortlessly through our powerful and completely free survey platform. With unlimited surveys, questions, responses, and advanced analytics tools, you can create, distribute, and analyze surveys in minutes, without any technical expertise or budget.

**Our goal** is to help our users save time and resources, so you can focus on what matters most: using data to drive success. We are dedicated to continuously improving our platform to meet the evolving needs of our users, and to providing you with the best possible experience.

Official SurveyMars <a href="https://github.com/modelcontextprotocol">Model Context Protocol (MCP)</a> server that enables interaction with SurveyMars APIs. This server allows MCP clients like <a href="https://www.anthropic.com/claude">Claude Desktop</a>, <a href="https://www.cursor.so">Cursor</a>, <a href="https://codeium.com/windsurf">Windsurf</a>, <a href="https://github.com/openai/openai-agents-python">OpenAI Agents</a> and others to create, distribute, and analyze surveys.

## Components

### Tools

- survey_create: Create survey with [SurveyMars](https://surveymars.com) 

## Quickstart with Claude Desktop

1. Login to your SurveyMars account from [SurveyMars Login](https://surveymars.com/app/login)
2. Get your `Account ID` and `Secret Key` from [SurveyMars Account Summary](https://surveymars.com/app/usercenter). 
3. Install `uv` (Python package manager), install with `curl -LsSf https://astral.sh/uv/install.sh | sh` or see the `uv` [repo](https://github.com/astral-sh/uv) for additional install methods.
4. Go to Claude > Settings > Developer > Edit Config > claude_desktop_config.json to include the following:

```
{
  "mcpServers": {
    "surveymars-mcp": {
      "command": "uvx",
      "args": [
        "surveymars-mcp",
        "--account-id=your-account-id",
        "--secret-key=your-secret-key"
      ]
    }
  }
}

```

If you're using Windows, you will have to enable "Developer Mode" in Claude Desktop to use the MCP server. Click "Help" in the hamburger menu at the top left and select "Enable Developer Mode".

## Example usage

Try asking Claude:

- "Help me create a questionnaire for a hotel satisfaction survey"
- "Create a vehicle purchase journey survey to gather valuable insights from customers at every stage of their journey, from their initial research and showroom visit, to their final purchase decision and post-sale satisfaction."

## Development

### Building and Publishing

To prepare the package for distribution:

1. Sync dependencies and update lockfile:
```bash
uv sync
```

2. Build package distributions:
```bash
uv build
```

This will create source and wheel distributions in the `dist/` directory.

3. Publish to PyPI:
```bash
uv publish
```

Note: You'll need to set PyPI credentials via environment variables or command flags:
- Token: `--token` or `UV_PUBLISH_TOKEN`
- Or username/password: `--username`/`UV_PUBLISH_USERNAME` and `--password`/`UV_PUBLISH_PASSWORD`
