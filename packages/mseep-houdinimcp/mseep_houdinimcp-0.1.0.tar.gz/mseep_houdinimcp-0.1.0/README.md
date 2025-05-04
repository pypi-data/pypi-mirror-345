# HoudiniMCP – Connect Houdini to Claude Desktop or Cursor via Model Context Protocol

**HoudiniMCP** allows you to control **SideFX Houdini** from **Claude Desktop** or **Cursor** using the **Model Context Protocol (MCP)**. It consists of:

1. A **Houdini plugin** (Python package) that listens on a local port (default `localhost:9876`) and handles commands (creating and modifying nodes, executing code, etc.).  
2. An **MCP bridge script** you run via **uv** (or system Python) that communicates via **std**in/**std**out with Claude and **TCP** with Houdini.

Below are the complete instructions for setting up Houdini, uv, Claude Desktop and Cursor.

---

## Table of Contents

1. [Requirements](#requirements)
2. [Houdini MCP Plugin Installation](#houdini-mcp-plugin-installation)
   1. [Folder Layout](#folder-layout)
   2. [Shelf Tool](#shelf-tool)
   3. [Packages Integration](#packages-integration)
   4. [Using uv on Windows](#using-uv-on-windows)
   5. [Telling Claude for Desktop to Use Your Script](#telling-claude-for-desktop-to-use-your-script)
   6. [Use Cursor](#use-cursor)
3. [OPUS Integration](#opus-integration)
4. [Acknowledgement](#acknowledgement)
---

## Requirements

- **SideFX Houdini**  
- **uv** 
- **Claude Desktop** (latest version)

---

## Houdini MCP Plugin Installation

### Folder Layout

Create a folder in your Houdini scripts directory:
C:/Users/YourUserName/Documents/houdini19.5/scripts/python/houdinimcp/

Inside **`houdinimcp/`**, place:

- **`__init__.py`** – handles plugin initialization (start/stop server)  
- **`server.py`** – defines the `HoudiniMCPServer` (listening on port `9876`)  
- **`houdini_mcp_server.py`** – optional bridging script (some prefer a separate location)
- **`pyproject.toml`**


*(If you prefer, `houdini_mcp_server.py` can live elsewhere. As long as you know its path for running with `uv`.)*

### Shelf Tool

create a **Shelf Tool** to toggle the server in Houdini:

1. **Right-click** a shelf → **"New Shelf..."** 

Name it "MCP" or something similar



2. **Right-click** again → **"New Tool..."** 
Name: "Toggle MCP Server"
Label: "MCP"

3. Under **Script**, insert something like:

```python
   import hou
   import houdinimcp

   if hasattr(hou.session, "houdinimcp_server") and hou.session.houdinimcp_server:
       houdinimcp.stop_server()
       hou.ui.displayMessage("Houdini MCP Server stopped")
   else:
       houdinimcp.start_server()
       hou.ui.displayMessage("Houdini MCP Server started on localhost:9876")

```


### Packages Integration

If you want Houdini to auto-load your plugin at startup, create a package file named houdinimcp.json in the Houdini packages folder (e.g. C:/Users/YourUserName/Documents/houdini19.5/packages/):
```json
{
  "path": "$HOME/houdini19.5/scripts/python/houdinimcp",
  "load_package_once": true,
  "version": "0.1",
  "env": [
    {
      "PYTHONPATH": "$PYTHONPATH;$HOME/houdini19.5/scripts/python"
    }
  ]
}
```

### Using uv on Windows
```powershell
  # 1) Install uv 
  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

  # 2) add uv to your PATH (depends on the user instructions) from cmd
  set Path=C:\Users\<YourUserName>\.local\bin;%Path%

  # 3) In a uv project or the plugin directory
  cd C:/Users/<YourUserName>/Documents/houdini19.5/scripts/python/houdinimcp/
  uv add "mcp[cli]"

  # 4) Verify
  uv run python -c "import mcp.server.fastmcp; print('MCP is installed!')"
```
### Telling Claude for Desktop to Use Your Script
Go to File > Settings > Developer > Edit Config > 
Open or create:
claude_desktop_config.json

Add an entry:

```json
{
  "mcpServers": {
    "houdini": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "C:/Users/<YourUserName>/Documents/houdini19.5/scripts/python/houdinimcp/houdini_mcp_server.py"
      ]
    }
  }
}
```
if uv run was successful and claude failed to load mcp, make sure claude is using the same python version, use:
```cmd
  python -c "import sys; print(sys.executable)"
``` 
to find python, and replace "python" with the path you got. 

### Use Cursor
Go to Settings > MCP > add new MCP server
add the same entry in claude_desktop_config.json
you might need to stop claude and restart houdini and the server

### OPUS Integration

OPUS is a Houdini-based platform that offers a comprehensive collection of procedural assets, specializing in furniture and environmental elements. It streamlines the entire process of parameter adjustments, allowing you to either set the parameters of interest or leave them entirely to the AI. When no parameters are set, the AI takes over and adjusts them in a controlled randomization way, ensuring flexibility while maintaining the desired outcome.

This API enables developers and creators to generate and customize these assets programmatically, making it ideal for applications such as virtual environments, gaming, architectural visualization, and more.

By integrating OPUS through RapidAPI, you can access a wide range of assets that can be tailored to suit your project’s specific requirements. This integration provides enhanced realism, flexibility, and customization within your digital environments.

#### Steps to enable OPUS

1. **Create an Account**: Sign up at [RapidAPI](https://rapidapi.com/).
2. **Subscribe to OPUS API**: Go to [OPUS API Subscription](https://rapidapi.com/genel-gi78OM1rB/api/opus5/pricing) and subscribe.
3. **Get Your RapidAPI Key**: After subscribing, obtain your RapidAPI key from [OPUS API](https://rapidapi.com/genel-gi78OM1rB/api/opus5).
4. **Update `urls.env`**: Add your RapidAPI key to the `urls.env` file.

For a visual guide, check out [this short YouTube video](https://youtu.be/-JgJwL6ZHIo) that demonstrates the possibilities with OPUS integration.


### Acknowledgement

Houdini-MCP was built following [blender-mcp](https://github.com/ahujasid/blender-mcp). We thank them for the contribution.
