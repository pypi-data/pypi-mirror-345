"""Solver installation manager for XCSP Launcher.

This module handles the full process of installing a solver from a repository:
cloning the repository, detecting or resolving configuration files, verifying
build requirements, building the solver, and placing binaries at the correct locations.
"""

import enum
import os
import platform
import shutil
from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path
import yaml
from git import Repo
from loguru import logger
from timeit import default_timer as timer

from xcsp.builder.build import AutoBuildStrategy, ManualBuildStrategy
from xcsp.builder.check import check_available_builder_for_language, MAP_FILE_LANGUAGE, MAP_LANGUAGE_FILES, MAP_BUILDER
from xcsp.utils.placeholder import replace_placeholder, replace_core_placeholder, replace_solver_dir_in_str
from xcsp.solver.cache import CACHE, Cache
from xcsp.solver.resolver import resolve_config
from xcsp.utils.paths import get_solver_install_dir, ChangeDirectory, get_solver_bin_dir
from xcsp.utils.log import unknown_command
from xcsp.utils.system import is_system_compatible


class RepoSource(enum.Enum):
    """Enumeration of supported repository hosting services."""
    GITHUB = "github.com"
    GITLAB = "gitlab.com"


class ConfigStrategy(ABC):
    """Abstract base class representing a strategy for handling solver configurations."""

    def __init__(self, solver_path: Path, repo):
        self._language = None
        self._builder_file = None
        self._solver_path = solver_path
        self._repo = repo

    def check(self):
        """Check if a valid builder is available for the detected language."""
        return check_available_builder_for_language(self.language())

    def language(self):
        """Return the programming language of the solver."""
        return self._language

    def builder_file(self) -> Path:
        """Return the main build configuration file."""
        return self._builder_file

    @abstractmethod
    def versions(self):
        """Yield information about available versions of the solver."""
        pass

    @abstractmethod
    def detect_language(self):
        """Detect the programming language of the solver based on available files."""
        pass


class NoConfigFileStrategy(ConfigStrategy):
    """Strategy used when no solver configuration file is provided."""

    def versions(self):
        """Yield a single version 'latest' based on the current commit hash."""
        yield {"version": "latest", "git_tag": self._repo.head.object.hexsha, "alias": []}

    def detect_language(self):
        """Attempt to detect the language by scanning known build files."""
        list_files = set(os.listdir(self._solver_path))
        for file in MAP_FILE_LANGUAGE.keys():
            if file in list_files:
                self._language = MAP_FILE_LANGUAGE[file]
                self._builder_file = Path(self._solver_path, file)
                logger.success(f"Detected language using builder file '{file}': {self.language()}")
                return
        raise ValueError("Unable to detect the project language automatically.")


class ConfigFileStrategy(ConfigStrategy):
    """Strategy used when a solver configuration file is available."""

    def __init__(self, solver_path: Path, config):
        super().__init__(solver_path, None)
        self._config = config

    def language(self):
        """Return the programming language from the configuration."""
        return self._config["language"]

    def detect_language(self):
        """Detect the language based on configuration and project structure."""
        logger.success(f"Language provided by configuration file: {self.language()}")
        l = self.language()
        files = MAP_LANGUAGE_FILES[l]
        logger.debug(f"Looking for one of: {', '.join(files)}")

        list_files = set(os.listdir(self._solver_path))
        for f in files:
            if f in list_files:
                self._builder_file = Path(self._solver_path, f)
                return

    def versions(self):
        """Yield all versions specified in the configuration."""
        for v in self._config["versions"]:
            yield v


def build_cmd(config, bin_executable):
    result_cmd = []
    if config["command"].get("prefix"):
        result_cmd.extend(replace_placeholder(config["command"]["prefix"]))
    if options := config["command"].get("always_include_options"):
        template = config["command"]["template"]
        result_cmd.extend(replace_core_placeholder(template, bin_executable, options))
    return result_cmd


class Installer:
    """Main class responsible for installing a solver from a repository."""

    def __init__(self, url: str, solver_name: str, id: str, config=None):
        self._url = url
        self._solver = solver_name
        self._id = id
        self._path_solver = None
        self._start_time = timer()
        self._repo = None
        self._config = config
        self._config_strategy = None
        self._mode_build_strategy = None

    def _init(self):
        """Initialize the solver installation directory."""
        self._path_solver = Path(get_solver_install_dir()) / self._id
        # os.makedirs(self._path_solver, exist_ok=True)

        if not self._id in CACHE:
            CACHE[self._id] = {
                "path_solver": str(self._path_solver.absolute()),
                "name_solver": self._solver,
                "id_solver": self._id,
                "versions": defaultdict(dict),
            }

    def _init_repo(self):
        self._repo = Repo(self._url)

    def _clone(self):
        """Clone the solver repository."""
        logger.info(f"Cloning the solver from {self._url} into {self._path_solver}")
        if os.path.exists(self._path_solver):
            self._repo = Repo(self._path_solver)
            logger.info(
                f"Repository not cloned, path '{self._path_solver}' already exists. {timer() - self._start_time:.2f} seconds.")
            return
        self._repo = Repo.clone_from(self._url, self._path_solver)
        logger.info(f"Repository cloned in {timer() - self._start_time:.2f} seconds.")

    def _resolve_config(self):
        """Resolve and load the solver configuration if available."""

        if self._config is not None:
            self._init_strategies_with_config()
            return

        config_file = resolve_config(self._path_solver, self._solver)

        if config_file is None:
            self._config_strategy = NoConfigFileStrategy(self._path_solver, self._repo)
            self._mode_build_strategy = AutoBuildStrategy(self._path_solver, self._config_strategy)
            return

        with open(config_file, "r") as f:
            self._config = yaml.safe_load(f)
            self._init_strategies_with_config()

    def _init_strategies_with_config(self):
        self._config_strategy = ConfigFileStrategy(self._path_solver, self._config)
        if self._config.get("mode", "manual") == "auto":
            self._mode_build_strategy = AutoBuildStrategy(self._path_solver, self._config_strategy)
        else:
            self._mode_build_strategy = ManualBuildStrategy(self._path_solver, self._config_strategy, self._config)

    def _check(self):
        """Check if the required build tools are available."""
        if not self._config_strategy.check():
            language = self._config_strategy.language()
            logger.error(
                f"None of the builders are available for language '{language}': {', '.join(MAP_BUILDER.get(language))}")
            raise ValueError(
                f"No available builders for the detected language '{language}'.")

    def _manage_dependency(self):
        if not self._config:
            return

        dependencies = self._config.get("build", {}).get("dependencies", [])
        if not dependencies:
            logger.info("No dependencies to manage.")
            return

        logger.info("Managing solver dependencies...")
        for dep in dependencies:
            git_url = dep.get("git")
            if not git_url:
                logger.warning("Dependency without 'git' key found. Skipping.")
                continue

            name = git_url.split("/")[-1].replace(".git", "")
            default_dir = self._path_solver.parent.parent / "deps" / name
            target_dir = replace_solver_dir_in_str(dep.get("dir"), str(self._path_solver)) if dep.get(
                "dir") else default_dir

            target_dir = Path(target_dir)
            target_dir.parent.mkdir(parents=True, exist_ok=True)

            if target_dir.exists():
                logger.info(f"Updating existing dependency in: {target_dir}")
                start_time = timer()
                try:
                    repo = Repo(target_dir)
                    repo.remotes.origin.pull()
                    logger.success(f"Pulled updates for {name} in {timer() - start_time:.2f}s.")
                except Exception as e:
                    logger.error(f"Failed to update dependency at {target_dir}: {e}")
            else:
                logger.info(f"Cloning dependency '{name}' into: {target_dir}")
                start_time = timer()
                try:
                    Repo.clone_from(git_url, target_dir)
                    logger.success(f"Cloned {name} in {timer() - start_time:.2f}s.")
                except Exception as e:
                    logger.error(f"Failed to clone dependency from {git_url} to {target_dir}: {e}")

    def _pull(self):
        pull_start = timer()
        logger.info(f"Pulling solver...")
        o = self._repo.remotes.origin
        o.pull()
        logger.info(f"Pulling finished {pull_start - self._start_time:.2f} seconds.")

    def _check_system(self):
        if not self._config:
            return True
        systems = self._config.get("system")
        return is_system_compatible(systems)

    def install(self):
        """Main method to install the solver."""
        self._init()
        self._clone() if self._url.startswith("http") else self._init_repo()
        self._pull()
        self._resolve_config()
        if not self._check_system():
            system_list = ",".join(self._config.get("system")) if isinstance(self._config.get("system"), list) else self._config.get("system")
            logger.info(f"Current system {platform.system().lower()} is not compatible with the system from {system_list}.")
            return
        self._config_strategy.detect_language()
        self._manage_dependency()
        self._check()

        build_start = timer()
        original_ref = self._repo.active_branch.name if not self._repo.head.is_detached else self._repo.head.object.hexsha
        with ChangeDirectory(self._path_solver):
            for v in self._config_strategy.versions():
                try:
                    logger.info(f"Checking out version '{v['git_tag']}'")
                    self._repo.git.checkout(v["git_tag"])
                    need_compile = v.get("executable") is not None and not (
                            Path(self._path_solver) / v.get('executable')).exists()

                    if not self._mode_build_strategy.build() and need_compile:
                        logger.error(f"Build failed for version '{v['version']}'. Installation aborted.")
                        break

                    bin_dir = get_solver_bin_dir(self._id, f"{v['version']}-{v['git_tag']}")
                    os.makedirs(bin_dir, exist_ok=True)

                    if v.get("executable") is None:
                        logger.warning(
                            f"Version '{v['version']}' was built, but no executable was specified. "
                            f"Please manually copy your binaries into {bin_dir}.")
                        continue
                    executable_path = Path(v['executable'])
                    result_path = shutil.copy(Path(self._path_solver) / v["executable"], bin_dir / executable_path.name)
                    logger.success(f"Executable for version '{v['version']}' successfully copied to {result_path}.")
                    if self._config is not None and self._config.get("command") is not None:
                        CACHE[self._id]["versions"][v['version']] = {
                            "options": self._config["command"]["options"],
                            "cmd": build_cmd(self._config, bin_dir / executable_path.name),
                            "alias": v.get("alias", list())
                        }

                except OSError as e:
                    logger.error(
                        f"An error occurred when building the version '{v['version']}' of solver {self._solver}")
                    logger.exception(e)
                finally:
                    logger.info(f"Restoring original Git reference: {original_ref}")
                    self._repo.git.checkout(original_ref)
        logger.info(f"Building completed in {timer() - build_start:.2f} seconds.")
        logger.info(f"Generating cache of solver...")
        Cache.save_cache(CACHE)
        logger.info(f"Installation completed in {timer() - self._start_time:.2f} seconds.")


def resolve_url(repo, source):
    """Construct the full URL from a repo namespace and source."""
    return "https://" + source.value + "/" + repo


def fill_parser(parser):
    """Add the 'install' subcommand to the parser."""
    parser_install = parser.add_parser("install", aliases=["i"],
                                       help="Subcommand to install a solver from a repository.")
    parser_install.add_argument("--id", help="Unique ID for the solver.", type=str, required=False, default=None)
    parser_install.add_argument("--name", help="Human-readable name of the solver.", type=str, required=False,
                                default=None)
    parser_install.add_argument("-c", "--config", help="A path to a config file.", type=str, required=False,
                                default=None)
    parser_install.add_argument("--url", help="Direct URL to the repository (alternative to --repo).", required=False,
                                default=None)
    parser_install.add_argument("--repo", help="Repository in the form 'namespace/repo' (alternative to --url).",
                                required=False, default=None)
    parser_install.add_argument("--source", help="Hosting service for the repository.", choices=[e for e in RepoSource],
                                default=RepoSource.GITHUB, type=RepoSource)


def install(args):
    logger.debug(args)
    """Execute the installation process based on parsed arguments."""
    if args['url'] is None and args['repo'] is None and args['config'] is None:
        raise ValueError("--url, --repo, --config cannot be None simultaneously.")

    at_most_one_true = [args[k] for k in ['url', 'repo', 'config'] if args[k] is not None]
    if len(at_most_one_true) > 1:
        raise ValueError("Can't be more one of these option specified : '--url','--repo','--config'")
    name = args['name']
    id_s = args['id']
    url = args['url']
    config = None
    if args['config'] is not None and os.path.exists(args['config']):
        with open(args['config'], 'r') as f:
            config = yaml.safe_load(f)
            name = config['name']
            id_s = config['id']
            url = config.get('git', None) or config.get('path', None)
    if url is None:
        url = resolve_url(args['repo'], args['source'])

    installer = Installer(url, name, id_s, config=config)
    installer.install()


MAP_COMMAND = {
    "install": install,
}


def manage_command(args):
    """Dispatch and manage subcommands for the XCSP launcher binary.

    Args:
        args (dict): Parsed command-line arguments.
    """
    subcommand = args['subcommand']
    MAP_COMMAND.get(subcommand, unknown_command)(args)
