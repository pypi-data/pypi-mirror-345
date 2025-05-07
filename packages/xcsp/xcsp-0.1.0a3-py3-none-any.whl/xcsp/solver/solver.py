"""
Module providing the Solver class to launch and monitor solver executions on XCSP3 instances.

It supports:
- Managing solver options (time limit, seeds, solution limits, etc.)
- Capturing solver outputs (objective values, assignments)
- Enforcing timeouts
- Building JSON or human-readable results
- Displaying execution summaries with wall-clock and CPU times
"""

import enum
import json
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List

import psutil
from loguru import logger

from xcsp.solver.cache import CACHE
from xcsp.utils.json import CustomEncoder

ANSWER_PREFIX = "s" + chr(32)
OBJECTIVE_PREFIX = "o" + chr(32)
SOLUTION_PREFIX = "v" + chr(32)


class ResultStatusEnum(enum.Enum):
    """
    Enum representing standard solver statuses such as SATISFIABLE, UNSATISFIABLE, UNKNOWN, and OPTIMUM FOUND.
    """
    SATISFIABLE = "SATISFIABLE"
    UNSATISFIABLE = "UNSATISFIABLE"
    UNKNOWN = "UNKNOWN"
    OPTIMUM = "OPTIMUM FOUND"
    TIMEOUT = "TIMEOUT"
    ERROR = "ERROR"
    MEMOUT = "MEMOUT"


class Solver:
    """
    Class representing a solver execution context for an XCSP3 model.
    Allows setting solver options, running the solver, and capturing results.
    """

    def __init__(self, name, id_solver, version, command_line, options, alias=None):
        """
        Initialize a Solver instance.

        Args:
            name (str): Human-readable name of the solver.
            id_solver (str): Unique solver identifier.
            version (str): Solver version.
            command_line ([str]): Base command line template as list with placeholder replaced.
            options (dict): Mapping of standard solver options.
            alias (list, optional): List of alternative names for the solver.
        """
        self._prefix = None
        self._stderr = sys.stderr
        self._stdout = sys.stdout
        self._name = name
        self._id = id_solver
        self._version = version
        self._command_line = command_line
        self._options = options
        self._args = []
        self._alias = alias if alias is not None else []
        self._solutions = None
        self._time_limit = None
        self._print_intermediate_assignment = False
        self._json_output = False

    @property
    def name(self):
        """Return the name of the solver."""
        return self._name

    @property
    def id(self):
        """Return the solver ID."""
        return self._id

    @property
    def version(self):
        """Return the solver version."""
        return self._version

    @property
    def alias(self):
        """Return a list of aliases for the solver."""
        return self._alias

    @property
    def cmd(self):
        """Return the base command line of the solver."""
        return ' '.join(self._command_line)

    def set_time_limit(self, time_limit: int | None):
        """
        Set the time limit (timeout) for the solver.

        Args:
            time_limit (int | None): Time limit in seconds, or None for unlimited.
        """
        if time_limit is not None:
            placeholder_time = self._options["time"]
            self._args.append(placeholder_time.replace("{{value}}", str(time_limit)))
            self._time_limit = time_limit

    def set_seed(self, seed: int | None):
        """
        Set the random seed for the solver.

        Args:
            seed (int | None): Random seed value.
        """
        if seed is not None:
            placeholder_seed = self._options["seed"]
            self._args.append(placeholder_seed.replace("{{value}}", str(seed)))

    def all_solutions(self, activate: bool):
        """
        Enable or disable collecting all solutions found by the solver.

        Args:
            activate (bool): True to collect all solutions.
        """
        if activate:
            self._args.append(self._options["all_solutions"])

    def set_limit_number_of_solutions(self, limit: int | None):
        """
        Set the maximum number of solutions to retrieve.

        Args:
            limit (int | None): Maximum number of solutions, or None for unlimited.
        """
        if limit is not None and limit > 0:
            placeholder_limit = self._options["number_of_solutions"]
            self._args.append(placeholder_limit.replace("{{value}}", str(limit)))

    def set_collect_intermediate_solutions(self, activate: bool):
        """
        Enable or disable collecting intermediate assignments during search.

        Args:
            activate (bool): True to collect intermediate solutions.
        """
        if activate:
            self._print_intermediate_assignment = activate
            self._args.append(self._options["print_intermediate_assignment"])

    def add_complementary_options(self, options):
        """
        Add additional command-line options manually.

        Args:
            options (list): List of additional options to append.
        """
        self._args.extend(options)

    def set_output(self, output):
        """
        Set where to redirect standard output (stdout).

        Args:
            output (str or Path): Either "stdout" or a file path.
        """
        self._stdout = open(output, "w") if output != "stdout" else sys.stdout

    def set_error(self, error):
        """
        Set where to redirect standard error output (stderr).

        Args:
            error (str or Path): Either "stderr" or a file path.
        """
        self._stderr = open(error, "w") if error != "stderr" else sys.stderr

    def set_prefix(self, prefix):
        """
        Set a prefix to prepend to each line of solver output.

        Args:
            prefix (str): Prefix string.
        """
        self._prefix = prefix

    def set_json_output(self, activate):
        """
        Enable or disable JSON output mode instead of live printing.

        Args:
            activate (bool): True to generate JSON output.
        """
        self._json_output = activate

    def objective_value(self):
        return self._solutions["bounds"][-1]["value"] if self._solutions is not None and self._solutions["bounds"] else None

    def status(self)->ResultStatusEnum:
        return self._solutions["status"] if self._solutions is not None and self._solutions["status"] else ResultStatusEnum.UNKNOWN

    def solve(self, instance_path, keep_solver_output=False):
        """
        Launch and monitor the solver on the given instance.

        Captures intermediate objectives and solutions,
        enforces a timeout, and returns parsed results.

        Args:
            instance_path (str | Path): Path to the XCSP3 instance file.
            keep_solver_output (bool): If True, solver stdout is printed live.

        Returns:
            dict: A dictionary summarizing the solver run including solutions, bounds, times.
        """
        command = self._command_line
        for index,elt in command:
            if elt=='{{instance}}':
                command[index] = elt.replace("{{instance}}", str(instance_path))
        command.extend(self._args)
        logger.info(f"Launching solver: {command}")

        logger.debug("Each elt of command line : " +' '.join([f"'{elt}'" for elt in command]))

        process = psutil.Popen(
            shlex.split(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        wall_start = time.time()
        cpu_start = psutil.cpu_times()

        bounds = []
        assignments = []
        status = ResultStatusEnum.UNKNOWN

        try:
            for line in process.stdout:
                line = line.rstrip()

                current_wall = time.time()
                current_cpu = psutil.cpu_times()
                wall_clock_time = current_wall - wall_start
                cpu_time = (current_cpu.user - cpu_start.user) + (current_cpu.system - cpu_start.system)

                if line.startswith(ANSWER_PREFIX):
                    tokens = line.split()
                    if len(tokens) > 1:
                        status = ResultStatusEnum[tokens[1].replace(" ", "_")]

                elif line.startswith(OBJECTIVE_PREFIX):
                    tokens = line.split()
                    if len(tokens) > 1:
                        try:
                            value = int(tokens[1])
                            bounds.append({"value": value, "wall_clock_time": wall_clock_time, "cpu_time": cpu_time})
                            if not self._json_output:
                                print(f"o {value}")
                        except ValueError:
                            pass

                elif line.startswith(SOLUTION_PREFIX):
                    assign = line[2:].strip()
                    assignments.append({"solution": assign, "wall_clock_time": wall_clock_time, "cpu_time": cpu_time})
                    if self._print_intermediate_assignment and not self._json_output:
                        print(f"v {assign}", file=sys.stdout)

                if keep_solver_output:
                    if self._prefix:
                        print(f"{self._prefix} {line}", file=self._stdout)
                    else:
                        print(line, file=self._stdout)

            if keep_solver_output:
                for line in process.stderr:
                    line = line.rstrip()
                    print(line, file=self._stderr)

            process.wait()

        except Exception as e:
            logger.exception("An error occurred during solver execution")
            process.kill()
            raise e

        wall_end = time.time()
        cpu_end = psutil.cpu_times()

        final_wall_clock_time = wall_end - wall_start
        final_cpu_time = (cpu_end.user - cpu_start.user) + (cpu_end.system - cpu_start.system)

        self._solutions = {
            "status": status,
            "bounds": bounds,
            "assignments": assignments,
            "wall_clock_time": final_wall_clock_time,
            "cpu_time": final_cpu_time
        }

        if self._json_output:
            print(json.dumps(self._solutions, indent=2, cls=CustomEncoder))
        else:
            print(f"s {status.value}")
        if process.returncode != 0:
            logger.error(f"An error occurred during solver execution. Solver exit with code {process.returncode}")
            status = ResultStatusEnum.ERROR
        else:
            logger.info(
                f"Resolution completed successfully. Wall-clock time: {final_wall_clock_time:.2f}s | CPU time: {final_cpu_time:.2f}s")

        self._print_final_summary(status, bounds, assignments, final_wall_clock_time, final_cpu_time)
        return self._solutions

    @staticmethod
    def lookup(name: str) -> 'Solver':
        """
        Retrieve a Solver instance by name and optional version.

        Args:
            name (str): Name or name@version of the solver.

        Returns:
            Solver: The corresponding solver instance.

        Raises:
            ValueError: If the solver is not found.
        """
        name_solver = name
        version_solver = 'latest'
        if '@' in name:
            split = name.split('@')
            name_solver = split[0]
            version_solver = split[1]
        solvers = Solver.available_solvers()
        alias_solvers = dict()
        for k, v in solvers.items():
            for a in v.alias:
                alias_solvers[f"{v.name}@{a}"] = v
        logger.debug(solvers)
        logger.debug(alias_solvers)
        key = f"{name_solver.upper()}@{version_solver}"
        if key not in solvers and key not in alias_solvers:
            raise ValueError(
                f"Impossible to found an installed solver with the name {name_solver} and the version {version_solver}")

        return solvers.get(key, alias_solvers.get(key))

    @staticmethod
    def available_solvers() -> Dict[str, 'Solver']:
        """
        Retrieve all available solvers installed in the system.

        Returns:
            dict: Mapping of name@version to Solver instances.
        """
        solvers = dict()
        for k, s in CACHE.items():
            for vv in s["versions"].keys():
                solvers[f"{s['name_solver']}@{vv}"] = (
                    Solver(s["name_solver"], s["id_solver"], vv, s["versions"][vv]['cmd'],
                           s["versions"][vv]['options'], s["versions"][vv].get('alias')))
        return solvers

    @staticmethod
    def create_from_cli(args):
        """
        Create and configure a Solver instance based on parsed CLI arguments.

        Args:
            args (dict): CLI arguments parsed with argparse or similar.

        Returns:
            Solver: Configured Solver instance.
        """

        name = args.get("name").upper()
        version = args.get("solver_version")
        if "@" not in name and version is not None:
            name = f"{name}@{version}"
        s = Solver.lookup(name)
        s.set_seed(args.get("seed"))
        s.set_time_limit(args.get("timeout"))
        s.set_collect_intermediate_solutions(args.get("intermediate"))
        s.set_limit_number_of_solutions(args.get("num_solutions"))

        stdout = 'stdout' if args.get("stdout") == 'stdout' else Path(args.get('tmp_dir')) / args.get("stdout")
        stderr = 'stderr' if args.get("stderr") == 'stderr' else Path(args.get('tmp_dir')) / args.get("stderr")

        s.set_output(stdout)
        s.set_error(stderr)
        s.set_prefix(args.get("prefix"))
        s.set_json_output(args.get("json_output"))
        s.all_solutions(args.get("all_solutions"))
        s.add_complementary_options(args.get('solver_options',list()))
        return s

    def _print_final_summary(self, status, bounds, assignments, final_wall_clock_time, final_cpu_time):
        """
        Print a final human-readable summary of the solver execution.

        Args:
            status (ResultStatusEnum): Final solver status.
            bounds (list): List of objective values encountered.
            assignments (list): List of intermediate or final solutions.
            final_wall_clock_time (float): Total wall-clock time in seconds.
            final_cpu_time (float): Total CPU time in seconds.
        """
        nb_solutions = max(len(assignments), len(bounds))
        nb_bounds = len(bounds)
        best_objective = None
        if nb_bounds > 0:
            best_objective = bounds[-1]["value"]

        emoji = "❓"
        status_upper = status.value.upper()

        if "SATISFIABLE" == status_upper:
            emoji = "✅"
        elif "UNSATISFIABLE" == status_upper:
            emoji = "🔺"
        elif "UNKNOWN" == status_upper:
            emoji = "❓"
        elif "OPTIMUM" == status_upper:
            emoji = "🏆"
        elif "ERROR" == status_upper:
            emoji = "❌"
        elif "TIMEOUT" == status_upper:
            emoji = "⌛"
        else:
            emoji = "⚡"

        summary_parts = [
            f"{emoji} {status.value}",
            f"{nb_solutions} solutions" if nb_solutions > 0 else "No solutions",
        ]

        if best_objective is not None:
            summary_parts.append(f"Best objective: {best_objective}")

        summary_parts.append(f"Wall: {final_wall_clock_time:.2f}s")
        summary_parts.append(f"CPU: {final_cpu_time:.2f}s")

        logger.info(" | ".join(summary_parts))
