"""MCP Client implementation for interacting with MCP servers and LLMs."""

import os
import sys
import json
import time
import asyncio
from loguru import logger
from contextlib import AsyncExitStack
from typing import Any, Dict, List, Optional, AsyncGenerator, Tuple, Union, cast, Callable

import litellm
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import Resource, Tool

from .exceptions import MissingConfigError
from ..config import MCPConfig, ServerConfig

# Configure the logger
logger.remove()
logger.add(sys.stderr, level="INFO")

# Default model map for LiteLLM
DEFAULT_MODEL_MAP = {
    "openai/qwen3:32b": {
        "max_tokens": 32768,
        "max_input_tokens": 32768,
        "max_output_tokens": 32768,
        "input_cost_per_token": 0.0,
        "output_cost_per_token": 0.0,
        "litellm_provider": "openai",
        "mode": "chat",
        "supports_function_calling": True,
    },
    "qwen3:32b": {
        "max_tokens": 32768,
        "max_input_tokens": 32768,
        "max_output_tokens": 32768,
        "input_cost_per_token": 0.0,
        "output_cost_per_token": 0.0,
        "litellm_provider": "openai",
        "mode": "chat",
        "supports_function_calling": True,
    }
}


class MCPClient:
    """Client for interacting with LLMs and MCP servers.
    
    This client provides a unified interface for connecting to MCP servers,
    discovering and calling tools, and processing user queries using LLMs.
    """

    # Use a separator that won't appear in server or tool names
    TOOL_NAME_SEPARATOR = "__"

    def __init__(
        self,
        config_path: Optional[str] = None,
        mcp_servers: Optional[dict] = None,
        api_key: Optional[str] = None,
        model: str = "anthropic/claude-3-7-sonnet-20241024",
        max_tokens: int = 4096,
        base_url: Optional[str] = None,
        debug: bool = False,
        model_map: Optional[dict] = None,
    ):
        """Initialize the MCP client.

        Args:
            config_path: Path to the MCP configuration file.
            api_key: API key for the LLM provider, defaults to env var based on model provider.
            model: LLM model to use (LiteLLM format with provider prefix).
            max_tokens: Maximum tokens for model completion.
            base_url: Base URL for API, e.g., "http://localhost:11434" for Ollama
            debug: Whether to enable debug logging.
            model_map: Optional custom model map for LiteLLM.
        """
        try:
            if config_path:
                self.config = MCPConfig.load_from_file(config_path)
            elif mcp_servers:
                self.config = MCPConfig.model_validate(mcp_servers)
            else:
                logger.warning("No MCP server configuration found. The client will operate without MCP servers.")
        except FileNotFoundError:
            # Create an empty config if none is found - allows using the client without MCP servers
            self.config = MCPConfig()
            logger.warning("No MCP server configuration found. The client will operate without MCP servers.")
        
        self.model = model
        self.max_tokens = max_tokens
        self.base_url = base_url

        # Setup LiteLLM configuration
        if debug:
            litellm._turn_on_debug()
        

        # Set API key based on model provider
        if base_url:
            litellm.api_base = base_url

        # Extract provider from model string
        provider = model.split('/')[0] if '/' in model else None
        env_var_name = f"{provider.upper()}_API_KEY" if provider else "LITELLM_API_KEY"

        self.api_key = api_key or os.environ.get(env_var_name) or os.environ.get("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError(f"API key is required. Set {env_var_name} env var or pass it to the constructor.")

        # Configure LiteLLM with the appropriate API key
        if provider and provider.lower() == "anthropic":
            os.environ["ANTHROPIC_API_KEY"] = self.api_key
        elif provider and provider.lower() == "openai":
            os.environ["OPENAI_API_KEY"] = self.api_key
        else:
            # For other providers or if no provider specified
            litellm.api_key = self.api_key

        # MCP server connections and state
        self.exit_stack = AsyncExitStack()
        self.sessions: Dict[str, ClientSession] = {}
        self.server_tools: Dict[str, List[Tool]] = {}
        
        # Map fully-qualified tool names to (server_name, tool_name) tuples
        self.tool_map: Dict[str, Tuple[str, str]] = {}
        
    async def connect_to_server(self, server_name: str) -> None:
        """Connect to a specific MCP server.

        Args:
            server_name: Name of the server to connect to.
            
        Raises:
            ValueError: If the server configuration is invalid.
            ConnectionError: If the connection to the server fails.
        """
        logger.info(f"Connecting to server: {server_name}")

        try:
            # Get server configuration
            server_config = self.config.get_server_config(server_name)

            server_params = StdioServerParameters(
                command=server_config.command,
                args=server_config.args,
                env=server_config.env
            )

            stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
            stdio, write_stream = stdio_transport

            session = await self.exit_stack.enter_async_context(ClientSession(stdio, write_stream))
            await session.initialize()

            # Store session
            self.sessions[server_name] = session

            # Get available tools
            response = await session.list_tools()
            self.server_tools[server_name] = response.tools

            logger.info(f"Connected to server '{server_name}' with {len(response.tools)} tools")
        except Exception as e:
            error_msg = f"Failed to connect to server '{server_name}': {str(e)}"
            logger.error(error_msg)
            raise ConnectionError(error_msg) from e

    async def connect_to_all_servers(self) -> None:
        """Connect to all configured MCP servers.
        
        Errors connecting to individual servers are logged but don't prevent connecting to other servers.
        """
        server_names = self.config.list_servers()
        connection_errors = []
        
        for server_name in server_names:
            try:
                await self.connect_to_server(server_name)
            except Exception as e:
                logger.error(f"Failed to connect to server '{server_name}': {str(e)}")
                connection_errors.append((server_name, str(e)))
        
        if connection_errors and len(connection_errors) == len(server_names):
            # All server connections failed
            error_details = "\n".join([f"- {name}: {error}" for name, error in connection_errors])
            raise ConnectionError(f"Failed to connect to all MCP servers:\n{error_details}")

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get a list of all available tools from connected servers in the format LiteLLM expects.
        
        Returns:
            List of tool definitions in OpenAI function format.
        """
        tools = []
        self.tool_map = {}  # Reset tool map

        for server_name, server_tools in self.server_tools.items():
            # Normalize server name for tool naming (replace hyphens with underscores)
            normalized_server = server_name.replace('-', '_')
            
            for tool in server_tools:
                # Create a consistent tool name with clear separator
                fq_tool_name = f"{normalized_server}{self.TOOL_NAME_SEPARATOR}{tool.name}"
                
                # Store the mapping from full qualified name to (server_name, tool_name)
                self.tool_map[fq_tool_name] = (server_name, tool.name)
                
                # Format tool for LiteLLM (follows OpenAI's format)
                tools.append({
                    "type": "function",
                    "function": {
                        "name": fq_tool_name,
                        "description": tool.description or f"Tool from {server_name}",
                        "parameters": tool.inputSchema
                    }
                })

        logger.debug(f"Registered tools: {self.tool_map}")
        return tools
        
    async def call_tool(self, full_tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool on an MCP server.

        Args:
            full_tool_name: Tool name in format "server_name__tool_name"
            arguments: Arguments to pass to the tool

        Returns:
            Tool execution result

        Raises:
            ValueError: If the tool name format is invalid or the server is not connected.
            RuntimeError: If the tool execution fails.
        """
        logger.info(f"Calling tool: {full_tool_name} with args: {arguments}")
        logger.debug(f"Available tool map: {self.tool_map}")
        
        if full_tool_name in self.tool_map:
            # Use the mapping we created in get_available_tools
            server_name, tool_name = self.tool_map[full_tool_name]
        else:
            # Fallback to parsing the name if not in our map (should be avoided)
            try:
                parts = full_tool_name.split(self.TOOL_NAME_SEPARATOR, 1)
                if len(parts) != 2:
                    raise ValueError(f"Invalid tool name format: {full_tool_name}")
                
                normalized_server, tool_name = parts
                # Convert back normalized server name to actual server name
                server_name = normalized_server.replace('_', '-')
                
                logger.warning(f"Tool {full_tool_name} not in tool map, parsed as server:{server_name}, tool:{tool_name}")
            except ValueError:
                raise ValueError(f"Invalid tool name format: {full_tool_name}. Expected 'server_name{self.TOOL_NAME_SEPARATOR}tool_name'")

        if server_name not in self.sessions:
            raise ValueError(f"Server '{server_name}' not connected. Available servers: {list(self.sessions.keys())}")

        session = self.sessions[server_name]
        logger.debug(f"Executing {tool_name} on server {server_name}")
        
        try:
            result = await session.call_tool(tool_name, arguments)
        except Exception as e:
            error_msg = f"Error executing tool {tool_name} on server {server_name}: {str(e)}"
            logger.exception(error_msg)
            raise RuntimeError(error_msg) from e

        # Convert MCP result to a dictionary for easier processing
        output: Dict[str, Any] = {}

        if hasattr(result, "content") and result.content:
            # Handle text content by checking each content item
            text_chunks = []
            for content in result.content:
                if hasattr(content, "text") and content.text:
                    text_chunks.append(content.text)
            
            if text_chunks:
                output["text"] = "\n".join(text_chunks)

        if hasattr(result, "isError") and result.isError:
            output["error"] = True

        return output
        
    async def handle_tool_call(
        self, 
        tool_name: str, 
        tool_id: str, 
        tool_args: str, 
        messages: List[Dict[str, Any]]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Handle a tool call, execute it and prepare messages for further processing.
        
        Args:
            tool_name: Name of the tool to call
            tool_id: ID of the tool call
            tool_args: String JSON arguments for the tool
            messages: Current message history
            
        Returns:
            Tuple of (result_text, updated_messages)
        """
        try:
            tool_args_dict = json.loads(tool_args)
            tool_result = await self.call_tool(tool_name, tool_args_dict)
            
            result_text = tool_result.get("text", "Tool executed successfully")
            if tool_result.get("error"):
                result_text = f"Error executing tool: {result_text}"
            
            # Add the tool call to messages
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": tool_id,
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "arguments": tool_args
                    }
                }]
            })
            
            # Add the tool result to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_id,
                "name": tool_name,
                "content": result_text
            })
            
            return result_text, messages
        except Exception as ex:
            logger.exception(f"Error calling tool: {ex}")
            error_message = f"Error executing tool {tool_name}: {str(ex)}"
            
            # Even with an error, we still need to update the messages
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": tool_id,
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "arguments": tool_args
                    }
                }]
            })
            
            messages.append({
                "role": "tool",
                "tool_call_id": tool_id,
                "name": tool_name,
                "content": error_message
            })
            
            return error_message, messages
            
    async def process_query(
        self,
        query: str,
        system_prompt: str = "You are a helpful assistant.",
        temperature: float = 0.7,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Process a query using LiteLLM and available tools.

        Args:
            query: User query to process
            system_prompt: Optional system prompt
            temperature: Temperature for model generation
            tools: Optional list of tools

        Returns:
            Final response from the model after processing all tool calls
        """
        if not tools:
            tools = self.get_available_tools()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]

        # Synchronous implementation - run until we get a final response
        return await self.complete(messages, temperature, tools)

    async def complete(self,
                 messages: list[dict],
                 temperature: float = 0.7,
                 tools: list[dict[str, Any]] | None = None):
        # We need to handle multiple turns of conversation potentially
        if not tools:
            tools = self.get_available_tools()
        while True:
            # Call LLM with current messages
            start_time = time.monotonic()
            response = litellm.completion(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=temperature,
                tools=tools,
                tool_choice="auto",
                api_base=self.base_url,
            )
            logger.info(f"Received response in {time.monotonic() - start_time:.2f}s")

            # Check if we have tool calls
            if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
                for tool_call in response.choices[0].message.tool_calls:
                    tool_args_str = tool_call.function.arguments
                    tool_id = tool_call.id

                    tool_name = tool_call.function.name
                    try:
                        # Call the tool and update messages
                        tool_args_dict = json.loads(tool_args_str)
                        # We need to run the async function in a synchronous context
                        tool_result = await self.call_tool(tool_name, tool_args_dict)

                        result_text = tool_result.get("text", "Tool executed successfully")
                        if tool_result.get("error"):
                            result_text = f"Error executing tool: {result_text}"

                        logger.debug(f"[Tool result: {result_text}]")
                    except Exception as ex:
                        logger.exception(f"Error calling tool: {ex}")
                        result_text = f"Error executing tool {tool_name}: {str(ex)}"
                        print(f"[Tool error: {result_text}]")

                    # Add the tool call to messages

                    messages.append({
                        "role": "assistant",
                        "content": "",
                        "tool_calls": [{
                            "id": tool_id,
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "arguments": tool_args_str
                            }
                        }]
                    })

                    # Add the tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_id,
                        "name": tool_name,
                        "content": result_text
                    })
            elif hasattr(response.choices[0], 'message') and hasattr(response.choices[0].message, 'content'):
                return response.choices[0].message.content

    async def aprocess_query(
        self,
        query: str,
        system_prompt: str = "You are a helpful assistant.",
        temperature: float = 0.7,
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """Process a query using LiteLLM and available tools, asynchronously.

        Args:
            query: User query to process
            system_prompt: Optional system prompt
            temperature: Temperature for model generation
            stream: Whether to stream the response

        Yields:
            Generated text chunks as they become available
        """
        # Ensure we have tools available
        all_tools = self.get_available_tools()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
        
        # Initial call to get model response or tool call
        try:
            if stream:
                async for chunk in self._process_streaming_query(messages, temperature, all_tools):
                    yield chunk
            else:
                async for chunk in self._process_non_streaming_query(messages, temperature, all_tools):
                    yield chunk
                
        except Exception as ex:
            logger.exception(f"Error in process_query: {ex}")
            yield f"\n[Error: {str(ex)}]\n"
    async def _process_streaming_query(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        tools: List[Dict[str, Any]] | None = None,
    ) -> AsyncGenerator[str, None]:
        """Process a query in streaming mode.
        
        Args:
            messages: List of messages to send to the model
            tools: List of available tools
            temperature: Temperature for model generation
            
        Yields:
            Generated text chunks as they become available
        """
        current_tool_call = None
        current_tool_args = ""
        tool_call_complete = False
        
        # Start streaming response
        response_stream = await litellm.acompletion(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=temperature,
            tools=tools,
            tool_choice="auto",
            stream=True,
            api_base=self.base_url,
        )
        
        async for chunk in response_stream:
            # Check for tool calls
            if hasattr(chunk, 'tool_calls') and chunk.tool_calls:
                # Get the current tool call
                for tool_call in chunk.tool_calls:
                    if not current_tool_call:
                        current_tool_call = {
                            "id": tool_call.id,
                            "name": tool_call.function.name,
                            "arguments": ""
                        }
                    
                    # Append the argument json chunk
                    if hasattr(tool_call.function, 'arguments'):
                        current_tool_args += tool_call.function.arguments
                    
                    # Attempt to parse complete JSON when we have a closing brace
                    if current_tool_args and '}' in current_tool_args and not tool_call_complete:
                        try:
                            # Check if we have complete, valid JSON
                            json.loads(current_tool_args)
                            tool_call_complete = True
                            
                            # We have a complete tool call, process it
                            yield f"\n[Calling tool: {current_tool_call['name']}]\n"
                            
                            # Call the tool and handle the result
                            result_text, updated_messages = await self.handle_tool_call(
                                current_tool_call['name'],
                                current_tool_call['id'],
                                current_tool_args,
                                messages
                            )
                            
                            yield f"\n[Tool result: {result_text}]\n"
                            
                            # Continue the conversation with the tool result
                            final_response = await litellm.acompletion(
                                model=self.model,
                                messages=updated_messages,
                                max_tokens=self.max_tokens,
                                temperature=temperature,
                                stream=True,
                                api_base=self.base_url,
                            )
                            
                            # Stream the final response
                            async for final_chunk in final_response:
                                delta = final_chunk.choices[0].delta
                                if hasattr(delta, 'content') and delta.content:
                                    yield delta.content
                                    
                        except json.JSONDecodeError:
                            # Not complete JSON yet, continue collecting
                            pass
            
            # Handle regular text content
            delta = chunk.choices[0].delta
            if hasattr(delta, 'content') and delta.content and not tool_call_complete:
                yield delta.content

    async def _process_non_streaming_query(
        self,
        messages: list[dict[str, Any]],
        temperature: float = 0.7,
        tools: list[dict[str, Any]] | None = None,
    ) -> AsyncGenerator[str, None]:
        """Process a query in non-streaming mode.
        
        Args:
            messages: List of messages to send to the model
            tools: List of available tools
            temperature: Temperature for model generation
            
        Yields:
            Generated text chunks
        """
        # Non-streaming mode
        response = await litellm.acompletion(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=temperature,
            tools=tools,
            tool_choice="auto",
            stream=False,
            api_base=self.base_url,
        )

        if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
            # Process tool calls
            for tool_call in response.choices[0].message.tool_calls:
                tool_args_str = tool_call.function.arguments

                tool_name = tool_call.function.name
                yield f"\n[Calling tool: {tool_name}]\n"

                # Call the tool and handle the result
                result_text, updated_messages = await self.handle_tool_call(
                    tool_name,
                    tool_call.id,
                    tool_args_str,
                    messages
                )

                yield f"\n[Tool result: {result_text}]\n"

                # Continue the conversation with the tool result
                final_response = await litellm.acompletion(
                    model=self.model,
                    messages=updated_messages,
                    max_tokens=self.max_tokens,
                    temperature=temperature,
                    stream=False,
                    api_base=self.base_url,
                )

                if hasattr(final_response.choices[0], 'message') and hasattr(final_response.choices[0].message, 'content'):
                    yield final_response.choices[0].message.content
        elif hasattr(response.choices[0], 'message') and hasattr(response.choices[0].message, 'content'):
            yield response.choices[0].message.content

    async def close(self):
        """Alias for cleanup() for compatibility."""
        await self.cleanup()
        
    async def aclose(self):
        """Alias for cleanup() for compatibility."""
        await self.cleanup()

    async def cleanup(self):
        """Clean up resources and connections."""
        await self.exit_stack.aclose()
        logger.debug("Cleaned up MCP client resources")
