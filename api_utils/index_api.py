import subprocess
from threading import Lock
from typing import Optional
from pydantic import BaseModel

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
        command = [
            "poetry",
            "run",
            "poe",
            "index",
            "--init" if request.init else "",
            "--root",
            request.root,
        ]
        command = [arg for arg in command if arg]  # Remove empty strings
        result = subprocess.run(command, capture_output=True, text=True)
        if not result.stderr:
            result.stderr = "none"
        return result.stdout, result.stderr

    def run_indexing_command(self, request: IndexingRequest):
        command = [
            "poetry",
            "run",
            "poe",
            "index",
            "--init" if request.init else "",
            "--root",
            request.root,
            "--config",
            request.config_filepath,
            "--resume",
            request.resume,
            "--emit",
            request.emit,
        ]
        command = [arg for arg in command if arg]  # Remove empty strings
        result = subprocess.run(command, capture_output=True, text=True)
        if not result.stderr:
            result.stderr = "none"
        return result.stdout, result.stderr

    def run_prompt_tune_command_default(self, request: PromptTuneRequest):
        command = [
            "poetry",
            "run",
            "poe",
            "prompt_tune",
            "--root",
            request.root,
            "--config",
            request.config,
            "--output",
            request.output,
            "--no-entity-types" if request.no_entity_types else "",
        ]
        command = [arg for arg in command if arg]  # Remove empty strings
        result = subprocess.run(command, capture_output=True, text=True)
        if not result.stderr:
            result.stderr = "none"
        return result.stdout, result.stderr

    def run_prompt_tune_command(self, request: PromptTuneRequest):
        command = [
            "poetry",
            "run",
            "poe",
            "prompt_tune",
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
        result = subprocess.run(command, capture_output=True, text=True)
        if not result.stderr:
            result.stderr = "none"
        return result.stdout, result.stderr


# Example usage
if __name__ == "__main__":
    requestIndex = IndexingRequest(init=False)
    runner = CommandRunner()
    stdout, stderr = runner.run_indexing_command_default(requestIndex)
    print("STDOUT:", stdout)
    print("STDERR:", stderr)

    # requestPromptTune = PromptTuneRequest()
    # stdout, stderr = runner.run_prompt_tune_command(requestPromptTune)
    # print("STDOUT:", stdout)
    # print("STDERR:", stderr)
