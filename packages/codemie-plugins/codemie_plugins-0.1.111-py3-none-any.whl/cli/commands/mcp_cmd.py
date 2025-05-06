"""Commands for MCP (Model Context Protocol) functionality."""
from __future__ import annotations

import asyncio
import json
import os
import tempfile
import traceback
from cli.commands.custom_command import CustomCommand
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import click
from rich.console import Console
from rich.table import Table

from cli.commands.custom_group import CustomGroup
from cli.utils import (
    load_config,
    register_for_graceful_shutdown,
)

# Import the MCP main module directly
from toolkits.mcp.main import ArgumentHandler, main_async

# Constants
CONFIG_KEY_MCP_SERVERS = "mcpServers"
SERVERS_JSON = "servers.json"
DEFAULT_TRANSPORT = "stdio"
DEFAULT_COMMAND = "-"
FILESYSTEM_SERVER = "filesystem"
ENV_ALLOWED_DIR = "ALLOWED_DIR"
ENV_FILE_PATHS = "FILE_PATHS"
ENV_TIMEOUT = "TIMEOUT"
ENV_VERBOSE = "VERBOSE"
GLOBAL_CONFIG_PATH = os.path.expanduser('~/.codemie/config.json')

# UI messages
MSG_NO_SERVERS = "[yellow]No MCP servers found in any configuration.[/]"
MSG_INVALID_JSON = "[yellow]Warning:[/] Invalid JSON in MCP server configuration file: {}"
MSG_CONFIG_ERROR = "[yellow]Warning:[/] Error reading MCP server configuration: {}"
MSG_MISSING_SERVERS = "[bold red]Error:[/] The following servers were not found in any configuration: {}"
MSG_USE_LIST_CMD = "[yellow]Use 'codemie-plugins mcp list' to see available servers[/]"
MSG_EXECUTION_ERROR = "[bold red]Error in MCP execution:[/] {}"
MSG_EXECUTION_CANCELLED = "[yellow]MCP execution was cancelled[/]"
MSG_KEYBOARD_INTERRUPT = "\n[yellow]Keyboard interrupt received, shutting down MCP servers...[/]"
MSG_EXECUTION_LOOP_ERROR = "[bold red]Error in MCP execution loop:[/] {}"
MSG_ERROR_RUNNING_MCP = "[bold red]Error running MCP:[/] {}"
MSG_SETTING_ENV_VAR = "[yellow]{} not set in environment, setting to original path[/]"
MSG_STARTING_MCP = "[bold green]Starting MCP with servers:[/] {}"

# Initialize console
console = Console()


def get_toolkit_config_path() -> Path:
    """
    Get the path to the MCP toolkit configuration file.
    
    Returns:
        Path: Path to the configuration file
    """
    root_dir = Path(__file__).parent.parent.parent
    return root_dir / "toolkits" / "mcp" / SERVERS_JSON


def load_toolkit_servers(config_path: Path) -> Dict[str, Any]:
    """
    Load MCP servers from the toolkit configuration file.
    
    Args:
        config_path: Path to the toolkit configuration file
        
    Returns:
        Dict[str, Any]: Dictionary of MCP servers from the toolkit configuration
    """
    toolkit_servers = {}
    
    if not config_path.exists():
        return toolkit_servers
        
    try:
        with open(config_path, 'r') as f:
            toolkit_config = json.load(f)
            toolkit_servers = toolkit_config.get(CONFIG_KEY_MCP_SERVERS, {})
    except json.JSONDecodeError:
        console.print(MSG_INVALID_JSON.format(config_path))
    except Exception as e:
        console.print(MSG_CONFIG_ERROR.format(str(e)))
            
    return toolkit_servers


def get_all_mcp_servers() -> Dict[str, Any]:
    """
    Get all MCP servers from both the global config.json and the toolkit's servers.json.
    
    Returns:
        Dict[str, Any]: Combined dictionary of MCP servers
    """
    # Get servers from global config
    config = load_config()
    global_servers = config.get(CONFIG_KEY_MCP_SERVERS, {})
    
    # Get servers from toolkit config file
    config_path = get_toolkit_config_path()
    toolkit_servers = load_toolkit_servers(config_path)
            
    # Combine servers (global servers override toolkit servers with the same name)
    return {**toolkit_servers, **global_servers}


def create_servers_table(toolkit_servers: Dict[str, Any], global_servers: Dict[str, Any]) -> Table:
    """
    Create a rich table displaying server information.
    
    Args:
        toolkit_servers: Dictionary of toolkit servers
        global_servers: Dictionary of global servers
        
    Returns:
        Table: Rich table with server information
    """
    table = Table(title="Available MCP Servers")
    table.add_column("Server Name", style="cyan")
    table.add_column("Transport", style="green")
    table.add_column("Command", style="blue")
    table.add_column("Source", style="yellow")
    
    # First add toolkit servers
    for server_name, server_config in toolkit_servers.items():
        transport = server_config.get("transport", DEFAULT_TRANSPORT)
        command = server_config.get("command", DEFAULT_COMMAND)
        table.add_row(server_name, transport, command, "Toolkit")
    
    # Then add global servers (which may override toolkit servers)
    for server_name, server_config in global_servers.items():
        transport = server_config.get("transport", DEFAULT_TRANSPORT)
        command = server_config.get("command", DEFAULT_COMMAND)
        # Check if this is overriding a toolkit server
        source = "Global Config" if server_name not in toolkit_servers else "Global Config (override)"
        table.add_row(server_name, transport, command, source)
    
    return table


def print_config_paths(config_path: Path) -> None:
    """
    Print the paths of configuration files.
    
    Args:
        config_path: Path to the toolkit configuration file
    """
    console.print("\n[cyan]Configurations loaded from:[/]")
    if config_path.exists():
        console.print(f"[cyan]- Toolkit: {config_path}[/]")
    console.print(f"[cyan]- Global: {GLOBAL_CONFIG_PATH}[/]")


def extract_env_vars_for_server(env_args: List[str], server_name: str) -> Set[str]:
    """
    Extract environment variable names specified for a particular server.
    
    Args:
        env_args: List of environment variable specifications
        server_name: Name of the server to extract variables for
        
    Returns:
        Set[str]: Set of environment variable names
    """
    env_vars = set()
    
    for e in env_args:
        if e.startswith(f"{server_name}="):
            var_names = e.split("=")[1].split(",")
            env_vars.update([v.upper() for v in var_names])
            
    return env_vars


def setup_filesystem_env_vars(env_args: List[str], original_dir: str) -> None:
    """
    Set up environment variables for the filesystem server if not already set.
    
    Args:
        env_args: List of environment variable specifications
        original_dir: Original working directory
    """
    env_specified_vars = extract_env_vars_for_server(env_args, FILESYSTEM_SERVER)
    
    # Check and set ALLOWED_DIR if not present
    if ENV_ALLOWED_DIR not in os.environ and ENV_ALLOWED_DIR not in env_specified_vars:
        console.print(MSG_SETTING_ENV_VAR.format(ENV_ALLOWED_DIR))
        os.environ[ENV_ALLOWED_DIR] = original_dir

    # Check and set FILE_PATHS if not present
    if ENV_FILE_PATHS not in os.environ and ENV_FILE_PATHS not in env_specified_vars:
        console.print(MSG_SETTING_ENV_VAR.format(ENV_FILE_PATHS))
        os.environ[ENV_FILE_PATHS] = original_dir


def create_combined_config(all_servers: Dict[str, Any], temp_dir_path: Path) -> Path:
    """
    Create a combined configuration file in the temporary directory.
    
    Args:
        all_servers: Dictionary of all MCP servers
        temp_dir_path: Path to the temporary directory
        
    Returns:
        Path: Path to the created configuration file
    """
    combined_config = {CONFIG_KEY_MCP_SERVERS: all_servers}
    temp_config_path = temp_dir_path / SERVERS_JSON
    
    with open(temp_config_path, 'w') as f:
        json.dump(combined_config, f, indent=2)
        
    return temp_config_path


def print_server_sources(toolkit_config_path: Path, temp_config_path: Path) -> None:
    """
    Print information about server configuration sources.
    
    Args:
        toolkit_config_path: Path to the toolkit configuration file
        temp_config_path: Path to the temporary combined configuration file
    """
    console.print("[cyan]Using servers from:[/]")
    if toolkit_config_path.exists():
        console.print(f"[cyan]- Toolkit config: {toolkit_config_path}[/]")
    console.print(f"[cyan]- Global config: {GLOBAL_CONFIG_PATH}[/]")
    console.print(f"[cyan]- Combined config: {temp_config_path}[/]")


def validate_servers(server_names: List[str], all_servers: Dict[str, Any]) -> bool:
    """
    Validate that all requested servers exist in the configuration.
    
    Args:
        server_names: List of server names to validate
        all_servers: Dictionary of all available servers
        
    Returns:
        bool: True if all servers are valid, False otherwise
    """
    missing_servers = [s for s in server_names if s not in all_servers]
    if missing_servers:
        console.print(MSG_MISSING_SERVERS.format(', '.join(missing_servers)))
        console.print(MSG_USE_LIST_CMD)
        return False
    return True


async def run_with_graceful_shutdown(
    server_names: List[str], 
    server_env_vars: Dict[str, List[str]], 
    debug: bool
) -> None:
    """
    Run the MCP client with graceful shutdown handling.
    
    Args:
        server_names: List of server names to run
        server_env_vars: Dictionary mapping server names to environment variables
        debug: Whether to print debug information
    """
    try:
        # Create a task for the main async function
        main_task = asyncio.create_task(
            main_async(server_names=server_names, server_env_vars=server_env_vars)
        )
        
        # Register it for graceful shutdown
        register_for_graceful_shutdown(main_task)
        
        # Wait for completion
        await main_task
    except asyncio.CancelledError:
        console.print(MSG_EXECUTION_CANCELLED)
    except Exception as e:
        console.print(MSG_EXECUTION_ERROR.format(str(e)))
        if debug:
            console.print(traceback.format_exc())


class MCPGroup(CustomGroup):
    def _get_command_examples(self, ctx: click.Context) -> str:

        return (
            "# List available MCP servers\n"
            "codemie-plugins mcp list\n\n"
            "# Run a single server\n"
            "codemie-plugins mcp run -s filesystem\n\n"
            "# Run multiple servers\n"
            "codemie-plugins mcp run -s filesystem,cli-mcp-server\n\n"
            "# Run with environment variables\n"
            "codemie-plugins mcp run -s filesystem -e filesystem=FILE_PATHS\n\n"
            "# Run with custom timeout\n"
            "codemie-plugins mcp run -s filesystem -t 120"
        )


@click.group(name="mcp", cls=MCPGroup)
@click.pass_context
def mcp_cmd(ctx):
    """Manage MCP (Model Context Protocol) servers and connections."""
    pass


@mcp_cmd.command(name="list", cls=CustomCommand)
@click.pass_context
def mcp_list(ctx):
    """List available MCP servers."""
    # Get all servers
    all_servers = get_all_mcp_servers()
    
    if not all_servers:
        console.print(MSG_NO_SERVERS)
        return
    
    # Get global and toolkit servers separately to show the source
    config = load_config()
    global_servers = config.get(CONFIG_KEY_MCP_SERVERS, {})
    
    config_path = get_toolkit_config_path()
    toolkit_servers = load_toolkit_servers(config_path)
    
    # Create and display the table
    table = create_servers_table(toolkit_servers, global_servers)
    console.print(table)
    
    # Show config file paths
    print_config_paths(config_path)


@mcp_cmd.command(name="run", cls=CustomCommand)
@click.option('--servers', '-s', required=True, help="Comma-separated list of server names to run")
@click.option('--env', '-e', multiple=True,
              help="Server-specific environment variables (format: 'server_name=VAR1,VAR2')")
@click.option('--timeout', '-t', help="Timeout in seconds", type=int)
@click.option('--verbose', '-v', help="Verbose mode to avoid logs truncation", is_flag=True)
@click.pass_context
def mcp_run(ctx, servers: str, env: List[str], timeout: Optional[int], verbose: Optional[bool] = False):
    """Run MCP with specified servers.

    Example: codemie-plugins mcp run -s filesystem,server2 -e filesystem=FILE_PATHS,DEFAULT_PATH
    """
    # Set timeout environment variable if provided
    if timeout:
        os.environ[ENV_TIMEOUT] = str(timeout)

    if verbose:
        console.print("[yellow]Verbose mode enabled. Logs will be displayed without truncation.[/]")
        os.environ[ENV_VERBOSE] = 'true'

    # Save original working directory
    original_dir = os.getcwd()

    # Check if filesystem is in the server list and set up environment variables
    if FILESYSTEM_SERVER in servers:
        setup_filesystem_env_vars(env, original_dir)

    try:
        # Create a temporary directory for the configs
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                temp_dir_path = Path(temp_dir)
                os.chdir(temp_dir_path)

                # Get configuration paths
                toolkit_config_path = get_toolkit_config_path()
                
                # Get all server configurations
                all_servers = get_all_mcp_servers()
                
                # Create a combined config file
                temp_config_path = create_combined_config(all_servers, temp_dir_path)

                # Print information about server sources
                print_server_sources(toolkit_config_path, temp_config_path)

                # Parse the server names
                server_names = ArgumentHandler.parse_server_names(servers)
                
                # Validate servers
                if not validate_servers(server_names, all_servers):
                    return

                # Convert env from click format to the format expected by parse_environment_variables
                env_args = [[e] for e in env]
                server_env_vars = ArgumentHandler.parse_environment_variables(env_args, server_names)

                # Print startup message
                console.print(MSG_STARTING_MCP.format(', '.join(server_names)))
                
                # Run the async function and handle keyboard interrupts
                try:
                    asyncio.run(run_with_graceful_shutdown(
                        server_names=server_names,
                        server_env_vars=server_env_vars,
                        debug=ctx.obj.get('DEBUG', False)
                    ))
                except KeyboardInterrupt:
                    console.print(MSG_KEYBOARD_INTERRUPT)
                except Exception as e:
                    console.print(MSG_EXECUTION_LOOP_ERROR.format(str(e)))
                    if ctx.obj.get('DEBUG'):
                        console.print(traceback.format_exc())

            finally:
                # Restore original working directory
                os.chdir(original_dir)

    except Exception as e:
        console.print(MSG_ERROR_RUNNING_MCP.format(str(e)))
        if ctx.obj.get('DEBUG'):
            console.print(traceback.format_exc())
