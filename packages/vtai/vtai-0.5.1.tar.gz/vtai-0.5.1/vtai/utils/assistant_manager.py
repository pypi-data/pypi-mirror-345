"""
Assistant management and thread handling for the VT application.

Handles initialization, thread management, and run processing for OpenAI assistants.
"""

import asyncio
import json
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Tuple

import chainlit as cl

from vtai.utils import constants as const
from vtai.utils.assistant_tools import process_thread_message, process_tool_call
from vtai.utils.config import logger
from vtai.utils.error_handlers import handle_exception


async def init_assistant(
    async_openai_client: Any, assistant_id: Optional[str] = None
) -> str:
    """
    Initialize or retrieve the OpenAI assistant with web search enabled.

    Args:
            async_openai_client: Async OpenAI client instance
            assistant_id: Optional existing assistant ID

    Returns:
            The assistant ID
    """
    import os

    from vtai.assistants.manager import get_or_create_assistant

    # Print all environment variables for debugging
    print("All environment variables:", os.environ)

    try:
        # Get or create the assistant with web search capabilities
        assistant = await get_or_create_assistant(
            client=async_openai_client,
            assistant_id=assistant_id,
            name=const.APP_NAME,
            instructions="You are a helpful assistant with web search capabilities. When information might be outdated or not in your training data, you can search the web for more current information.",
            model="gpt-4o",
        )

        logger.info(f"Successfully initialized assistant: {assistant.id}")
        return assistant.id
    except Exception as e:
        logger.error(f"Error initializing assistant: {e}")
        # Return the existing assistant_id if any
        return assistant_id if assistant_id else ""


async def create_run_instance(
    thread_id: str, assistant_id: str, async_openai_client: Any
) -> Any:
    """
    Create a run instance for the assistant.

    Args:
            thread_id: Thread ID to create run for
            assistant_id: The ID of the assistant to use
            async_openai_client: Async OpenAI client instance

    Returns:
            Run instance object
    """
    # Ensure we have a valid assistant ID
    if not assistant_id:
        logger.error("Could not create or retrieve assistant")
        raise ValueError("No assistant ID available. Please configure an assistant ID")

    # Create a run with the assistant
    logger.info(f"Creating run for thread {thread_id} with assistant {assistant_id}")
    return await async_openai_client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )


@asynccontextmanager
async def managed_run_execution(thread_id: str, run_id: str, async_openai_client: Any):
    """
    Context manager to safely handle run execution and ensure proper cleanup.

    Args:
            thread_id: Thread ID
            run_id: Run ID
            async_openai_client: Async OpenAI client instance
    """
    try:
        yield
    except asyncio.CancelledError:
        logger.warning("Run execution canceled for run %s", run_id)
        try:
            # Attempt to cancel the run if it was cancelled externally
            await async_openai_client.beta.threads.runs.cancel(
                thread_id=thread_id, run_id=run_id
            )
        except Exception as e:
            logger.error("Error cancelling run: %s", e)
        raise
    except Exception as e:
        logger.error("Error in run execution: %s", e)
        await handle_exception(e)


async def process_code_interpreter_tool(
    step_references: Dict[str, cl.Step], step: Any, tool_call: Any
) -> Dict[str, Any]:
    """
    Process code interpreter tool calls.

    Args:
            step_references: Dictionary of step references
            step: The run step
            tool_call: The tool call to process

    Returns:
            Tool output dictionary
    """
    output_value = ""
    if (
        tool_call.code_interpreter.outputs
        and len(tool_call.code_interpreter.outputs) > 0
    ):
        output_value = tool_call.code_interpreter.outputs[0]

    # Create a step for code execution
    async with cl.Step(
        name="Code Interpreter",
        type="code",
        parent_id=(
            cl.context.current_step.id
            if hasattr(cl.context, "current_step") and cl.context.current_step
            else None
        ),
    ) as code_step:
        code_step.input = tool_call.code_interpreter.input or "# Generating code"

        # Stream tokens to show activity
        await code_step.stream_token("Executing code")
        await asyncio.sleep(0.3)  # Small delay for visibility
        await code_step.stream_token(".")
        await asyncio.sleep(0.3)
        await code_step.stream_token(".")

        # Update with output when available
        if output_value:
            code_step.output = output_value
            await code_step.update()

    await process_tool_call(
        step_references=step_references,
        step=step,
        tool_call=tool_call,
        name=tool_call.type,
        input=tool_call.code_interpreter.input or "# Generating code",
        output=output_value,
        show_input="python",
    )

    return {
        "output": tool_call.code_interpreter.outputs or "",
        "tool_call_id": tool_call.id,
    }


async def process_function_tool(
    step_references: Dict[str, cl.Step], step: Any, tool_call: Any
) -> Dict[str, Any]:
    """
    Process function tool calls.

    Args:
            step_references: Dictionary of step references
            step: The run step
            tool_call: The tool call to process

    Returns:
            Tool output dictionary
    """
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)

    # Handle the web search tool specifically
    if function_name == "web_search":
        import os

        from vtai.tools.search import (
            WebSearchOptions,
            WebSearchParameters,
            WebSearchTool,
        )

        # Get API keys from environment
        openai_api_key = os.environ.get("OPENAI_API_KEY") or None
        tavily_api_key = os.environ.get("TAVILY_API_KEY") or None

        # Determine if we should use Tavily
        use_tavily = tavily_api_key is not None
        if use_tavily:
            logger.info("Using Tavily for assistant web search")

        # Initialize the web search tool with appropriate API keys
        web_search_tool = WebSearchTool(
            api_key=openai_api_key, tavily_api_key=tavily_api_key
        )

        # Extract search parameters
        query = function_args.get("query", "")
        model = function_args.get("model", "openai/gpt-4o")
        max_results = function_args.get("max_results", None)

        # Build search options if provided
        search_options = None
        if any(
            key in function_args
            for key in ["search_context_size", "include_urls", "summarize_results"]
        ):
            search_options = WebSearchOptions(
                search_context_size=function_args.get("search_context_size", "medium"),
                include_urls=function_args.get("include_urls", True),
                summarize_results=function_args.get("summarize_results", True),
            )
        else:
            # Default search options
            search_options = WebSearchOptions(
                search_context_size="medium", include_urls=True, summarize_results=True
            )

        # Create search parameters
        params = WebSearchParameters(
            query=query,
            model=model,
            max_results=max_results,
            search_options=search_options,
            use_tavily=use_tavily,
        )

        # Perform the search
        try:
            logger.info(f"Performing web search for: {query}")

            # Create a step for the web search execution
            async with cl.Step(
                name=f"Web Search: {query}",
                type="tool",
                parent_id=(
                    cl.context.current_step.id
                    if hasattr(cl.context, "current_step") and cl.context.current_step
                    else None
                ),
            ) as search_step:
                search_step.input = f"Searching for: {query}"

                # Stream tokens to show activity
                await search_step.stream_token("Searching")
                await asyncio.sleep(0.5)  # Small delay for visibility
                await search_step.stream_token(".")
                await asyncio.sleep(0.5)
                await search_step.stream_token(".")

                # Indicate if we're summarizing
                if search_options.summarize_results:
                    await search_step.stream_token("\nSummarization enabled...")

                # Execute the search
                search_result = await web_search_tool.search(params)

                # Get search status
                search_status = search_result.get("status", "unknown")

                # Check if search had an error
                if search_status == "error":
                    error_msg = search_result.get("error", "Unknown error occurred")
                    logger.error(f"Web search error: {error_msg}")

                    # Update step with error info
                    search_step.output = f"Error performing web search: {error_msg}"
                    await search_step.update()

                    await process_tool_call(
                        step_references=step_references,
                        step=step,
                        tool_call=tool_call,
                        name=function_name,
                        input=function_args,
                        output=f"Error performing web search: {error_msg}",
                        show_input="json",
                    )

                    return {
                        "output": f"Error performing web search: {error_msg}",
                        "tool_call_id": tool_call.id,
                    }

                # Process the results
                response_content = search_result.get(
                    "response", "No search results available"
                )

                # Add source information if available
                sources_text = ""
                try:
                    sources_json = search_result.get("sources_json")
                    if sources_json:
                        sources = json.loads(sources_json).get("sources", [])
                        if sources:
                            sources_text = "\n\nSources:\n"
                            for i, source in enumerate(sources, 1):
                                title = source.get("title", "Untitled")
                                url = source.get("url", "No URL")
                                sources_text += f"{i}. {title} - {url}\n"

                    # Append sources to response if available
                    if sources_text:
                        response_content = f"{response_content}\n{sources_text}"
                except Exception as e:
                    logger.error(f"Error processing sources: {e}")

                # Update step with final result
                search_step.output = f"Found information about '{query}'"
                await search_step.update()

            await process_tool_call(
                step_references=step_references,
                step=step,
                tool_call=tool_call,
                name=function_name,
                input=function_args,
                output=response_content,
                show_input="json",
            )

            return {
                "output": response_content,
                "tool_call_id": tool_call.id,
            }
        except Exception as e:
            error_msg = f"Error performing web search: {str(e)}"
            logger.error(error_msg)

            await process_tool_call(
                step_references=step_references,
                step=step,
                tool_call=tool_call,
                name=function_name,
                input=function_args,
                output=error_msg,
                show_input="json",
            )

            return {
                "output": error_msg,
                "tool_call_id": tool_call.id,
            }
    # For other tools that are temporarily disabled
    logger.warning(
        "Function tool call received but tools are disabled: %s", function_name
    )

    await process_tool_call(
        step_references=step_references,
        step=step,
        tool_call=tool_call,
        name=function_name,
        input=function_args,
        output="Function tools are temporarily disabled",
        show_input="json",
    )

    return {
        "output": "Function tools are temporarily disabled",
        "tool_call_id": tool_call.id,
    }


async def process_retrieval_tool(
    step_references: Dict[str, cl.Step], step: Any, tool_call: Any
) -> None:
    """
    Process retrieval tool calls.

    Args:
            step_references: Dictionary of step references
            step: The run step
            tool_call: The tool call to process
    """
    # Create a step for retrieval execution
    async with cl.Step(
        name="Document Retrieval",
        type="retrieval",
        parent_id=(
            cl.context.current_step.id
            if hasattr(cl.context, "current_step") and cl.context.current_step
            else None
        ),
    ) as retrieval_step:
        retrieval_step.input = "Retrieving relevant information from uploaded documents"

        # Stream tokens to show activity
        await retrieval_step.stream_token("Retrieving")
        await asyncio.sleep(0.3)  # Small delay for visibility
        await retrieval_step.stream_token(".")
        await asyncio.sleep(0.3)
        await retrieval_step.stream_token(".")

        # Update with completion indication
        retrieval_step.output = "Retrieved relevant information from documents"
        await retrieval_step.update()

    await process_tool_call(
        step_references=step_references,
        step=step,
        tool_call=tool_call,
        name=tool_call.type,
        input="Retrieving information",
        output="Retrieved information",
    )


async def process_tool_calls(
    step_details: Any, step_references: Dict[str, cl.Step], step: Any
) -> List[Dict[str, Any]]:
    """
    Process all tool calls from a step.

    Args:
            step_details: The step details object
            step_references: Dictionary of step references
            step: The run step

    Returns:
            List of tool outputs
    """
    tool_outputs = []

    if step_details.type != "tool_calls":
        return tool_outputs

    for tool_call in step_details.tool_calls:
        if isinstance(tool_call, dict):
            from vtai.utils.dict_to_object import DictToObject

            tool_call = DictToObject(tool_call)

        if tool_call.type == "code_interpreter":
            output = await process_code_interpreter_tool(
                step_references, step, tool_call
            )
            tool_outputs.append(output)
        elif tool_call.type == "retrieval":
            await process_retrieval_tool(step_references, step, tool_call)
        elif tool_call.type == "function":
            output = await process_function_tool(step_references, step, tool_call)
            tool_outputs.append(output)

    return tool_outputs


async def run_assistant(
    thread_id: str,
    human_query: str,
    file_ids: Optional[List[str]] = None,
    async_openai_client: Any = None,
    assistant_id: str = None,
    app_name: str = "Assistant",
) -> None:
    """
    Run the assistant with the user query and manage the response.

    Args:
            thread_id: Thread ID to interact with
            human_query: User's message
            file_ids: Optional list of file IDs to attach
            async_openai_client: OpenAI async client
            assistant_id: The ID of the assistant to use
            app_name: Name of the application for step naming
    """
    # Add the message to the thread
    file_ids = file_ids or []
    try:
        # Add message to thread with timeout
        await asyncio.wait_for(
            async_openai_client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=human_query,
            ),
            timeout=30.0,
        )

        # Create the run
        run_instance = await create_run_instance(
            thread_id, assistant_id, async_openai_client
        )

        message_references: Dict[str, cl.Message] = {}
        step_references: Dict[str, cl.Step] = {}
        tool_outputs = []

        # Use context manager for safer execution
        async with managed_run_execution(
            thread_id, run_instance.id, async_openai_client
        ):
            # Periodically check for updates with a timeout for each operation
            while True:
                run_instance = await asyncio.wait_for(
                    async_openai_client.beta.threads.runs.retrieve(
                        thread_id=thread_id, run_id=run_instance.id
                    ),
                    timeout=30.0,
                )

                # Fetch the run steps with timeout
                run_steps = await asyncio.wait_for(
                    async_openai_client.beta.threads.runs.steps.list(
                        thread_id=thread_id, run_id=run_instance.id, order="asc"
                    ),
                    timeout=30.0,
                )

                for step in run_steps.data:
                    # Fetch step details with timeout
                    run_step = await asyncio.wait_for(
                        async_openai_client.beta.threads.runs.steps.retrieve(
                            thread_id=thread_id, run_id=run_instance.id, step_id=step.id
                        ),
                        timeout=30.0,
                    )
                    step_details = run_step.step_details

                    # Process message creation
                    if step_details.type == "message_creation":
                        thread_message = await asyncio.wait_for(
                            async_openai_client.beta.threads.messages.retrieve(
                                message_id=step_details.message_creation.message_id,
                                thread_id=thread_id,
                            ),
                            timeout=30.0,
                        )
                        await process_thread_message(
                            message_references, thread_message, async_openai_client
                        )

                    # Process tool calls
                    tool_outputs.extend(
                        await process_tool_calls(step_details, step_references, step)
                    )

                # Submit tool outputs if required
                if (
                    run_instance.status == "requires_action"
                    and hasattr(run_instance, "required_action")
                    and run_instance.required_action is not None
                    and hasattr(run_instance.required_action, "type")
                    and run_instance.required_action.type == "submit_tool_outputs"
                    and tool_outputs
                ):
                    await asyncio.wait_for(
                        async_openai_client.beta.threads.runs.submit_tool_outputs(
                            thread_id=thread_id,
                            run_id=run_instance.id,
                            tool_outputs=tool_outputs,
                        ),
                        timeout=30.0,
                    )

                # Wait between polling to reduce API load
                await asyncio.sleep(2)

                if run_instance.status in [
                    "cancelled",
                    "failed",
                    "completed",
                    "expired",
                ]:
                    logger.info(
                        "Run %s finished with status: %s",
                        run_instance.id,
                        run_instance.status,
                    )
                    break

    except asyncio.TimeoutError:
        logger.error("Timeout occurred during run execution")
        await cl.Message(
            content="The operation timed out. Please try again with a simpler query."
        ).send()
    except Exception as e:
        logger.error("Error in run: %s", e)
        await handle_exception(e)
