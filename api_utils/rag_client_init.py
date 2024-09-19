import os
import asyncio
from typing import Tuple
from api_utils.index_api import (
    CommandRunner,
    IndexingRequest,
    PromptTuneRequest,
)
from api_utils.config import (
    YamlManager,
    DotenvManager,
    ConfigOperator,
)
from api_utils.query_api import (
    GlobalSearchEngine,
    LocalSearchEngine,
    GlobalSearchRequest,
    LocalSearchRequest,
)
from api_utils.default_config import ROOT_DIR


class RagClientInit:
    def __init__(self):
        self.runner = CommandRunner()

    def initialize_indexing(self, request_index):
        if not os.path.exists(request_index.root):
            os.makedirs(request_index.root)
            print(f"创建了:{request_index.root}文件夹")

        self.runner.run_indexing_command_default(request_index)

        if os.path.exists(request_index.root):
            input_folder = os.path.join(request_index.root, "input")
            if not os.path.exists(input_folder):
                os.makedirs(input_folder)
                print(f"创建了{input_folder}文件夹")

        return request_index.root

    def initialize_prompt_tune(self, request_prompt_tune):
        stdout, stderr = self.runner.run_prompt_tune_command(request_prompt_tune)
        print("STDOUT:", stdout)
        print("STDERR:", stderr)

    def initialize_config(self, user_config_path, env_config_path, yaml_config_path):
        config_operator = ConfigOperator(
            user_config_path, env_config_path, yaml_config_path
        )
        config_operator.initialize_config()

    def get_config_for_indexing(self, user_config_path) -> IndexingRequest:
        env_manager = DotenvManager(user_config_path)
        config = env_manager.read_env()
        # TODO: Add more config options
        return IndexingRequest()

    def get_config_for_prompt_tune(self, user_config_path) -> PromptTuneRequest:
        env_manager = DotenvManager(user_config_path)
        config = env_manager.read_env()
        # TODO: Add more config options
        return PromptTuneRequest()

    def get_config_for_query(
        self, user_config_path, root_dir=f"{ROOT_DIR}"
    ) -> Tuple[GlobalSearchRequest, LocalSearchRequest]:
        env_manager = DotenvManager(user_config_path)
        config = env_manager.read_env()
        graphrag_api_key = config.get("GRAPHRAG_API_KEY", None)

        directories = []
        output_dir = f"{root_dir}/output"
        for dirpath, dirnames, filenames in os.walk(output_dir):
            for dirname in dirnames:
                directories.append(os.path.join(dirpath, dirname, "artifacts"))

        input_dir = directories[0]
        # TODO: Add more directories options
        print(f"Using input_dir: {input_dir}")
        return GlobalSearchRequest(
            api_key=graphrag_api_key,
            input_dir=input_dir,
        ), LocalSearchRequest(
            api_key=graphrag_api_key,
            input_dir=input_dir,
        )


# This is a template for initializing the pipeline
class InitPipeline:
    client = RagClientInit()
    root_dir = "./ragtest"

    @classmethod
    def default_init(cls):
        request_index = IndexingRequest(root=cls.root_dir)
        cls.client.initialize_indexing(request_index)

    @classmethod
    def default_start_index(cls):
        request_index = IndexingRequest(root=cls.root_dir, init=False)
        cls.client.initialize_indexing(request_index)

    @classmethod
    def default_config(cls):
        user_config_path = ".env"
        env_config_path = f"{cls.root_dir}/.env"
        yaml_config_path = f"{cls.root_dir}/settings.yaml"
        cls.client.initialize_config(
            user_config_path, env_config_path, yaml_config_path
        )

    @classmethod
    def default_prompt_tune(cls):
        request_prompt_tune = cls.client.get_config_for_prompt_tune(".env")
        cls.client.initialize_prompt_tune(request_prompt_tune)

    @classmethod
    def get_query_engines(cls) -> Tuple[GlobalSearchEngine, LocalSearchEngine]:
        global_request, local_request = cls.client.get_config_for_query(
            ".env",
            cls.root_dir,
        )
        global_engine = GlobalSearchEngine(global_request)
        local_engine = LocalSearchEngine(local_request)
        return global_engine, local_engine


if __name__ == "__main__":
    # InitPipeline.default_init()
    # InitPipeline.default_config()
    # InitPipeline.default_start_index()

    InitPipeline.default_prompt_tune()

    # global_engine, local_engine = InitPipeline.get_query_engines()

    # asyncio.run(global_engine.run_search("介绍一下网络空间安全课程"))

    print("Done")
