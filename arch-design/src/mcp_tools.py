"""
MCP Tools Integration Helper
Uses Strands' built-in MCP support.

Provides a synchronous interface for loading MCP tools into your agent.
This module handles the context management required by MCP connections.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Global context manager to keep MCP connections alive
_mcp_context = None
_mcp_context_manager = None  # Store the original ExitStack

def get_mcp_tools_sync(mcp_config: List[Dict[str, Any]]) -> List:
    """
    Get MCP tools synchronously using Strands' built-in support.
    
    This function handles the context management required by MCP connections
    and keeps them alive for the lifetime of the process.
    
    Args:
        mcp_config: List of MCP server configurations from .agent.yaml
        
    Returns:
        List of Strands-compatible tools from MCP servers
    """
    global _mcp_context, _mcp_context_manager
    
    if not mcp_config:
        return []
    
    try:
        from src.mcp_client import get_mcp_tools_with_context
        
        tools, context_manager = get_mcp_tools_with_context(mcp_config)
        
        if context_manager:
            # CRITICAL: Enter the context to keep connections alive
            # This establishes the MCP connections and keeps them open
            _mcp_context_manager = context_manager
            _mcp_context = context_manager.__enter__()
            logger.info(f"✅ Loaded {len(tools)} MCP tools and established connections")
        else:
            logger.warning("No context manager returned from get_mcp_tools_with_context")
            if not tools:
                logger.warning("No MCP tools loaded. Check your MCP server configuration.")
        
        return tools
        
    except ImportError:
        logger.info("MCP not available. Install with: pip install mcp")
        return []
    except Exception as e:
        logger.warning(f"Failed to load MCP tools: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return []

def cleanup_mcp():
    """Cleanup MCP connections."""
    global _mcp_context, _mcp_context_manager
    if _mcp_context_manager:
        try:
            # Properly exit the context manager to close connections
            _mcp_context_manager.__exit__(None, None, None)
            logger.info("MCP connections closed")
        except Exception as e:
            logger.warning(f"Error cleaning up MCP: {e}")
        _mcp_context = None
        _mcp_context_manager = None

# Register cleanup on process exit
import atexit
atexit.register(cleanup_mcp) 