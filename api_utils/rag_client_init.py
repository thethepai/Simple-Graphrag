import os
import asyncio
from threading import Lock
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
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(RagClientInit, cls).__new__(
                        cls, *args, **kwargs
                    )
        return cls._instance

    def __init__(self):
        self.runner = CommandRunner()

    @classmethod
    def destroy_instance(cls):
        with cls._lock:
            cls._instance = None

    def initialize_indexing(self, request_index: IndexingRequest = IndexingRequest()):
        if not os.path.exists(request_index.root):
            os.makedirs(request_index.root)
            print(f"创建了:{request_index.root}文件夹")
        else:
            print(f"文件夹:{request_index.root}已存在，你是否已经运行过初始化了？")
            return

        if os.path.exists(request_index.root):
            input_folder = os.path.join(request_index.root, "input")
            if not os.path.exists(input_folder):
                os.makedirs(input_folder)
                print(f"创建了{input_folder}文件夹")

        self.runner.run_indexing_command_default(request_index)

    def initialize_prompt_tune(
        self, request_prompt_tune: PromptTuneRequest = PromptTuneRequest()
    ):
        self.runner.run_prompt_tune_command_default(request_prompt_tune)

    def initialize_config(
        self,
        user_config_path,
        env_config_path,
        yaml_config_path,
    ):
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
        self,
        user_config_path,
        root_dir=f"{ROOT_DIR}",
        choice=-1,
    ) -> Tuple[GlobalSearchRequest, LocalSearchRequest]:
        env_manager = DotenvManager(user_config_path)
        config = env_manager.read_env()
        graphrag_api_key = config.get("GRAPHRAG_API_KEY", None)

        directories = []
        output_dir = f"{root_dir}/output"
        directories = [
            os.path.join(output_dir, name, "artifacts")
            for name in os.listdir(output_dir)
            if os.path.isdir(os.path.join(output_dir, name))
        ]
        print("Directories found:", directories)

        if directories:
            query_input_dir = directories[choice]
        else:
            print("No directories found")
        # TODO: Add more directories options
        print(f"Using input_dir: {query_input_dir}")
        return GlobalSearchRequest(
            api_key=graphrag_api_key,
            input_dir=query_input_dir,
        ), LocalSearchRequest(
            api_key=graphrag_api_key,
            input_dir=query_input_dir,
        )


# TODO: Asynchronous version
# This is a template for initializing the pipeline
class InitPipeline:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(InitPipeline, cls).__new__(
                        cls, *args, **kwargs
                    )
        return cls._instance

    def __init__(self):
        self.client = RagClientInit()
        self.root_dir = ROOT_DIR
        self._query_engines_instance = None
        self._config_engines_instance = None

    def default_init(self):
        request_index = IndexingRequest(root=self.root_dir)
        self.client.initialize_indexing(request_index)

    def default_start_index(self):
        request_index = IndexingRequest(root=self.root_dir, init=False)
        self.client.initialize_indexing(request_index)

    def default_config(self):
        user_config_path = ".env"
        env_config_path = f"{self.root_dir}/.env"
        yaml_config_path = f"{self.root_dir}/settings.yaml"
        self.client.initialize_config(
            user_config_path, env_config_path, yaml_config_path
        )

    def default_prompt_tune(self):
        request_prompt_tune = self.client.get_config_for_prompt_tune(".env")
        self.client.initialize_prompt_tune(request_prompt_tune)

    def get_config_engines(self) -> Tuple[
        YamlManager,
        DotenvManager,
        ConfigOperator,
    ]:
        if self._config_engines_instance is None:
            yaml_manager = YamlManager(f"{self.root_dir}/settings.yaml")
            dotenv_manager = DotenvManager(".env")
            config_operator = ConfigOperator(
                ".env",
                f"{self.root_dir}/.env",
                f"{self.root_dir}/settings.yaml",
            )
            self._config_engines_instance = (
                yaml_manager,
                dotenv_manager,
                config_operator,
            )
        return self._config_engines_instance

    def get_query_engines(self) -> Tuple[GlobalSearchEngine, LocalSearchEngine]:
        if self._query_engines_instance is None:
            global_request, local_request = self.client.get_config_for_query(
                ".env",
                self.root_dir,
            )
            global_engine = GlobalSearchEngine(global_request)
            local_engine = LocalSearchEngine(local_request)
            self._query_engines_instance = (global_engine, local_engine)
        return self._query_engines_instance

    @classmethod
    def reset_query_engines(self):
        self._query_engines_instance = None

    @classmethod
    def reset_config_engines(self):
        self._config_engines_instance = None


if __name__ == "__main__":
    pipeline = InitPipeline()
    pipeline.default_init()
    pipeline.default_config()
    # pipeline.default_start_index()
    # pipeline.default_prompt_tune()

    # global_engine, local_engine = pipeline.get_query_engines()

    # asyncio.run(global_engine.run_search("介绍一下网络空间安全课程"))

    print("Done")
