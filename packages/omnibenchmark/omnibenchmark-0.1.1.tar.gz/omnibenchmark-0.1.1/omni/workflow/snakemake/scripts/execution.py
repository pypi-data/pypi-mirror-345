import logging
import os
import subprocess
from pathlib import Path
from typing import List

import configparser

from snakemake.script import Snakemake


def mock_execution(inputs: List[str], output: str, snakemake: Snakemake):
    print("Processed", inputs, "to", output, "using threads", snakemake.threads)
    print("  bench_iteration is", snakemake.bench_iteration)
    print("  resources are", snakemake.resources)
    print("  wildcards are", snakemake.wildcards)
    print("  rule is", snakemake.rule)
    print("  scriptdir is", snakemake.scriptdir)
    print("  params are", snakemake.params)


def execution(
    module_dir: Path,
    module_name: str,
    output_dir: Path,
    dataset: str,
    inputs_map: dict[str, str],
    parameters: List[str],
    keep_module_logs: bool,
) -> int:
    config_parser = _read_config(module_dir, module_name)

    executable = config_parser["DEFAULT"]["SCRIPT"]
    executable_path = module_dir / executable
    if not os.path.exists(executable_path):
        logging.error(f"ERROR: {module_name} executable does not exist.")
        raise RuntimeError(f"{module_name} executable does not exist")

    # Constructing the command
    command = _create_command(executable_path)

    # Add output directory and dataset name to command
    command.extend(["--output_dir", output_dir.as_posix(), "--name", dataset])

    # Adding input files with their respective keys
    if inputs_map:
        for k, v in inputs_map.items():
            command.extend([f"--{k}", Path(v).as_posix()])

    # Adding extra parameters
    if parameters:
        command.extend(parameters)

    # Prepare stdout and stderr files in the output directory
    stdout_file = output_dir / "stdout.log"
    stderr_file = output_dir / "stderr.log"

    try:
        with open(stdout_file, "w") as stdout_f, open(stderr_file, "w") as stderr_f:
            result = subprocess.run(
                command,
                check=True,
                stdout=stdout_f,
                stderr=stderr_f,
                text=True,
            )

            return result.returncode

    except subprocess.CalledProcessError as e:
        logging.error(
            f"ERROR: Executing {executable} failed with exit code {e.returncode}: {e.stdout} {e.stderr} {e.output}"
            f"See {stderr_file} for details."
        )
        raise RuntimeError(
            f"ERROR: Executing {executable} failed with exit code {e.returncode}: {e.stdout} {e.stderr} {e.output}"
            f"See {stderr_file} for details."
        ) from e

    finally:
        # Cleanup empty log files / always cleanup stdout_file if keep_module_logs is False
        if stdout_file.exists() and (
            os.path.getsize(stdout_file) == 0 or not keep_module_logs
        ):
            stdout_file.unlink()
        if stderr_file.exists() and os.path.getsize(stderr_file) == 0:
            stderr_file.unlink()


def _read_config(module_dir: Path, module_name: str) -> configparser.ConfigParser:
    config_path = module_dir / "config.cfg"
    if not os.path.exists(config_path):
        logging.error(f"ERROR: {module_name} config.cfg does not exist.")
        raise RuntimeError(f"{module_name} config.cfg does not exist")

    parser = configparser.ConfigParser()

    # Read the configuration file
    parser.read(config_path)

    return parser


def _create_command(executable_path: Path) -> list[str]:
    _, extension = os.path.splitext(executable_path)

    if extension == ".py":
        # Execute Python script
        return ["python3", executable_path.as_posix()]
    elif extension == ".R":
        # Execute R script
        return ["Rscript", executable_path.as_posix()]
    elif extension == ".sh":
        # Execute shell script
        return ["sh", executable_path.as_posix()]
    else:
        logging.error(
            f"ERROR: Unsupported script extension: {extension}. Only Python/R/Shell scripts are supported."
        )
        raise RuntimeError(
            f"Unsupported script extension: {extension}. Only Python/R/Shell scripts are supported."
        )
