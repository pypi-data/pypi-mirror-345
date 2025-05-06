import logging
import sqlite3  # Ensure sqlite3 is imported if needed
from pathlib import Path

import pandas as pd
from agents import function_tool
from satif_sdk import SDIFDatabase
from satif_sdk.code_executors import CodeExecutionError, LocalCodeExecutor

logger = logging.getLogger(__name__)

# Global or context for the tool (similar to TidyAdapter)
PLOTTING_TOOL_CONTEXT = {
    "input_sdif_path": None,
    "user_instructions": None,
    "output_plot_path": None,
}


@function_tool
async def execute_plotting_code(code: str) -> str:
    """
    Executes the provided Python plotting script code.
    The code should use the pre-defined 'db' (SDIFDatabase instance)
    and 'instructions' (string) variables.
    The code MUST save the generated Plotly plot to 'plot.html'.
    Returns the path to the saved plot on success or an error message.
    """
    input_sdif_path = PLOTTING_TOOL_CONTEXT.get("input_sdif_path")
    user_instructions = PLOTTING_TOOL_CONTEXT.get("user_instructions")

    if not input_sdif_path:
        return "Error: Input SDIF path not found in tool context."
    # Check existence *before* trying to open
    if not Path(input_sdif_path).exists():
        return f"Error: Input SDIF file not found at {input_sdif_path}."
    if user_instructions is None:
        # Allow empty instructions, pass empty string
        user_instructions = ""
        logger.warning(
            "User instructions not found in tool context, using empty string."
        )
        # return "Error: User instructions not found in tool context."

    # Use LocalCodeExecutor - WARNING: Insecure for untrusted code
    executor = LocalCodeExecutor()

    expected_output_filename = "plot.html"
    # Resolve path relative to the current working directory
    expected_output_path = Path(expected_output_filename).resolve()

    # Clear previous plot if it exists
    if expected_output_path.exists():
        try:
            expected_output_path.unlink()
        except OSError as e:
            logger.error(
                f"Could not remove existing plot file {expected_output_path}: {e}"
            )

    # Prepare the extra context for the executor
    db_instance = None
    try:
        # Instantiate the DB instance to be passed to the code
        # Use read-only mode as the code should only read for plotting
        db_instance = SDIFDatabase(input_sdif_path, read_only=True)

        # Define the context that will be available to the executed code
        code_context = {
            "db": db_instance,
            "instructions": user_instructions,
            # Add any other context variables if needed by the executor/code
        }

        # The code provided by the agent is now expected to be a script
        script_code = f"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from satif.sdif_database.database import SDIFDatabase # Make class available for type hints etc.
import sqlite3 # For potential use by pandas/db interaction

# Pre-defined variables available:
# db: SDIFDatabase instance connected to {input_sdif_path}
# instructions: str = User's instructions

# --- User's Script Code Start ---
{code}
# --- User's Script Code End ---
"""
        logger.debug(f"Executing plotting script code:\n---\n{code[:500]}...\n---")

        # LocalCodeExecutor.execute expects 'db' and 'datasource' in its signature
        # We pass our *actual* db instance as part of extra_context which overrides
        # the dummy 'db' argument passed for signature compliance.
        executor.execute(
            code=script_code,
            db=db_instance,  # Pass instance for signature, but it's also in extra_context
            datasource=None,  # Not needed
            extra_context=code_context,  # Pass db and instructions here
        )

        # Check if the expected output file was created
        if expected_output_path.exists():
            logger.info(
                f"Plotting code executed successfully. Output: {expected_output_path}"
            )
            PLOTTING_TOOL_CONTEXT["output_plot_path"] = expected_output_path
            return f"Success: Plot saved to {expected_output_path}"
        else:
            logger.error(
                "Plotting code executed but output file 'plot.html' not found."
            )
            # Check if the error might be within the script's own error handling
            # (This requires parsing the execution output, which LocalExecutor doesn't provide easily)
            return "Error: Code executed (possibly with internal errors), but the expected output file 'plot.html' was not created."

    except (
        CodeExecutionError,
        sqlite3.Error,
        FileNotFoundError,
        ValueError,
        TypeError,
    ) as e:
        logger.error(f"Error executing plotting code or accessing DB: {e}")
        # Attempt to provide more specific feedback if possible
        error_message = f"Error executing plotting code: {e}"
        # Look for common issues like table not found
        if isinstance(e, pd.io.sql.DatabaseError) and "no such table" in str(e).lower():
            error_message = f"Error executing plotting code: Table not found. {e}"
        elif isinstance(e, KeyError):  # Pandas KeyError on column access
            error_message = f"Error executing plotting code: Column not found or data processing error. {e}"

        return error_message  # Return the formatted error
    except Exception as e:
        logger.exception("Unexpected error during plotting code execution via tool.")
        return f"Unexpected Error during execution: {e}"
    finally:
        # Ensure the db instance created here is closed
        if db_instance:
            try:
                db_instance.close()
                logger.debug("Closed DB instance in plotting tool.")
            except Exception as close_err:
                logger.error(f"Error closing DB instance in plotting tool: {close_err}")
