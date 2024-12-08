import os
import json


def parse_launch_json(file_path):
    # Load the launch.json file
    with open(file_path, "r") as f:
        data = json.load(f)
    return data.get("configurations", [])


def generate_openocd_command(config):
    # Construct OpenOCD command
    config_files = " ".join([f"-f {cfg}" for cfg in config.get("configFiles", [])])
    cwd = config.get("cwd", ".")
    return f"cd {cwd} && openocd {config_files}"


def generate_gdb_command(config):
    # Construct arm-none-eabi-gdb command
    executable = config.get("executable", "")
    svd_file = config.get("svdFile", "")
    cwd = config.get("cwd", ".")
    entry_point = config.get("runToEntryPoint", "main")

    gdb_commands = [
        f"cd {cwd}",
        f'arm-none-eabi-gdb {executable} -ex "target remote :3333"',
        f'-ex "set auto-load safe-path {cwd}"',
        f'-ex "monitor reset halt"',
        f'-ex "load"',
        f'-ex "break {entry_point}"',
        f'-ex "continue"',
    ]
    if svd_file:
        gdb_commands.insert(2, f'-ex "set tdesc filename {svd_file}"')

    return "\n".join(gdb_commands)


def create_script_files(configurations, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for config in configurations:
        name = config.get("name", "Unknown").replace(" ", "_")
        openocd_command = generate_openocd_command(config)
        gdb_command = generate_gdb_command(config)

        openocd_script_path = os.path.join(output_dir, f"{name}_openocd.sh")
        gdb_script_path = os.path.join(output_dir, f"{name}_gdb.sh")

        # Write OpenOCD script
        with open(openocd_script_path, "w") as openocd_script:
            openocd_script.write("#!/bin/bash\n")
            openocd_script.write(openocd_command + "\n")

        # Write GDB script
        with open(gdb_script_path, "w") as gdb_script:
            gdb_script.write("#!/bin/bash\n")
            gdb_script.write(gdb_command + "\n")

        # Make scripts executable
        os.chmod(openocd_script_path, 0o755)
        os.chmod(gdb_script_path, 0o755)

        print(f"Scripts created: {openocd_script_path}, {gdb_script_path}")


def main():
    # Locate launch.json in the .vscode directory
    vscode_dir = os.path.join(os.getcwd(), ".vscode")
    launch_json_path = os.path.join(vscode_dir, "launch.json")

    if not os.path.exists(launch_json_path):
        print(f"Error: launch.json not found in {vscode_dir}.")
        return

    output_dir = os.path.join(os.getcwd(), "generated_scripts")
    configurations = parse_launch_json(launch_json_path)
    create_script_files(configurations, output_dir)
    print(f"All scripts generated in the '{output_dir}' folder.")


if __name__ == "__main__":
    main()
