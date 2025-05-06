import os
import subprocess

from loguru import logger


def install_requirements(requirements_file: str, force: bool = False) -> bool:
    cmd = ["pip", "install", "-r", requirements_file]
    if force:
        cmd.insert(2, "--force-reinstall")
    # Install dependencies if a requirements.txt file exists
    if os.path.exists(requirements_file):
        logger.info(f"Installing dependencies '{requirements_file}'...")
        subprocess.check_call(cmd)
        logger.info(f"Dependencies '{requirements_file}' installed !")
        return True
    else:
        logger.warning(f"No requirements file found : '{requirements_file}'.")
        return False