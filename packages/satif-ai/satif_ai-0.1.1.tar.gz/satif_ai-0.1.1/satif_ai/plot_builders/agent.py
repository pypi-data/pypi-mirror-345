import logging
import re
from pathlib import Path
from typing import Optional, Union

from agents import Agent, Runner
from agents.mcp import MCPServerStdio
from mcp import ClientSession

from satif_ai.plot_builders.prompt import PLOTTING_AGENT_PROMPT
from satif_ai.plot_builders.tool import PLOTTING_TOOL_CONTEXT, execute_plotting_code

logger = logging.getLogger(__name__)


class PlottingAgent:
    """Agent that generates Plotly plots from SDIF data based on user instructions."""

    def __init__(
        self,
        mcp_server: MCPServerStdio,
        mcp_session: ClientSession,
        llm_model: str = "o4-mini",
    ):
        self.mcp_server = mcp_server
        self.mcp_session = mcp_session
        self.llm_model = llm_model

    def _parse_final_path(self, final_text: str) -> Optional[Path]:
        """Extracts the path from the success message."""
        # Regex to find the path after "Success: Plot saved to "
        match = re.search(r"Success: Plot saved to (.*)", final_text)
        if match:
            path_str = match.group(1).strip()
            try:
                p = Path(path_str)
                # Check if it seems plausible (e.g., ends with .html and absolute)
                # Check for existence here is important
                if p.is_absolute() and p.name.endswith(".html") and p.exists():
                    return p
                elif (
                    p.exists()
                ):  # Accept relative path if it exists (less ideal but maybe happens)
                    logger.warning(
                        f"Parsed path {p} is not absolute but exists. Accepting."
                    )
                    return p.resolve()  # Return resolved absolute path
            except Exception as e:
                logger.warning(f"Error validating parsed path '{path_str}': {e}")
                pass
        # Fallback checks remain the same
        if "plot.html" in final_text:
            potential_path_str = final_text.strip()
            # Try to extract if it's just the path
            if Path(potential_path_str).name == "plot.html":
                try:
                    potential_path = Path(
                        potential_path_str
                    ).resolve()  # Resolve relative paths
                    if potential_path.exists():
                        logger.warning(
                            "Agent returned path directly instead of success message."
                        )
                        return potential_path
                except Exception:
                    pass

        return None

    async def generate_plot(
        self, sdif_path: Union[str, Path], instructions: str
    ) -> Optional[Path]:
        """
        Generates a Plotly plot HTML file based on instructions and SDIF data.

        Args:
            sdif_path: Path to the input SDIF database file.
            instructions: Natural language instructions for the plot.

        Returns:
            Path to the generated HTML plot file, or None if generation failed.

        Raises:
            FileNotFoundError: If the input SDIF file does not exist.
            RuntimeError: If agent execution fails or context cannot be fetched or plot fails.
            Exception: For other unexpected errors.
        """
        input_path = sdif_path
        # Set tool context
        PLOTTING_TOOL_CONTEXT["input_sdif_path"] = input_path
        PLOTTING_TOOL_CONTEXT["user_instructions"] = instructions
        PLOTTING_TOOL_CONTEXT["output_plot_path"] = None

        agent_final_output_text = (
            "Agent did not produce final output."  # Default message
        )

        try:
            # Get Initial Context from MCP Resources
            logger.info(
                f"Fetching schema and sample for {input_path}..."
            )  # Changed level to INFO
            input_schema_str = "Error: Could not get schema."
            input_sample_str = "Error: Could not get sample."
            try:
                input_path_str = str(input_path)
                schema_uri = f"schema://{input_path_str}"
                sample_uri = f"sample://{input_path_str}"
                logger.debug(f"Requesting schema URI: {schema_uri}")
                logger.debug(f"Requesting sample URI: {sample_uri}")

                input_schema_resource = await self.mcp_session.read_resource(schema_uri)
                input_sample_resource = await self.mcp_session.read_resource(sample_uri)

                input_schema_str = (
                    input_schema_resource.contents[0].text
                    if input_schema_resource.contents
                    else "Error: Could not get schema (empty response)."
                )
                input_sample_str = (
                    input_sample_resource.contents[0].text
                    if input_sample_resource.contents
                    else "Error: Could not get sample (empty response)."
                )

            except Exception as mcp_err:
                logger.error(f"Failed to get schema/sample via MCP: {mcp_err}")
                raise RuntimeError(
                    f"Failed to get required context via MCP: {mcp_err}"
                ) from mcp_err

            # Format the prompt
            formatted_prompt = PLOTTING_AGENT_PROMPT.format(
                input_sdif_path=str(input_path),
                input_schema=input_schema_str,
                input_sample=input_sample_str,
                user_instructions=instructions,
            )

            # Instantiate the Agent
            agent = Agent(
                name="Plotting Agent",
                mcp_servers=[self.mcp_server],
                tools=[execute_plotting_code],
                model=self.llm_model,
            )

            # Run the agent
            logger.info(f"Running Plotting Agent with model {self.llm_model}...")
            result = await Runner.run(
                agent,
                input=formatted_prompt,
            )

            if not result or not result.final_output:
                raise RuntimeError(
                    "Plotting agent execution failed or returned no output."
                )

            agent_final_output_text = (
                result.final_output
            )  # Store for potential error message
            logger.info(
                f"Plotting Agent finished. Final output:\n{agent_final_output_text}"
            )

            # Attempt to parse the path from the agent's final confirmation
            final_plot_path = self._parse_final_path(agent_final_output_text)

            if final_plot_path:  # Path found and exists
                logger.info(
                    f"Successfully confirmed plot generation at: {final_plot_path}"
                )
                return final_plot_path
            else:
                final_plot_path_from_context = PLOTTING_TOOL_CONTEXT.get(
                    "output_plot_path"
                )
                if (
                    final_plot_path_from_context
                    and final_plot_path_from_context.exists()
                ):
                    logger.warning(
                        "Parsed path from final output failed, but tool context has valid path."
                    )
                    return final_plot_path_from_context
                else:
                    logger.error(
                        "Agent finished, but could not confirm successful plot generation or find output file."
                    )
                    # Include agent output in error for debugging
                    raise RuntimeError(
                        f"Agent finished, but plot generation failed or output path couldn't be determined. Agent final output: '{agent_final_output_text}'"
                    )  # Modified Error

        except Exception as e:
            logger.exception(f"Error during PlottingAgent generate_plot: {e}")
            raise  # Re-raise other exceptions
        finally:
            # Robust context cleanup using pop
            PLOTTING_TOOL_CONTEXT.pop("input_sdif_path", None)
            PLOTTING_TOOL_CONTEXT.pop("user_instructions", None)
            PLOTTING_TOOL_CONTEXT.pop("output_plot_path", None)
            logger.debug("Cleared plotting tool context.")
