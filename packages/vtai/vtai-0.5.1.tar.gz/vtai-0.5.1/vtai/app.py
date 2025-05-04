"""
VT - Main application entry point.

A multimodal AI chat application with dynamic conversation routing.
"""

import asyncio
import os
from typing import Any, Dict, List, Optional

import chainlit as cl
import dotenv
from chainlit.types import ChatProfile

# Import modules from main app
from vtai.assistants.manager import get_or_create_assistant
from vtai.utils import constants as const
from vtai.utils import llm_providers_config as conf
from vtai.utils.app_config import parse_command_line_args, setup_chainlit_config
from vtai.utils.assistant_manager import init_assistant, run_assistant
from vtai.utils.audio_processors import on_audio_chunk, on_audio_start
from vtai.utils.config import initialize_app, logger
from vtai.utils.conversation_handlers import (
    config_chat_session,
    handle_conversation,
    handle_files_attachment,
    handle_thinking_conversation,
)
from vtai.utils.error_handlers import handle_exception
from vtai.utils.file_handlers import process_files
from vtai.utils.llm_profile_builder import build_llm_profile
from vtai.utils.media_processors import handle_tts_response
from vtai.utils.safe_execution import safe_execution
from vtai.utils.settings_builder import build_settings
from vtai.utils.user_session_helper import get_setting, is_in_assistant_profile

# Initialize the application with improved client configuration
route_layer, assistant_id, openai_client, async_openai_client = initialize_app()

# App name constant
APP_NAME = const.APP_NAME


@cl.set_chat_profiles
async def build_chat_profile(_=None):
    """Define and set available chat profiles."""
    # Force shuffling of starters on each app startup
    # This ensures starter prompts are in a different order each time
    return [
        ChatProfile(
            name=profile.title,
            markdown_description=profile.description,
            starters=conf.get_shuffled_starters(use_random=True),
        )
        for profile in conf.APP_CHAT_PROFILES
    ]


@cl.on_chat_start
async def start_chat():
    """
    Initialize the chat session with settings and system message.
    """
    # Initialize default settings
    cl.user_session.set(conf.SETTINGS_CHAT_MODEL, conf.DEFAULT_MODEL)

    # Build LLM profile with direct icon path instead of using map
    build_llm_profile()

    # Settings configuration
    settings = await build_settings()

    # Configure chat session with selected model
    await config_chat_session(settings)

    if is_in_assistant_profile():
        try:
            # Initialize or get the assistant with web search capabilities
            assistant_id_result = await init_assistant(
                async_openai_client=async_openai_client, assistant_id=assistant_id
            )
            if not assistant_id_result:
                raise ValueError("Failed to initialize assistant")

            # Create a new thread for the conversation
            thread = await async_openai_client.beta.threads.create()
            cl.user_session.set("thread", thread)
            logger.info("Created new thread: %s", thread.id)
        except (
            asyncio.TimeoutError,
            ConnectionError,
            ValueError,
        ) as e:
            logger.error("Failed to create thread: %s", e)
            await handle_exception(e)
        except Exception as e:
            logger.error("Unexpected error creating thread: %s", repr(e))
            await handle_exception(e)


@cl.step(name=APP_NAME, type="run")
async def run(thread_id: str, human_query: str, file_ids: Optional[List[str]] = None):
    """
    Run the assistant with the user query and manage the response.

    Args:
        thread_id: Thread ID to interact with
        human_query: User's message
        file_ids: Optional list of file IDs to attach
    """
    await run_assistant(
        thread_id=thread_id,
        human_query=human_query,
        file_ids=file_ids,
        async_openai_client=async_openai_client,
        assistant_id=assistant_id,
        app_name=APP_NAME,
    )


@cl.on_message
async def on_message(message: cl.Message) -> None:
    """
    Handle incoming user messages and route them appropriately.

    Args:
        message: The user message object
    """
    async with safe_execution(
        operation_name="message processing",
        cancelled_message="The operation was cancelled. Please try again.",
    ):
        if is_in_assistant_profile():
            thread = cl.user_session.get("thread")
            files_ids = await process_files(message.elements, async_openai_client)
            await run(
                thread_id=thread.id, human_query=message.content, file_ids=files_ids
            )
        else:
            # Get message history
            messages = cl.user_session.get("message_history") or []

            # Check if current model is a reasoning model that benefits from <think>
            current_model = get_setting(conf.SETTINGS_CHAT_MODEL)
            is_reasoning = conf.is_reasoning_model(current_model)

            # If this is a reasoning model and <think> is not already in content, add it
            if is_reasoning and "<think>" not in message.content:
                # Clone the original message content
                original_content = message.content
                # Modify the message content to include <think> tag
                message.content = f"<think>{original_content}"
                logger.info(
                    "Automatically added <think> tag for reasoning model: %s",
                    current_model,
                )

            if message.elements and len(message.elements) > 0:
                await handle_files_attachment(message, messages, async_openai_client)
            else:
                # Check for <think> tag directly in user request
                if "<think>" in message.content.lower():
                    logger.info(
                        "Processing message with <think> tag using thinking "
                        "conversation handler"
                    )
                    await handle_thinking_conversation(message, messages, route_layer)
                else:
                    await handle_conversation(message, messages, route_layer)


@cl.on_settings_update
async def update_settings(settings: Dict[str, Any]) -> None:
    """
    Update user settings based on preferences.

    Args:
        settings: Dictionary of user settings
    """
    try:
        # Update temperature if provided
        if settings_temperature := settings.get(conf.SETTINGS_TEMPERATURE):
            cl.user_session.set(conf.SETTINGS_TEMPERATURE, settings_temperature)

        # Update top_p if provided
        if settings_top_p := settings.get(conf.SETTINGS_TOP_P):
            cl.user_session.set(conf.SETTINGS_TOP_P, settings_top_p)

        # Check if chat model was changed
        model_changed = False
        if conf.SETTINGS_CHAT_MODEL in settings:
            cl.user_session.set(
                conf.SETTINGS_CHAT_MODEL, settings.get(conf.SETTINGS_CHAT_MODEL)
            )
            model_changed = True

        # Update all other settings
        setting_keys = [
            conf.SETTINGS_IMAGE_GEN_IMAGE_STYLE,
            conf.SETTINGS_IMAGE_GEN_IMAGE_QUALITY,
            conf.SETTINGS_VISION_MODEL,
            conf.SETTINGS_USE_DYNAMIC_CONVERSATION_ROUTING,
            conf.SETTINGS_TTS_MODEL,
            conf.SETTINGS_TTS_VOICE_PRESET_MODEL,
            conf.SETTINGS_ENABLE_TTS_RESPONSE,
            conf.SETTINGS_TRIMMED_MESSAGES,
        ]

        for key in setting_keys:
            if key in settings:
                cl.user_session.set(key, settings.get(key))

        # If model was changed, rebuild the chat profiles to ensure icons are properly set
        if model_changed:
            # Rebuild LLM profiles to ensure icons are updated
            build_llm_profile()
            logger.info("Chat model changed, rebuilt profiles with icons")

        logger.info("Settings updated successfully")
    except Exception as e:
        logger.error("Error updating settings: %s", e)


@cl.action_callback("speak_chat_response_action")
async def on_speak_chat_response(action: cl.Action) -> None:
    """
    Handle TTS action triggered by the user.

    Args:
        action: The action object containing payload
    """
    try:
        await action.remove()
        value = action.payload.get("value") or ""
        await handle_tts_response(value, openai_client)
    except Exception as e:
        logger.error("Error handling TTS response: %s", e)
        await cl.Message(content="Failed to generate speech. Please try again.").send()


# Use the audio processor functions from the dedicated module
cl.on_audio_start(on_audio_start)
cl.on_audio_chunk(on_audio_chunk)


def main():
    """
    Entry point for the VT.ai application when installed via pip.
    This function is called when the 'vtai' command is executed.
    """
    # Parse command-line arguments and set up environment
    args_dict = parse_command_line_args()

    # Check for errors in command line parsing
    if "error" in args_dict:
        return

    # Extract necessary variables
    args = args_dict["args"]
    remaining_args = args_dict["remaining_args"]
    config_dir = args_dict["config_dir"]

    # Set up chainlit configuration
    setup_chainlit_config()

    # Initialize command to run
    cmd_args = []

    # Check for the chainlit run command in remaining args
    if not remaining_args or "run" not in remaining_args:
        # No run command provided, directly run the app using chainlit
        cmd = f"chainlit run {os.path.realpath(__file__)}"
    else:
        # Pass any arguments to chainlit
        cmd = f"chainlit {' '.join(remaining_args)} {os.path.realpath(__file__)}"

    print(f"Starting VT.ai: {cmd}")
    os.system(cmd)


if __name__ == "__main__":
    main()
