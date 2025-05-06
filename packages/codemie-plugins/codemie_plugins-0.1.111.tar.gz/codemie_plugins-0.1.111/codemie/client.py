"""Plugin client module."""
import random
import os
import asyncio
from typing import Optional, Callable

from langchain_core.messages import ToolMessage
from pydantic import BaseModel
from langchain.tools import BaseTool
from codemie.toolkit import logger
from codemie.langchain.services import ToolService

class PluginClient:
    """Plugin client class."""
    def __init__(self, tools: list[BaseTool], tool_result_converter: Optional[Callable[[ToolMessage], str]] = None, timeout: int = 60):
        """Initialize PluginClient class."""
        if not os.getenv("PLUGIN_KEY"):
            logger.error("Plugin key is required.")
            raise SystemExit
        self.timeout = timeout
        self.plugin_key = os.getenv("PLUGIN_KEY")
        self.plugin_id = str(random.randint(100000, 999999))
        self.plugin_label = os.getenv("PLUGIN_LABEL") if os.getenv("PLUGIN_LABEL") else "default"

        if not os.getenv("PLUGIN_ENGINE_URI"):
            logger.error("Plugin engine URI is required.")
            raise SystemExit
        self.pe_uri = os.getenv("PLUGIN_ENGINE_URI")

        if not tools:
            logger.error("No tools provided.")
            raise SystemExit
        self.tools = tools
        self._enrich_tools_details()

        self.tool_result_converter = tool_result_converter

        self.options = {
            "user": self.plugin_key,
            "password": self.plugin_key,
            "max_reconnect_attempts": -1,
            "connect_timeout": 10
        }

        if self.pe_uri.startswith("tls://"):
            self.options["tls_handshake_first"] = True

        self.nats_config = {
            "servers": [self.pe_uri],
            "options": self.options
        }

        # Store tool services for management
        self.tool_services = []

        if os.getenv("GIT_NEW_VERSION_CHECK"):
            os.system("$DEVBOX_PROJECT_ROOT/check_updates.sh")

    def _enrich_tools_details(self):
        """Enrich tools description with plugin information."""
        for tool in self.tools:
            if not tool.name.startswith("_"):
                tool.name = f"_{tool.name}"
            if isinstance(tool.args_schema, dict) and not tool.args_schema.get("title"):
                tool.args_schema["title"] = f"{tool.name}Args"
            if isinstance(tool.args_schema, BaseModel) and not tool.args_schema.title:
                tool.args_schema.title = f"{tool.name}Args"
            tool.description = f"""{tool.description}
            Plugin label: {self.plugin_label}
            Plugin ID: {self.plugin_id}
            """

    async def connect(self):
        """Connect to plugin engine."""
        logger.info("Connecting to plugin engine %s", self.pe_uri)

        try:
            # Run the async connect in the event loop
            await self.async_connect()
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
        except Exception as e:
            logger.error(f"Error in connect: {str(e)}")
            raise

    async def async_connect(self):
        """Asynchronously connect all tools to the plugin engine."""
        logger.info(f"Starting async connection for {len(self.tools)} tools")

        # Create a ToolService for each tool
        self.tool_services = []
        for tool in self.tools:
            prefix = f"{self.plugin_key}.{self.plugin_id}.{self.plugin_label}"
            ts = ToolService(
                nats_config=self.nats_config,
                tool=tool,
                prefix=prefix,
                timeout=self.timeout,
                tool_result_converter=self.tool_result_converter,
            )
            self.tool_services.append(ts)

        # Start all services with a small delay between them
        tasks = []
        for ts in self.tool_services:
            task = await ts.start()
            tasks.append(task)
            await asyncio.sleep(3)  # Small delay between starting each service

        logger.info(f"Started {len(tasks)} tool services")

        # Wait for all tasks to complete (they should run forever unless there's an error)
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.info("Services are being cancelled")
        except Exception as e:
            logger.error(f"Error in tools: {str(e)}")
        finally:
            # Ensure all services are properly stopped
            await self.shutdown()

    async def shutdown(self):
        """Gracefully shutdown all services."""
        logger.info("Shutting down all tool services")
        shutdown_tasks = []
        for ts in self.tool_services:
            shutdown_tasks.append(ts.stop())

        if shutdown_tasks:
            await asyncio.gather(*shutdown_tasks)
        logger.info("All tool services shut down")
