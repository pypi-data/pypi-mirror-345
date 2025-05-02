from pathlib import Path
import toml  # Replace configparser with toml
import subprocess  # Add subprocess for shell command execution

def get_project_file_path(relative_path):
    """
    Get the path to a file located relative to the root of the project directory,
    two folders up from the script directory.

    Args:
        relative_path (str): Relative path to the file from the root directory.

    Returns:
        Path: Absolute path to the specified file.
    """
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent.parent
    file_path = root_dir / relative_path

    return file_path

def copy_and_replace(input_path, output_path, string_mappings):
    """
    Copy a file or all files from the input directory to the output path, replacing strings
    in the files based on the provided dictionary of mappings.

    Args:
        input_path (str or Path): Path to the input file or directory.
        output_path (str or Path): Path to the output file or directory.
        string_mappings (dict): Dictionary where keys are strings to replace, and values are their replacements.

    Raises:
        FileNotFoundError: If the input path does not exist.
        ValueError: If the input path is not a file or directory.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input path does not exist: {input_path}")

    if input_path.is_file():
        # Handle single file copy and replace
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with input_path.open("r", encoding="utf-8") as f:
            content = f.read()
        for old_str, new_str in string_mappings.items():
            content = content.replace(old_str, new_str)
        with output_path.open("w", encoding="utf-8") as f:
            f.write(content)

    elif input_path.is_dir():
        # Handle directory copy and replace
        output_path.mkdir(parents=True, exist_ok=True)
        for file_path in input_path.rglob("*"):
            relative_path = file_path.relative_to(input_path)
            target_path = output_path / relative_path
            if file_path.is_dir():
                target_path.mkdir(parents=True, exist_ok=True)
            else:
                with file_path.open("r", encoding="utf-8") as f:
                    content = f.read()
                for old_str, new_str in string_mappings.items():
                    content = content.replace(old_str, new_str)
                with target_path.open("w", encoding="utf-8") as f:
                    f.write(content)
    else:
        raise ValueError(f"Input path is neither a file nor a directory: {input_path}")

if __name__ == "__main__":

    print("Welcome to Antelop's workflow installation tool.\n")

    # Load the configuration file
    config_path = get_project_file_path('install_scripts/workflows/workflows_config.toml')  # Updated file name
    config = toml.load(config_path)  # Use toml to load the configuration
    install_dir = Path(config['paths']['install_dir'])
    data_dir = Path(config['paths']['data_dir'])
    work_dir = Path(
    config['paths']['work_dir'])
    email = config['misc']['email']
    unix_group = config['misc']['unix_group']
    workflows = config['install']['workflows']
    containers = config['install']['containers']
    nextflow = config['install']['nextflow']
    print("Config loaded successfully\n")

    workflows_dir = install_dir / "workflows"
    containers_dir = install_dir / "containers"
    workflows_dir.mkdir(parents=True, exist_ok=True)
    containers_dir.mkdir(parents=True, exist_ok=True)

    # Check if the install directory exists
    if not install_dir.exists():
        raise FileNotFoundError(f"Install directory does not exist: {install_dir}")

    # Change ownership and permissions of the install directory
    print(f"Setting ownership and permissions for {install_dir}")
    chown_command = f"chown -R :{unix_group} {install_dir}"
    chmod_command = f"chmod -R 755 {install_dir}"
    try:
        subprocess.run(chown_command, shell=True, check=True)
        subprocess.run(chmod_command, shell=True, check=True)
        print(f"Ownership and permissions set successfully for {install_dir}\n")
    except subprocess.CalledProcessError as e:
        print(f"Failed to set ownership or permissions: {e}\n")

    if workflows:
        # Copy the workflows template directory to the install directory
        print(f"Installing workflows to {install_dir}")
        workflows_template_path = get_project_file_path("workflows-template")
        config_mapping = {
            "<install_dir>": str(install_dir),
            "<data_dir>": str(data_dir),
            "<work_dir>": str(work_dir),
            "<email>": email,
        }
        copy_and_replace(workflows_template_path, workflows_dir, config_mapping)
        print("Workflows installed successfully\n")

    if containers:
        # Configure the .def file
        print("Configuring the .def file")
        input_def_path = str(get_project_file_path("install_scripts/containers/antelop-python.def"))
        output_def_path = str(get_project_file_path("install_scripts/containers/antelop-python-configured.def"))
        config_mapping = {
            "<repo_directory>": str(get_project_file_path(".")),
        }
        copy_and_replace(input_def_path, output_def_path, config_mapping)
        print(f"Configured .def file written to {output_def_path}\n")

        # Containers to build
        containers = {
            "antelop-python.sif": "antelop-python-configured.def",
            "caiman.sif": "caiman.def",
            "dlc.sif": "dlc.def",
            "mountainsort5.sif": "mountainsort5.def",
            "pykilosort.sif": "pykilosort.def",
            "spikeinterface.sif": "spikeinterface.def"
        }

        print("Creating singularity containers\n")
        # Build the containers
        for output, input in containers.items():
            print(f"Building {output} using {input}")
            build_command = f"apptainer build {containers_dir / output} {get_project_file_path(f'install_scripts/containers/{input}')}"
            print(build_command)
            try:
                subprocess.run(build_command, shell=True, check=True)  # Execute the command
                print(f"Successfully built {output}\n")
            except subprocess.CalledProcessError as e:
                print(f"Failed to build {output}: {e}\n")

    if nextflow:
        # Install Nextflow
        print("Installing Nextflow\n")
        nextflow_dir = install_dir / "bin" / "nextflow"
        nextflow_dir.mkdir(parents=True, exist_ok=True)
        nextflow_url = "https://github.com/nextflow-io/nextflow/releases/download/v23.10.3/nextflow"
        nextflow_path = nextflow_dir / "nextflow"
        download_command = f"curl -L {nextflow_url} -o {nextflow_path} && chmod +x {nextflow_path}"
        try:
            subprocess.run(download_command, shell=True, check=True)
            print(f"Nextflow downloaded and installed successfully at {nextflow_path}\n")
        except subprocess.CalledProcessError as e:
            print(f"Failed to download and install Nextflow: {e}\n")

    # Change ownership and permissions of the install directory
    print(f"Setting ownership and permissions for {install_dir}")
    chown_command = f"chown -R :{unix_group} {install_dir}"
    chmod_command = f"chmod -R 755 {install_dir}"
    try:
        subprocess.run(chown_command, shell=True, check=True)
        subprocess.run(chmod_command, shell=True, check=True)
        print(f"Ownership and permissions set successfully for {install_dir}\n")
    except subprocess.CalledProcessError as e:
        print(f"Failed to set ownership or permissions: {e}\n")
