import os
import yaml

def load_config() -> dict:
    """Loads the first YAML config file in the current directory that ends with 'atdm_flow.yaml'.

    Returns:
        dict: Parsed YAML configuration.

    Raises:
        FileNotFoundError: If no matching config file is found.
    """
    for file in os.listdir(os.getcwd()):
        if file.endswith("atdm_flow.yaml"):
            with open(file, "r") as f:
                return yaml.safe_load(f)

    raise FileNotFoundError(
        "No config file found ending with 'atdm_flow.yaml' in the project root."
    )