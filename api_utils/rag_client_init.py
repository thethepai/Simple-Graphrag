import os
from index_api import CommandRunner, IndexingRequest, PromptTuneRequest

class RagClientInit:
    def __init__(self):
        self.runner = CommandRunner()

    def initialize_indexing(self, request_index):
        stdout, stderr = self.runner.run_indexing_command_default(request_index)
        print("STDOUT:", stdout)
        print("STDERR:", stderr)

        if os.path.exists(request_index.root):
            print(f"创建了{request_index.root}文件夹")
            input_folder = os.path.join(request_index.root, "input")
            if not os.path.exists(input_folder):
                os.makedirs(input_folder)
                print(f"创建了{input_folder}文件夹")


    def initialize_prompt_tune(self, request_prompt_tune):
        stdout, stderr = self.runner.run_prompt_tune_command(request_prompt_tune)
        print("STDOUT:", stdout)
        print("STDERR:", stderr)

if __name__ == "__main__":
    request_index = IndexingRequest(root="./ragtest")
    request_prompt_tune = PromptTuneRequest(
        root="/path/to/project",
        config="/path/to/settings.yaml",
        domain="environmental news",
        method="random",
        limit=10,
        language="Chinese",
        max_tokens=2048,
        chunk_size=256,
        min_examples_required=3,
        no_entity_types=True,
        output="/path/to/output"
    )

    client = RagClientInit()
    # client.initialize_indexing(request_index)
    # client.initialize_prompt_tune(request_prompt_tune)

    