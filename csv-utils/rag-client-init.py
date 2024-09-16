import os
from graphrag.index.cli import index_cli


class RagClientInit:
    def __init__(self, root, config, output):
        self.root = root
        self.config = config
        self.output = output

    def create_input_folder(self):
        input_folder = os.path.join(self.root, "input")
        os.makedirs(input_folder, exist_ok=True)

    def initialize_graphrag(self):
        if os.path.exists(self.root):
            print(f"文件夹 {self.root} 已经存在")
        else:
            print(f"文件夹 {self.root} 不存在，将创建文件夹")
            index_cli(
                root=self.root,
                init=True,
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
            self.create_input_folder()

    def prompt_tune_graphrag(self):
        # python -m graphrag.prompt_tune --root ./graphrag-files --config ./graphrag-files/settings.yaml --no-entity-types
        pass

    def initialize_index(self):
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


if __name__ == "__main__":

    root_path = "./graphrag-files"
    config_path = "./graphrag-files/settings.yaml"
    output_path = "./graphrag-files/prompts"

    client = RagClientInit(root_path, config_path, output_path)
    client.initialize_graphrag()
    # client.initialize_index()
