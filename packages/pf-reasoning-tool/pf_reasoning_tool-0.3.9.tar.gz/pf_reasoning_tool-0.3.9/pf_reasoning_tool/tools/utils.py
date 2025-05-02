# C:\Users\CRVI\OneDrive - Hall & Wilcox\promptflowcustomtools\pf-reasoning-tool-proj\pf_reasoning_tool\tools\utils.py
# --- Updated to load standard YAML format from the 'yamls' directory ---

# Using ruamel.yaml as originally specified. Ensure it's installed: pip install ruamel.yaml
# Alternatively, you could use the standard PyYAML library: pip install pyyaml
from ruamel.yaml import YAML
from pathlib import Path


def collect_tools_from_directory(base_dir) -> dict:
    """
    Collects tool definitions from standard YAML files within the specified directory.
    Uses the filename stem (e.g., 'reasoning_tool_call') as the tool identifier key.
    """
    tools = {}
    yaml_loader = YAML(typ='safe') # Use safe loader

    # Check if the base directory exists
    if not Path(base_dir).is_dir():
        print(f"Warning: Tool YAML directory not found: {base_dir}")
        return tools

    # Search only directly within the specified base_dir (non-recursive)
    for f_path in Path(base_dir).glob("*.yaml"):
        tool_identifier = f_path.stem # e.g., "reasoning_tool_call"
        print(f"Found potential tool YAML: {f_path.name}, attempting to load with identifier: {tool_identifier}")
        try:
            with open(f_path, "r", encoding='utf-8') as f_handle:
                # Load the entire YAML content as the tool definition
                tool_definition = yaml_loader.load(f_handle)

                # Basic validation: Check if it looks like a PromptFlow tool definition
                if isinstance(tool_definition, dict) and tool_definition.get("function"):
                    tools[tool_identifier] = tool_definition
                    print(f"  > Successfully loaded tool: {tool_identifier}")
                else:
                    print(f"  > Warning: File {f_path.name} does not appear to be a valid tool definition (missing 'function' key?). Skipping.")

        except Exception as e:
            print(f"  > Error loading or processing YAML file {f_path.name}: {e}")

    if not tools:
        print(f"Warning: No valid tool YAML files found in {base_dir}")

    return tools


def list_package_tools():
    """
    List package tools by searching for YAML files in the 'yamls' subdirectory
    relative to the package root.
    """
    # This path calculation correctly points to pf_reasoning_tool/yamls/
    # based on utils.py being in pf_reasoning_tool/tools/
    yaml_dir = Path(__file__).resolve().parents[1] / "yamls"

    print(f"Executing list_package_tools - Looking for tool YAMLs in: {yaml_dir}")
    return collect_tools_from_directory(yaml_dir)

# --- End Updated Code ---