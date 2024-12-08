import os
import json


def get_workspace_root():
    """Returns the root directory of the workspace."""
    return os.getcwd()


def get_launch_json_path(workspace_root):
    """Returns the path to the launch.json file."""
    vscode_dir = os.path.join(workspace_root, ".vscode")
    return os.path.join(vscode_dir, "launch.json")


def read_launch_json(launch_json_path):
    """Reads and returns the parsed JSON data from the launch.json file."""
    if not os.path.exists(launch_json_path):
        raise FileNotFoundError(f"Error: launch.json not found at {launch_json_path}")

    with open(launch_json_path, "r") as file:
        return json.load(file)


def create_output_directory(workspace_root):
    """Creates the output directory for the scripts."""
    output_dir = os.path.join(workspace_root, "debug-scripts")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def generate_script_content(config, workspace_root):
    """Generates the content for a debug script based on the configuration."""
    name = config.get("name")
    program = config.get("program")
    args = config.get("args", [])
    gdb_path = config.get("miDebuggerPath")

    # Resolve ${workspaceFolder} in the program path
    if "${workspaceFolder}" in program:
        program = program.replace("${workspaceFolder}", workspace_root)

    arguments = " ".join(args)
    script_content = f"""#!/bin/bash
# Debug script for {name}

{gdb_path} \\
    --eval-command="target remote :3333" \\
    --eval-command="file {program}" \\
    {arguments}
"""
    return script_content


def save_script(script_name, script_content, output_dir):
    """Saves the generated script to the specified directory."""
    script_path = os.path.join(output_dir, script_name)
    with open(script_path, "w") as script_file:
        script_file.write(script_content)

    # Make the script executable
    os.chmod(script_path, 0o755)


def generate_debug_scripts():
    """Generates debug scripts based on the configurations in launch.json."""
    workspace_root = get_workspace_root()
    launch_json_path = get_launch_json_path(workspace_root)

    try:
        launch_data = read_launch_json(launch_json_path)
    except FileNotFoundError as e:
        print(e)
        return

    configurations = launch_data.get("configurations", [])
    if not configurations:
        print("Error: No configurations found in launch.json")
        return

    output_dir = create_output_directory(workspace_root)

    for config in configurations:
        name = config.get("name")
        script_name = f"{name.replace(' ', '_')}.sh"

        # Generate the content for the script
        script_content = generate_script_content(config, workspace_root)

        # Save the script and make it executable
        save_script(script_name, script_content, output_dir)

    print(f"Debug scripts generated in {output_dir}")


def main():
    """Main entry point for the script."""
    print("Starting to generate debug scripts...")
    generate_debug_scripts()


if __name__ == "__main__":
    main()
