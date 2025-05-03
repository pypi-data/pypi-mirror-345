"""Build system for XCSP Launcher.

This module defines strategies to build solver sources either automatically
(based on detected build files) or manually (based on explicit configuration).
It also provides utility functions to execute builds while logging their output.
"""

import subprocess
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

import psutil
from loguru import logger

from xcsp.utils.paths import ChangeDirectory, get_cache_dir
from xcsp.utils.placeholder import replace_placeholder, replace_solver_dir

# Mapping of detected build configuration files to standard build commands
MAP_FILE_BUILD_COMMANDS = {
    "build.gradle": ["./gradlew build -x test", "gradle build -x test"],
    "pom.xml": ["mvn package", "mvn install"],
    "CMakeLists.txt": ["cmake . && make", "cmake .. && make"],
    "Makefile": ["make"],
    "Cargo.toml": ["cargo build"],
    "setup.py": ["python setup.py install", "python setup.py build"],
    "pyproject.toml": ["python -m build"]
}

def try_build_from_file(detected_file: Path, log_path: Path) -> bool:
    """Attempt to build a project based on the detected build configuration file.

    Args:
        detected_file (Path): The main build configuration file (e.g., CMakeLists.txt, build.gradle).
        log_path (Path): Path to the build log file.

    Returns:
        bool: True if the build succeeded, False otherwise.
    """
    build_commands = MAP_FILE_BUILD_COMMANDS.get(detected_file.name)
    if not build_commands:
        logger.error(f"No known build commands associated with '{detected_file.name}'.")
        return False

    log_path.parent.mkdir(parents=True, exist_ok=True)

    success = False
    for command in build_commands:
        logger.info(f"Trying build command: {command}")

        with open(log_path, "a") as log_file:
            log_file.write(f"\n--- Trying build command: {command} ---\n")
            log_file.flush()

            try:
                process = psutil.Popen(
                    command,
                    shell=True,
                    cwd=detected_file.parent,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                returncode = process.wait()
                if returncode == 0:
                    logger.success(f"Build succeeded with command: {command}")
                    success = True
                    return True
                else:
                    logger.warning(f"Build failed with command: {command} (exit code {returncode})")

            except Exception as e:
                logger.exception(f"Exception occurred during build: {e}")

    if not success:
        logger.error("All attempted build commands failed.")
    return success

class BuildStrategy(ABC):
    """Abstract base class representing a build strategy for a solver."""

    def __init__(self, path_solver: Path, config_strategy, config=None):
        self._path_solver = path_solver
        self._config_strategy = config_strategy
        self._config = config

    def build(self) -> bool:
        """Execute the build process inside the solver directory."""
        with ChangeDirectory(self._path_solver):
            return self._internal_build()

    @abstractmethod
    def _internal_build(self) -> bool:
        """Internal method for performing the build, must be implemented by subclasses."""
        pass

class AutoBuildStrategy(BuildStrategy):
    """Build strategy using automatic detection based on known build files."""

    def _internal_build(self) -> bool:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = Path(get_cache_dir()) / f"solver_build_{timestamp}.log"
        return try_build_from_file(self._config_strategy.builder_file(), log_path)

class ManualBuildStrategy(BuildStrategy):
    """Build strategy using manual build instructions provided in the configuration."""

    def __init__(self, path_solver: Path, config_strategy, config):
        super().__init__(path_solver, config_strategy, config)

    def _internal_build(self) -> bool:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = Path(get_cache_dir()) / f"solver_build_{timestamp}.log"
        command = self._config.get("build", {}).get("build_command")

        if not command:
            logger.error("No manual build command specified in configuration.")
            return False
        success = False
        log_path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(command, str):
            command = [command]
        with open(log_path, "a") as log_file:
            log_file.write(f"\n--- Trying manual build ---\n")
            logger.info(f"Trying manual build")
            for index,c in enumerate(command):
                c = replace_solver_dir(replace_placeholder(c), str(self._path_solver))
                logger.info(f"Step {index+1}/{len(command)} with command : {c} \n")
                log_file.write(f"Step {index+1}/{len(command)} with command : {c} \n")
                log_file.flush()
                try:
                    process = psutil.Popen(
                        c,
                        shell=True,
                        cwd=self._path_solver,
                        stdout=log_file,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1
                    )
                    returncode = process.wait()
                    if returncode == 0:
                        logger.success(f"Step {index+1} succeeded : {c}")
                        success = True
                    else:
                        logger.warning(f"Step {index+1}/{len(command)} failed : {c} (exit code {returncode})")
                        success = False
                        break
                except Exception as e:
                    logger.exception(f"Exception occurred during manual build: {e}")
                    success = False
            if not success:
                logger.error("Manual build failed after all attempts.")
        return success
