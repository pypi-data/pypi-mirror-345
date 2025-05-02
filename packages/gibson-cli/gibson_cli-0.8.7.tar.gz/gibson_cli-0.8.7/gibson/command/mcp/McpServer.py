import signal
import sys

import gibson.core.Colors as Colors
from gibson.command.BaseCommand import BaseCommand
from gibson.services.mcp.server import mcp


class McpServer(BaseCommand):
    def execute(self):
        if len(sys.argv) == 3 and sys.argv[2] == "run":
            # Setup signal handlers to exit the server
            signal.signal(signal.SIGTERM, lambda signo, frame: sys.exit(0))
            signal.signal(signal.SIGINT, lambda signo, frame: sys.exit(0))
            self.conversation.type("GibsonAI MCP server running...\n")
            mcp.run()
        else:
            self.usage()

    def usage(self):
        self.configuration.display_project()
        self.conversation.type(
            f"usage: {Colors.command(self.configuration.command, 'mcp', args='run', hint='run the mcp server')}\n"
        )
        self.conversation.newline()
        exit(1)
