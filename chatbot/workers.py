"""
This file is here to maintain
retrocompatibility with Lend's Default
Project Boilerplate
"""

import argparse
import glob
import importlib.util
import logging
from pathlib import Path
from types import ModuleType

_JOBS_FOLDER = Path(__file__).parent / "infra" / "workers"


def load_job(name: str, filepath: str) -> ModuleType:
    """Dynamically load a worker module from filepath.

    Args:
        name: Module name
        filepath: Path to the Python file

    Returns:
        Loaded module

    Raises:
        ImportError: If module cannot be loaded
    """
    spec = importlib.util.spec_from_file_location(name, filepath)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module {name} from {filepath}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_job_filepaths() -> dict[str, str]:
    job_paths = glob.glob(f"{_JOBS_FOLDER}/[!_]*.py")
    return {Path(filepath).stem: filepath for filepath in job_paths}


def parse_args(worker_choices: list[str]) -> dict[str, str]:
    parser = argparse.ArgumentParser()
    parser.add_argument("-worker", required=True, choices=worker_choices)
    return vars(parser.parse_args())


def run_worker(job: ModuleType, worker_name: str) -> None:
    """Run a worker module.

    Args:
        job: Loaded worker module with process() method
        worker_name: Name of the worker for instrumentation
    """
    # configure_worker_cronjob_instrumentation(service_name=worker_name)
    job.process()  # type: ignore[attr-defined]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    jobs = get_job_filepaths()
    args = parse_args(list(jobs.keys()))
    worker_job = load_job(args["worker"], jobs[args["worker"]])
    run_worker(worker_job, args["worker"])
