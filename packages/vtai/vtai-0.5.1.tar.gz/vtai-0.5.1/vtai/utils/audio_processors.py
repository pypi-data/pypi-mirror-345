"""
Audio processing utilities for the VT application.

Handles audio recording, transcription, and audio-based conversations.
"""

import asyncio
import audioop
import io
import os
import wave
from typing import BinaryIO, List, Optional

import chainlit as cl
import numpy as np

from vtai.utils import constants as const
from vtai.utils import llm_providers_config as conf
from vtai.utils.config import logger
from vtai.utils.media_processors import (
    SILENCE_THRESHOLD,
    SILENCE_TIMEOUT,
    handle_tts_response,
    speech_to_text,
)
from vtai.utils.user_session_helper import get_setting, get_user_session_id

APP_NAME = const.APP_NAME


async def on_audio_start() -> bool:
    """
    Initialize audio recording session when the user starts speaking.

    This function sets up the necessary state variables for tracking speech
    and silence during audio recording.

    Returns:
            True to allow audio recording
    """
    cl.user_session.set("silent_duration_ms", 0)
    cl.user_session.set("is_speaking", False)
    cl.user_session.set("audio_chunks", [])
    cl.user_session.set("voice_initiated", True)  # Mark conversation as voice-initiated
    return True


async def on_audio_chunk(chunk: cl.InputAudioChunk) -> None:
    """
    Process each audio chunk as it arrives, detecting silence for turn-taking.

    This function analyzes incoming audio chunks, measures silence duration,
    and triggers processing when the user stops speaking.

    Args:
            chunk: Audio chunk from the user
    """
    # Get audio chunks from user session
    audio_chunks = cl.user_session.get("audio_chunks")

    # If this is the first chunk, initialize timers and state
    if chunk.isStart:
        logger.info("Starting new audio recording session")
        cl.user_session.set("last_elapsed_time", chunk.elapsedTime)
        cl.user_session.set("is_speaking", True)
        cl.user_session.set("silent_duration_ms", 0)

        # Ensure audio_chunks is initialized
        if audio_chunks is None:
            audio_chunks = []
            cl.user_session.set("audio_chunks", audio_chunks)
        return

    # Safety check - ensure audio_chunks exists
    if audio_chunks is None:
        logger.warning("audio_chunks is None, reinitializing")
        audio_chunks = []
        cl.user_session.set("audio_chunks", audio_chunks)

    # Process the audio chunk
    audio_chunk = np.frombuffer(chunk.data, dtype=np.int16)
    audio_chunks.append(audio_chunk)

    # Get session variables with safety defaults
    last_elapsed_time = cl.user_session.get("last_elapsed_time")
    silent_duration_ms = cl.user_session.get("silent_duration_ms", 0)
    is_speaking = cl.user_session.get("is_speaking", True)

    # Safety check for last_elapsed_time
    if last_elapsed_time is None:
        logger.warning("last_elapsed_time is None, resetting to current time")
        last_elapsed_time = chunk.elapsedTime
        cl.user_session.set("last_elapsed_time", last_elapsed_time)
        # Skip time diff calculation for this iteration
        time_diff_ms = 0
    else:
        # Calculate the time difference between this chunk and the previous one
        time_diff_ms = chunk.elapsedTime - last_elapsed_time

    # Update the last elapsed time for the next iteration
    cl.user_session.set("last_elapsed_time", chunk.elapsedTime)

    # Compute the RMS (root mean square) energy of the audio chunk
    audio_energy = audioop.rms(
        chunk.data, 2
    )  # Assumes 16-bit audio (2 bytes per sample)

    logger.debug(
        f"Audio energy: {audio_energy}, Silent duration: {silent_duration_ms}ms"
    )

    if audio_energy < SILENCE_THRESHOLD:
        # Audio is considered silent
        silent_duration_ms += time_diff_ms
        cl.user_session.set("silent_duration_ms", silent_duration_ms)
        if silent_duration_ms >= SILENCE_TIMEOUT and is_speaking:
            logger.info(
                f"Silence detected for {silent_duration_ms}ms, processing audio"
            )
            cl.user_session.set("is_speaking", False)
            await process_audio()
    else:
        # Audio is not silent, reset silence timer and mark as speaking
        cl.user_session.set("silent_duration_ms", 0)
        if not is_speaking:
            logger.info("Speech resumed after silence")
            cl.user_session.set("is_speaking", True)


async def process_audio() -> None:
    """
    Process the complete audio recording after silence detection.

    This function concatenates the audio chunks, creates a WAV file,
    transcribes it using Whisper, and processes the transcription.

    If the conversation was initiated by voice, it will automatically
    trigger text-to-speech for the response.
    """
    # Get the audio buffer from the session
    audio_chunks = cl.user_session.get("audio_chunks")
    if not audio_chunks or len(audio_chunks) == 0:
        logger.warning("No audio chunks to process.")
        return

    logger.info(f"Processing {len(audio_chunks)} audio chunks")

    try:
        # Concatenate all chunks
        concatenated = np.concatenate(list(audio_chunks))
        logger.info(f"Concatenated audio length: {len(concatenated)} samples")

        # Create an in-memory binary stream
        wav_buffer = io.BytesIO()

        # Create WAV file with proper parameters
        with wave.open(wav_buffer, "wb") as wav_file:
            wav_file.setnchannels(1)  # mono
            wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit)
            wav_file.setframerate(24000)  # sample rate (24kHz PCM)
            wav_file.writeframes(concatenated.tobytes())
            logger.info(f"Created WAV file with {wav_file.getnframes()} frames")

        # Reset buffer position
        wav_buffer.seek(0)

        # Get frames and rate info by reopening the buffer
        with wave.open(wav_buffer, "rb") as wav_info:
            frames = wav_info.getnframes()
            rate = wav_info.getframerate()
            duration = frames / float(rate)
            logger.info(f"Audio duration: {duration:.2f} seconds")

        # Reset the buffer position again for reading
        wav_buffer.seek(0)

        # Check if audio is too short
        if duration <= 1.7:
            logger.warning(
                f"The audio is too short (duration: {duration:.2f}s), discarding."
            )
            return

        audio_buffer = wav_buffer.getvalue()
        logger.info(f"Audio buffer size: {len(audio_buffer)} bytes")

        whisper_input = ("audio.wav", audio_buffer, "audio/wav")

        # Create audio element for displaying in the UI
        input_audio_el = cl.Audio(content=audio_buffer, mime="audio/wav")

        # Show a step with loading animation for speech-to-text
        transcription = ""
        async with cl.Step(name=APP_NAME, type="tool") as step:
            # Add some visual indicator that transcription is in progress
            await step.stream_token("🎤 ")
            for _ in range(3):
                await step.stream_token(".")
                await asyncio.sleep(0.3)

            # Transcribe the audio
            logger.info("Sending audio to Whisper for transcription...")
            transcription = await speech_to_text(whisper_input)
            logger.info(f"Transcription result: '{transcription}'")

            # Update step content with completion message
            step.output = f"✓ Speech transcribed: {len(transcription)} characters"
            await step.update()

        # If transcription is empty, log and return
        if not transcription or transcription.strip() == "":
            logger.warning("Received empty transcription from Whisper")
            await cl.Message(
                content="I couldn't detect any speech in your audio. Please try speaking again."
            ).send()
            return

        # Get message history
        messages = cl.user_session.get("message_history") or []

        # Send the user message with transcription
        logger.info("Sending transcription as user message")
        await cl.Message(
            author="You",
            type="user_message",
            content=transcription,
            elements=[input_audio_el],
        ).send()

        # Add transcription to message history
        messages.append({"role": "user", "content": transcription})
        cl.user_session.set("message_history", messages)

        # Get the current conversation handler based on settings
        from vtai.utils.conversation_handlers import (
            get_response_from_messages,
            handle_conversation,
        )

        # Set a flag to capture the response for TTS
        voice_initiated = cl.user_session.get("voice_initiated", False)

        # Create a message object for processing
        temp_message = cl.Message(content=transcription)

        if voice_initiated:
            logger.info(
                "Voice-initiated conversation detected, will auto-play TTS response"
            )
            # For voice-initiated conversations, capture the response
            response_text = await get_response_from_messages(
                messages, cl.user_session.get(conf.SETTINGS_CHAT_MODEL)
            )

            # Process the transcription using the existing conversation handler
            # which will display the text response
            logger.info("Handling conversation with transcription")
            await handle_conversation(temp_message, messages, None)

            # Get the OpenAI client for TTS
            from vtai.utils.config import get_openai_client

            openai_client = get_openai_client()

            # Auto-trigger TTS if enabled in settings
            enable_tts = get_setting(conf.SETTINGS_ENABLE_TTS_RESPONSE)
            if enable_tts and response_text:
                logger.info("Auto-triggering TTS for voice-initiated conversation")

                # Show a step with loading animation for text-to-speech
                async with cl.Step(name=APP_NAME, type="tool") as step:
                    # Add some visual indicator that TTS is in progress
                    await step.stream_token("🔊 ")
                    for _ in range(3):
                        await step.stream_token(".")
                        await asyncio.sleep(0.3)

                    # Generate speech
                    await handle_tts_response(response_text, openai_client)

                    # Update step content with completion message
                    model = get_setting(conf.SETTINGS_TTS_MODEL) or "TTS model"
                    voice = (
                        get_setting(conf.SETTINGS_TTS_VOICE_PRESET_MODEL) or "default"
                    )
                    step.output = f"✓ Speech generated using {model} with {voice} voice"
                    await step.update()
            else:
                logger.info("TTS is disabled in settings or no response to speak")
        else:
            # For normal text-initiated conversations, just handle normally
            logger.info("Handling conversation with transcription (normal flow)")
            await handle_conversation(temp_message, messages, None)

        logger.info("Conversation handling complete")

    except Exception as e:
        logger.error(f"Error processing audio: {e}", exc_info=True)
        await cl.Message(content=f"Error processing your speech: {str(e)}").send()
