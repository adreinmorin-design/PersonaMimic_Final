import asyncio
import json

# Ensure paths correctly resolve depending on how this is launched
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

# Initialize FastMCP Server
mcp = FastMCP("PersonaMimicStudio")


@mcp.tool()
async def get_swarm_status() -> str:
    """Get the live status of all active Swarm Brains in the factory."""
    from app.swarm.service import swarm_manager

    status = await asyncio.to_thread(swarm_manager.get_status)
    # Serialize datetime objects correctly if they exist
    return json.dumps(status, default=str, indent=2)


@mcp.tool()
async def spawn_autonomous_brain(
    name: str, model: str = "qwen2.5:7b", target_niche: str = ""
) -> str:
    """
    Launch an autonomous product factory brain to hunt, strategize, build, and publish.
    """
    from app.swarm.service import swarm_manager

    brain = await asyncio.to_thread(swarm_manager.spawn, name, model, "autonomous")
    await asyncio.to_thread(brain.start, niche=target_niche)
    return f"Autonomous Level-5 Brain '{name}' launched successfully targeting '{target_niche}'."


@mcp.tool()
async def halt_brain(name: str) -> str:
    """Stop a specific brain from executing."""
    from app.swarm.service import swarm_manager

    if name in swarm_manager.brains:
        await asyncio.to_thread(swarm_manager.brains[name].stop)
        return f"Brain '{name}' halted."
    return f"Error: Brain '{name}' not found."


@mcp.tool()
async def execute_persona_tool(tool_name: str, args_json: str) -> str:
    """
    Execute any raw underlying persona tool (e.g. market_research, assemble_full_product).
    Pass args_json as a valid JSON string.
    """
    from app.swarm.tools import execute_tool

    try:
        args = json.loads(args_json)
        result = await execute_tool(tool_name, args)
        return str(result)
    except Exception as e:
        return f"Tool Execution Fault: {e}"


@mcp.tool()
async def list_inventory() -> str:
    """List all digital products currently created and stored by the factory."""
    from app.swarm.tools import list_products

    return await list_products()


if __name__ == "__main__":
    # When running as an MCP Server, we hook directly to standard IO
    mcp.run()
