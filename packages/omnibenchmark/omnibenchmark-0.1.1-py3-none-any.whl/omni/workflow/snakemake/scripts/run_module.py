#! /usr/bin/env python
# WARNING: Custom dependencies might not be available here, since this is run inside a specified environment.

import hashlib
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List

from snakemake.script import Snakemake
from filelock import FileLock

from omni.workflow.snakemake.scripts.execution import execution


# Create a unique folder name based on the repository URL and commit hash
def generate_unique_repo_folder_name(repo_url, commit_hash):
    unique_string = f"{repo_url}@{commit_hash}"
    folder_name = hashlib.md5(unique_string.encode()).hexdigest()

    return folder_name


def clone_module(output_dir: Path, repository_url: str, commit_hash: str) -> Path:
    try:
        import git  # Check if gitpython is available
    except ImportError:
        logging.info("gitpython is not installed. Installing now...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "gitpython==3.1.43"]
        )
        import git  # Retry importing

    module_name = generate_unique_repo_folder_name(repository_url, commit_hash)
    module_dir = output_dir / module_name

    def clone():
        logging.info(
            f"Cloning module `{repository_url}:{commit_hash}` to `{module_dir.as_posix()}`"
        )
        repo = git.Repo.clone_from(repository_url, module_dir.as_posix())
        repo.git.checkout(commit_hash)

        return repo

    lock = module_dir.with_suffix(".lock")
    with FileLock(lock):
        if not module_dir.exists():
            repo = clone()
        else:
            repo = git.Repo(module_dir.as_posix())
            if repo.bare:
                logging.warning(
                    f"Removing incomplete repo {module_dir} and retrying..."
                )
                shutil.rmtree(module_dir)
                repo = clone()

        if repo.head.commit.hexsha[:7] != commit_hash:
            logging.error(
                f"ERROR: Failed while cloning module `{repository_url}:{commit_hash}`"
            )
            logging.error(
                f"{commit_hash} does not match {repo.head.commit.hexsha[:7]}`"
            )
            raise RuntimeError(
                f"ERROR: {commit_hash} does not match {repo.head.commit.hexsha[:7]}"
            )

    return module_dir


def dump_parameters_to_file(output_dir: str, parameters: List[str]):
    os.makedirs(output_dir, exist_ok=True)

    if parameters is not None:
        params_file = os.path.join(output_dir, "parameters.txt")
        with open(params_file, "w") as params_file:
            params_file.write(f"{parameters}")

        param_dict_file = os.path.join(output_dir, "..", "parameters_dict.txt")
        with open(param_dict_file, "a") as param_dict_file:
            param_dict_file.write(f"{os.path.basename(output_dir)} {parameters}\n")


try:
    snakemake: Snakemake = snakemake
    params = dict(snakemake.params)

    parameters = params["parameters"]
    repository_url = params["repository_url"]
    commit_hash = params["commit_hash"]
    inputs_map = params.get("inputs_map")
    dataset = params.get("dataset")
    if dataset is None:
        dataset = getattr(snakemake.wildcards, "dataset", "unknown")

    keep_module_logs = params.get("keep_module_logs", False)

    # Create parameters file for outputs
    output_dir = os.path.dirname(snakemake.output[0])
    dump_parameters_to_file(output_dir, parameters)

    # Clone github repository
    repositories_dir = Path(".snakemake") / "repos"
    module_dir = clone_module(repositories_dir, repository_url, commit_hash)

    # Execute module code
    module_name = snakemake.rule

    output_dir = Path(str(os.path.commonpath(snakemake.output)))
    if len(snakemake.output) == 1:
        output_dir = Path(os.path.dirname(output_dir))

    execution(
        module_dir,
        module_name=module_name,
        output_dir=output_dir,
        dataset=dataset,
        inputs_map=inputs_map,
        parameters=parameters,
        keep_module_logs=keep_module_logs,
    )

except NameError:
    raise RuntimeError(f"This script must be run from within a Snakemake workflow")
