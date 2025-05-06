import typer
import typer
import logging
import os
from dotenv import load_dotenv
from typing import Optional, List # Added List

# --- Logging Setup ---
# Configure basic logging early
# Levels: DEBUG=10, INFO=20, WARNING=30, ERROR=40, CRITICAL=50
log_level_str = os.getenv("LOG_LEVEL", "WARNING").upper()
log_level = getattr(logging, log_level_str, logging.WARNING)
logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Load .env file ---
# Assume .env is inside the llm_tester directory, relative to this cli package
_cli_package_dir = os.path.dirname(os.path.abspath(__file__))
_llm_tester_dir = os.path.dirname(_cli_package_dir) # Go up one level
_dotenv_path = os.path.join(_llm_tester_dir, '.env') # Path is llm_tester/.env

def load_env(env_path: Optional[str] = None):
    """Loads .env file, prioritizing explicit path."""
    load_path = env_path or _dotenv_path
    if os.path.exists(load_path):
        # Force override in case variable exists but is empty in parent environment
        loaded = load_dotenv(dotenv_path=load_path, override=True)
        if loaded:
            logger.info(f"Loaded environment variables from: {load_path} (override=True)")
        else:
            logger.warning(f"Attempted to load .env from {load_path}, but it might be empty or already loaded.")
    else:
        if env_path: # Only warn if a specific path was given and not found
             logger.warning(f"Specified --env file not found: {env_path}. Using default environment.")
        else:
             logger.info(f"Default .env file not found at {_dotenv_path}. Using default environment.")

# Initial load using default path
load_env()

# --- Typer App Initialization ---
app = typer.Typer(
    name="llm-tester",
    help="Test and manage LLM performance with pydantic models.",
    add_completion=False # Disable shell completion for now
)

# --- Global Options Callback ---
@app.callback()
def main_options(
    ctx: typer.Context,
    verbose: int = typer.Option(0, "--verbose", "-v", count=True, help="Increase verbosity level (-v for INFO, -vv for DEBUG)."),
    env: Optional[str] = typer.Option(None, "--env", help=f"Path to .env file (overrides default {_dotenv_path}).")
):
    """
    LLM Tester CLI main options.
    """
    # --- Setup Logging Level based on verbosity ---
    if verbose == 1:
        effective_log_level = logging.INFO
    elif verbose >= 2:
        effective_log_level = logging.DEBUG
    else:
        effective_log_level = log_level # Use level from env or default WARNING

    # Apply log level to root logger and llm_tester logger
    logging.getLogger().setLevel(effective_log_level)
    logging.getLogger('llm_tester').setLevel(effective_log_level) # Target our specific package logger
    logger.info(f"Logging level set to {logging.getLevelName(effective_log_level)}")

    # --- Handle explicit --env argument ---
    if env:
        load_env(env_path=env) # Reload with the specified path

    # Store context if needed by subcommands (optional)
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["env_path"] = env

    # Store invocation context to check if a subcommand was called
    ctx.obj["invoked_subcommand"] = ctx.invoked_subcommand


# --- Interactive Mode Launch Logic ---
# We need to check *after* parsing if a command was invoked.
# If not, we launch the interactive session.
# This is typically done after the app() call, but Typer doesn't easily support
# running something *only* if no command was found directly in the callback.
# A common workaround is to check ctx.invoked_subcommand at the end of the script execution.
# Let's add the command first, and handle the default launch later if needed.

# --- Register Command Groups ---
from .commands import providers, configure # Removed llm_models import
app.add_typer(providers.app, name="providers")
# app.add_typer(llm_models.app, name="llm-models") # Removed registration
app.add_typer(configure.app, name="configure")

# --- Register schemas command group ---
from .commands import schemas
app.add_typer(schemas.app, name="schemas")

# --- Register Top-Level Commands (from run.py) ---
# Import the specific command functions from the run module
from .commands.run import run_tests, list_items

# Register run_tests as the 'run' command (or maybe 'test'?)
# Let's make it 'run' to match the old default behavior implicitly
@app.command("run")
def run_command(
    # Re-declare options here, matching run.py's run_tests signature
    providers: Optional[List[str]] = typer.Option(None, "--providers", "-p", help="LLM providers to test (default: all enabled)."),
    models: Optional[List[str]] = typer.Option(None, "--models", "-m", help="Specify models as 'provider:model_name' or 'provider/model_name'. Can be used multiple times."),
    test_dir: Optional[str] = typer.Option(None, "--test-dir", help="Directory containing test files (default: uses LLMTester default)."),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output file for report/JSON (default: stdout)."),
    json_output: bool = typer.Option(False, "--json", help="Output results as JSON instead of Markdown report."),
    optimize: bool = typer.Option(False, "--optimize", help="Optimize prompts before running final tests."),
    filter: Optional[str] = typer.Option(None, "--filter", "-f", help="Filter test cases by pattern (e.g., 'module/name'). Not fully implemented.")
):
    """
    Run the LLM test suite with the specified configurations.
    (This is the primary command if no subcommand is specified in the old CLI)
    """
    # Directly call the implementation function from run.py
    run_tests(
        providers=providers,
        models=models,
        test_dir=test_dir,
        output_file=output_file,
        json_output=json_output,
        optimize=optimize,
        filter=filter
    )

# Register list_items as the 'list' command
@app.command("list")
def list_command(
     # Re-declare options here, matching run.py's list_items signature
    providers: Optional[List[str]] = typer.Option(None, "--providers", "-p", help="LLM providers to list (default: all enabled)."),
    models: Optional[List[str]] = typer.Option(None, "--models", "-m", help="Specify models to consider for provider listing."),
    test_dir: Optional[str] = typer.Option(None, "--test-dir", help="Directory containing test files to list.")
):
    """
    List discovered test cases and configured providers/models without running tests.
    """
    # Directly call the implementation function from run.py
    list_items(
        providers=providers,
        models=models,
        test_dir=test_dir
    )

# --- Register recommend command ---
from .commands.recommend import recommend_model_command
# Register recommend_model_command as the 'recommend-model' command
app.command("recommend-model")(recommend_model_command)

# --- Register interactive command ---
from .commands.interactive import start_interactive_command
app.command("interactive")(start_interactive_command)


# --- Default Action (if no command given) ---
# Typer doesn't have a built-in "run this if no command".
# We can handle this in the __main__ block by checking the context
# after app() has run, although it's a bit less clean.
# A simpler approach for now is to rely on the user running `llm-tester interactive`.
# Let's stick to the explicit command for now.


if __name__ == "__main__":
    app()
