import subprocess
from threading import Lock
from typing import Optional
from pydantic import BaseModel

class IndexingRequest(BaseModel):
    root: str
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
    root: str
    domain: Optional[str] = None
    method: str = "random"
    limit: int = 15
    language: Optional[str] = None
    max_tokens: int = 2048
    chunk_size: int = 256
    no_entity_types: bool = False
    output: str

class CommandRunner:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(CommandRunner, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def run_indexing_command(self, request: IndexingRequest):
        command = [
            "poetry", "run", "poe", "index",
            "--init" if request.init else "",
            "--root", request.root
        ]
        command = [arg for arg in command if arg]  # Remove empty strings
        result = subprocess.run(command, capture_output=True, text=True)
        return result.stdout, result.stderr

# Example usage
if __name__ == "__main__":
    request = IndexingRequest(root="./ragtest")
    runner = CommandRunner()
    stdout, stderr = runner.run_indexing_command(request)
    print("STDOUT:", stdout)
    print("STDERR:", stderr)