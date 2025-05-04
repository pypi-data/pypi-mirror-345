"""
File and application configuration utilities for the VT application.

Handles file operations, configuration setup, and application initialization.
"""

import os
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

from vtai.utils.config import logger


def copy_if_newer(src: Path, dst: Path, log_msg: str = None) -> bool:
    """
    Copy a file only if the source is newer than the destination or if destination doesn't exist.

    Args:
            src: Source file path
            dst: Destination file path
            log_msg: Optional message to log if copy occurs

    Returns:
            bool: True if file was copied, False otherwise
    """
    if not dst.exists() or src.stat().st_mtime > dst.stat().st_mtime:
        shutil.copy2(src, dst)
        if log_msg:
            logger.info(f"{log_msg} to {dst}")
        return True
    return False


def create_symlink_or_empty_file(src: Path, dst: Path, is_dir: bool = False) -> None:
    """
    Creates a symlink if possible, otherwise creates an empty directory or file.

    Args:
            src: Source path to link to
            dst: Destination path for the symlink
            is_dir: Whether the source is a directory
    """
    if dst.exists():
        if dst.is_symlink():
            # Already a symlink, no action needed
            return
        elif is_dir:
            # It's a regular directory, rename it as backup
            backup_dir = dst.parent / f"{dst.name}.backup"
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            dst.rename(backup_dir)

    # Create the symlink
    os.symlink(str(src), str(dst))
    logger.info(f"Created symlink from {dst} to {src}")


def setup_chainlit_config() -> Path:
    """
    Sets up a centralized Chainlit configuration directory and creates necessary files.

    Returns:
            Path: Path to the centralized chainlit config directory
    """
    # Get the package installation directory
    pkg_dir = Path(__file__).parent.parent.parent
    src_chainlit_dir = pkg_dir / ".chainlit"

    # Create centralized Chainlit config directory
    user_config_dir = Path(os.path.expanduser("~/.config/vtai"))
    chainlit_config_dir = user_config_dir / ".chainlit"

    # Create directories
    user_config_dir.mkdir(parents=True, exist_ok=True)
    chainlit_config_dir.mkdir(parents=True, exist_ok=True)

    # Handle configuration files
    if src_chainlit_dir.exists() and src_chainlit_dir.is_dir():
        # Copy config.toml if needed
        copy_if_newer(
            src=src_chainlit_dir / "config.toml",
            dst=chainlit_config_dir / "config.toml",
            log_msg="Copied default config.toml",
        )

        # Handle translations directory
        src_translations = src_chainlit_dir / "translations"
        dst_translations = chainlit_config_dir / "translations"

        if src_translations.exists() and src_translations.is_dir():
            dst_translations.mkdir(exist_ok=True)

            # Copy translation files
            for trans_file in src_translations.glob("*.json"):
                copy_if_newer(
                    src=trans_file,
                    dst=dst_translations / trans_file.name,
                    log_msg=None,  # Don't log individual translation files
                )

            logger.info(f"Copied translations to {dst_translations}")

    # Handle chainlit.md
    src_md = pkg_dir / "chainlit.md"
    central_md = user_config_dir / "chainlit.md"

    if src_md.exists() and src_md.stat().st_size > 0:
        copy_if_newer(src=src_md, dst=central_md, log_msg="Copied custom chainlit.md")
    elif not central_md.exists():
        # Create empty file
        central_md.touch()
        logger.info(f"Created empty chainlit.md at {central_md}")

    # Create symlinks if not in project directory
    current_dir = Path.cwd()
    local_chainlit_dir = current_dir / ".chainlit"
    local_md = current_dir / "chainlit.md"

    if str(current_dir) != str(pkg_dir.parent):
        try:
            # Handle .chainlit directory symlink
            create_symlink_or_empty_file(
                src=chainlit_config_dir, dst=local_chainlit_dir, is_dir=True
            )

            # Handle chainlit.md file - create empty file to prevent Chainlit defaults
            if not local_md.exists():
                local_md.touch()
                logger.info(f"Created empty chainlit.md to prevent default content")

        except Exception as e:
            # Fallback if symlink creation fails
            logger.warning(f"Could not create symlinks: {e}. Using local files.")
            local_chainlit_dir.mkdir(exist_ok=True)

            if not local_md.exists():
                try:
                    local_md.touch()
                    logger.info(f"Created empty chainlit.md as fallback")
                except Exception as create_error:
                    logger.warning(
                        f"Failed to create empty chainlit.md: {create_error}"
                    )

    return chainlit_config_dir


def parse_command_line_args() -> Dict[str, Any]:
    """
    Parse command-line arguments for the application.

    Returns:
            Dictionary of parsed arguments
    """
    import argparse

    import dotenv

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="VT.ai Application")
    parser.add_argument(
        "--model",
        type=str,
        help="Model to use (e.g., deepseek, sonnet, o3-mini)",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="API key in the format provider=key (e.g., openai=sk-..., anthropic=sk-...)",
    )

    # Parse known args to handle chainlit's own arguments
    args, remaining_args = parser.parse_known_args()

    # Create user config directory
    config_dir = Path(os.path.expanduser("~/.config/vtai"))
    config_dir.mkdir(parents=True, exist_ok=True)

    # Set Chainlit's config path before any imports, using environment variables
    # that Chainlit recognizes for its paths
    os.environ["CHAINLIT_CONFIG_DIR"] = str(config_dir)
    os.environ["CHAINLIT_HOME"] = str(config_dir)

    # Process API key if provided
    env_path = config_dir / ".env"

    if args.api_key:
        try:
            # Parse provider=key format
            if "=" in args.api_key:
                provider, key = args.api_key.split("=", 1)

                # Map provider to appropriate environment variable name
                provider_map = {
                    "openai": "OPENAI_API_KEY",
                    "anthropic": "ANTHROPIC_API_KEY",
                    "deepseek": "DEEPSEEK_API_KEY",
                    "cohere": "COHERE_API_KEY",
                    "huggingface": "HUGGINGFACE_API_KEY",
                    "groq": "GROQ_API_KEY",
                    "openrouter": "OPENROUTER_API_KEY",
                    "gemini": "GEMINI_API_KEY",
                    "mistral": "MISTRAL_API_KEY",
                    "tavily": "TAVILY_API_KEY",
                    "lmstudio": "LM_STUDIO_API_KEY",
                }

                env_var = provider_map.get(provider.lower())
                if env_var:
                    # Create or update .env file with the API key
                    dotenv.set_key(env_path, env_var, key)
                    print(f"API key for {provider} saved to {env_path}")
                else:
                    print(
                        f"Unknown provider: {provider}. Supported providers are: {', '.join(provider_map.keys())}"
                    )
                    return {"error": "Unknown provider"}
            else:
                print("API key format should be provider=key (e.g., openai=sk-...)")
                return {"error": "Invalid API key format"}
        except Exception as e:
            print(f"Error saving API key: {e}")
            return {"error": str(e)}

    # Directly load the .env file we just created/updated
    dotenv.load_dotenv(env_path)

    # Add model selection if specified
    if args.model:
        # Use the model parameter to set the appropriate environment variable
        model_map = {
            "deepseek": (
                "DEEPSEEK_API_KEY",
                "You need to provide a DeepSeek API key with --api-key deepseek=<key>",
            ),
            "sonnet": (
                "ANTHROPIC_API_KEY",
                "You need to provide an Anthropic API key with --api-key anthropic=<key>",
            ),
            "o3-mini": (
                "OPENAI_API_KEY",
                "You need to provide an OpenAI API key with --api-key openai=<key>",
            ),
            # Add more model mappings here
        }

        if args.model.lower() in model_map:
            env_var, error_msg = model_map[args.model.lower()]
            if not os.getenv(env_var):
                print(error_msg)
                return {"error": error_msg}

            # Set model in environment for the chainlit process
            os.environ["VT_DEFAULT_MODEL"] = args.model
            print(f"Using model: {args.model}")
        else:
            print(
                f"Unknown model: {args.model}. Supported models are: {', '.join(model_map.keys())}"
            )
            return {"error": f"Unknown model: {args.model}"}

    return {
        "args": args,
        "remaining_args": remaining_args,
        "config_dir": config_dir,
        "env_path": env_path,
    }
