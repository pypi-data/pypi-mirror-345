import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Union

from agents import Agent, Runner, function_tool
from agents.mcp.server import MCPServerStdio
from mcp import ClientSession
from satif_core import AsyncCodeBuilder, CodeBuilder, SDIFDatabase
from satif_sdk.comparators import get_comparator
from satif_sdk.representers import get_representer
from satif_sdk.transformers import CodeTransformer

# Global variables for transformation
INPUT_SDIF_PATH: Optional[Path] = None
OUTPUT_TARGET_FILES: Optional[Dict[Union[str, Path], str]] = None


@function_tool
async def execute_transformation(code: str) -> str:
    """Executes the transformation code on the input and returns the
    comparison difference between the transformed output and the target output example.

    Args:
        code: The code to execute on the input.
    """
    if INPUT_SDIF_PATH is None or OUTPUT_TARGET_FILES is None:
        return "Error: Transformation context not initialized"

    code_transformer = CodeTransformer(function=code)
    generated_output_path = code_transformer.export(INPUT_SDIF_PATH)

    comparisons = []

    if os.path.isdir(generated_output_path):
        # If it's a directory, compare each file with its corresponding target
        generated_files = os.listdir(generated_output_path)

        for (
            output_base_file,
            output_target_file_name,
        ) in OUTPUT_TARGET_FILES.items():
            if output_target_file_name in generated_files:
                generated_file_path = os.path.join(
                    generated_output_path, output_target_file_name
                )
                comparator = get_comparator(output_target_file_name.split(".")[-1])
                comparison = comparator.compare(generated_file_path, output_base_file)
                comparisons.append(
                    f"Comparison for {generated_file_path} [SOURCE] with {output_target_file_name} [TARGET]: {comparison}"
                )
            else:
                comparisons.append(
                    f"Error: {output_target_file_name} not found in the generated output"
                )
    else:
        # If it's a single file, ensure there's only one target and compare
        if len(OUTPUT_TARGET_FILES) == 1:
            output_file = list(OUTPUT_TARGET_FILES.keys())[0]
            output_target_file_name = list(OUTPUT_TARGET_FILES.values())[0]
            comparator = get_comparator(output_file.split(".")[-1])
            comparison = comparator.compare(generated_output_path, output_file)
            comparisons.append(
                f"Comparison for {generated_output_path} [SOURCE] with {output_target_file_name} [TARGET]: {comparison}"
            )
        else:
            comparisons.append(
                "Error: Single output file generated but multiple target files expected"
            )

    return "\n".join(comparisons)


class TransformationCodeBuilder(CodeBuilder):
    def __init__(self, output_example: Path | List[Path] | Dict[str, Path]):
        self.output_example = output_example

    def build(
        self,
        sdif: Path | SDIFDatabase,
        instructions: Optional[str] = None,
    ) -> str:
        pass


class TransformationAsyncCodeBuilder(AsyncCodeBuilder):
    """This class is used to build a transformation code that will be used to transform a SDIF database into a set of files following the format of the given output files."""

    def __init__(
        self,
        mcp_server: MCPServerStdio,
        mcp_session: ClientSession,
        llm_model: str = "o3-mini",
    ):
        self.mcp_server = mcp_server
        self.mcp_session = mcp_session
        self.llm_model = llm_model

    async def build(
        self,
        sdif: Path,
        output_target_files: Dict[Union[str, Path], str] | List[Path],
        output_sdif: Optional[Path] = None,
        instructions: Optional[str] = None,
    ) -> str:
        global INPUT_SDIF_PATH, OUTPUT_TARGET_FILES
        INPUT_SDIF_PATH = Path(sdif)

        if isinstance(output_target_files, list):
            OUTPUT_TARGET_FILES = {file: file.name for file in output_target_files}
        else:
            OUTPUT_TARGET_FILES = output_target_files

        input_schema = await self.mcp_session.read_resource(f"schema://{sdif}")
        input_sample = await self.mcp_session.read_resource(f"sample://{sdif}")

        output_schema = await self.mcp_session.read_resource(f"schema://{output_sdif}")
        output_sample = await self.mcp_session.read_resource(f"sample://{output_sdif}")
        output_representation = {
            file: get_representer(file).represent(file)
            for file in list(OUTPUT_TARGET_FILES.keys())
        }

        prompt = await self.mcp_session.get_prompt(
            "create_transformation",
            arguments={
                "input_file": INPUT_SDIF_PATH.name,
                "input_schema": input_schema.contents[0].text,
                "input_sample": input_sample.contents[0].text,
                "output_files": str(list(OUTPUT_TARGET_FILES.values())),
                "output_schema": output_schema.contents[0].text,
                "output_sample": output_sample.contents[0].text,
                "output_representation": str(output_representation),
            },
        )
        agent = Agent(
            name="Transformation Builder",
            mcp_servers=[self.mcp_server],
            tools=[execute_transformation],
            model=self.llm_model,
        )
        result = await Runner.run(agent, prompt.messages[0].content.text)
        transformation_code = self.parse_code(result.final_output)
        return transformation_code

    def parse_code(self, code) -> str:
        match = re.search(r"```(?:python)?(.*?)```", code, re.DOTALL)
        if match:
            return match.group(1).strip()
        else:
            # Handle case where no code block is found
            return code.strip()
