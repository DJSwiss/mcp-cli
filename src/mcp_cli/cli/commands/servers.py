# src/mcp_cli/cli/commands/servers.py
"""
CLI binding for “servers list”.
"""
from __future__ import annotations

import logging
from typing import Any

import typer

# shared helpers
from mcp_cli.commands.servers import servers_action, servers_action_async
from mcp_cli.tools.manager import get_tool_manager
from mcp_cli.cli.commands.base import BaseCommand

logger = logging.getLogger(__name__)

# ─── Typer sub-app ───────────────────────────────────────────────────────────
app = typer.Typer(help="List connected MCP servers")


@app.command("run")
def servers_run() -> None:
    """
    Show connected servers with status & tool counts (blocking CLI mode).
    """
    tm = get_tool_manager()
    if tm is None:
        typer.echo("Error: no ToolManager initialised", err=True)
        raise typer.Exit(code=1)

    servers_action(tm)
    raise typer.Exit(code=0)


# ─── In-process command for CommandRegistry ─────────────────────────────────
class ServersListCommand(BaseCommand):
    """`servers list` command usable from interactive shell or scripts."""

    def __init__(self) -> None:
        super().__init__(
            name="servers list",
            help_text="Show all connected servers with their status and tool counts.",
        )

    async def execute(self, tool_manager: Any, **_: Any) -> None:
        """
        Delegates to the shared *async* helper.
        """
        logger.debug("Executing ServersListCommand")
        await servers_action_async(tool_manager)
