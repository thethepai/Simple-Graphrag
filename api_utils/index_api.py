import subprocess
from threading import Lock
from typing import Optional
from pydantic import BaseModel
import asyncio
import os
import sys
from graphrag.index.cli import index_cli

index_cli(
    root=self.root,
    init=False,
    verbose=False,
    resume=None,
    update_index_id=False,
    memprofile=False,
    nocache=False,
    reporter=None,
    config_filepath=None,
    emit=None,
    dryrun=False,
    skip_validations=False,
)

# config
from api_utils.default_config import (
    ROOT_DIR,
    CONFIG_FILE_PATH,
    OUTPUT_DIR,
)


class IndexingRequest(BaseModel):
    root: str = ROOT_DIR
    init: bool = True
    verbose: bool = False
    resume: Optional[str] = None
    update_index_id: Optional[str] = False
    memprofile: bool = False
    nocache: bool = False
    reporter: Optional[str] = None
    config_filepath: Optional[str] = None
    emit: Optional[str] = None
    dryrun: bool = False
    skip_validations: bool = False


class PromptTuneRequest(BaseModel):
    root: str = ROOT_DIR
    config: str = CONFIG_FILE_PATH
    domain: Optional[str] = None
    limit: int = 15
    language: Optional[str] = None
    max_tokens: int = 2048
    chunk_size: int = 256
    no_entity_types: bool = True
    output: str = OUTPUT_DIR


class CommandRunner:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(CommandRunner, cls).__new__(
                        cls, *args, **kwargs
                    )
        return cls._instance

    @classmethod
    def destroy_instance(cls):
        with cls._lock:
            cls._instance = None

    def run_indexing_command_default(self, request: IndexingRequest):
        index_cli(
            root=request.root,
            init=request.init,
            verbose=False,
            resume=None,
            update_index_id=False,
            memprofile=False,
            nocache=False,
            reporter=None,
            config_filepath=None,
            emit=None,
            dryrun=False,
            skip_validations=False,
        )

    def run_indexing_command(self, request: IndexingRequest):
        command = [
            "python",
            "-m",
            "graphrag.index",
            "--init" if request.init else "",
            "--root",
            request.root,
            "--config" if request.config_filepath else "",
            "--resume" if request.resume else "",
            "--emit" if request.emit else "",
        ]
        command = [arg for arg in command if arg]  # Remove empty strings

        # env
        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join(sys.path)

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
        )
        if not result.stderr:
            result.stderr = "none"
        return result.stdout, result.stderr

    def run_prompt_tune_command_default(self, request: PromptTuneRequest):
        command = [
            "python",
            "-m",
            "graphrag.prompt_tune",
            "--root",
            request.root,
            "--config",
            request.config,
            "--output",
            request.output,
            "--no-entity-types" if request.no_entity_types else "",
        ]
        command = [arg for arg in command if arg]  # Remove empty strings

        # env
        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join(sys.path)

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
        )
        if not result.stderr:
            result.stderr = "none"
        return result.stdout, result.stderr

    def run_prompt_tune_command(self, request: PromptTuneRequest):
        command = [
            "python",
            "-m",
            "graphrag.prompt_tune",
            "--root",
            request.root,
            "--config",
            request.config,
            "--domain" if request.domain else "",
            "--limit",
            str(request.limit),
            "--language" if request.language else "",
            "--max-tokens",
            str(request.max_tokens),
            "--chunk-size",
            str(request.chunk_size),
            "--no-entity-types" if request.no_entity_types else "",
            "--output",
            request.output,
        ]
        command = [arg for arg in command if arg]  # Remove empty strings

        # env
        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join(sys.path)

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
        )
        if not result.stderr:
            result.stderr = "none"
        return result.stdout, result.stderr


# Example usage
if __name__ == "__main__":

    def index_test():
        requestIndex = IndexingRequest(init=False)
        runner = CommandRunner()
        stdout, stderr = runner.run_indexing_command_default(requestIndex)
        print(stdout)
        print(stderr)

    def prompt_test():
        requestPromptTune = PromptTuneRequest()
        runner = CommandRunner()
        stdout, stderr = runner.run_prompt_tune_command(requestPromptTune)
        print(stdout)
        print(stderr)

    index_test()
    # prompt_test()
