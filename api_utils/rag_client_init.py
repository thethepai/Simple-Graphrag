import os
from .index_api import CommandRunner, IndexingRequest, PromptTuneRequest
from .config import YamlManager, DotenvManager
from .query_api import GlobalSearchEngine, LocalSearchEngine


class RagClientInit:
    def __init__(self):
        self.runner = CommandRunner()

    def initialize_indexing(self, request_index):
        stdout, stderr = self.runner.run_indexing_command_default(request_index)
        print("STDOUT:", stdout)
        print("STDERR:", stderr)

        if os.path.exists(request_index.root):
            print(f"创建了{request_index.root}文件夹")
            # default folder name in graphrag
            input_folder = os.path.join(request_index.root, "input")
            if not os.path.exists(input_folder):
                os.makedirs(input_folder)
                print(f"创建了{input_folder}文件夹")

    def initialize_prompt_tune(self, request_prompt_tune):
        stdout, stderr = self.runner.run_prompt_tune_command(request_prompt_tune)
        print("STDOUT:", stdout)
        print("STDERR:", stderr)

    def initialize_config(self, user_config_path, env_config_path, yaml_config_path):
        env_manager = DotenvManager(user_config_path)
        yaml_manager = YamlManager(yaml_config_path)

        user_config = env_manager.read_env()
        yaml_config = yaml_manager.read_yaml()

        env_manager = DotenvManager(env_config_path)
        api_key = user_config.get("GRAPHRAG_API_KEY")
        api_key_config = {"GRAPHRAG_API_KEY": api_key}
        env_manager.write_env(api_key_config)

        yaml_config["embeddings"]["llm"]["api_base"] = user_config.get(
            "API_BASE", yaml_config["embeddings"]["llm"].get("api_base")
        )
        yaml_config["llm"]["api_base"] = user_config.get(
            "API_BASE", yaml_config["llm"].get("api_base")
        )
        yaml_config["llm"]["model"] = user_config.get(
            "MODEL_ID", yaml_config["llm"].get("model")
        )
        yaml_config["embeddings"]["llm"]["model"] = user_config.get(
            "EMBEDDING_MODEL_ID", yaml_config["embeddings"]["llm"].get("model")
        )

        if user_config.get("CLAIM_EXTRACTION") == "True":
            yaml_config["claim_extraction"]["enabled"] = True
        else:
            yaml_config["claim_extraction"]["enabled"] = False
        yaml_manager.write_yaml(yaml_config)

    def get_config_for_query(self, user_config_path):
        env_manager = DotenvManager(user_config_path)
        config = env_manager.read_env()
        graphrag_api_key = config.get("GRAPHRAG_API_KEY", None)
        
        
        return graphrag_api_key


class InitPipeline:
    client = RagClientInit()  # load instance once

    @classmethod
    def default_init(cls):
        request_index = IndexingRequest(root="./ragtest")
        cls.client.initialize_indexing(request_index)

    @classmethod
    def default_start_index(cls):
        request_index = IndexingRequest(root="./ragtest", init=False)
        cls.client.initialize_indexing(request_index)

    @classmethod
    def default_config(cls):
        user_config_path = ".env"
        env_config_path = "./ragtest/.env"
        yaml_config_path = "./ragtest/settings.yaml"
        cls.client.initialize_config(
            user_config_path, env_config_path, yaml_config_path
        )

    @classmethod
    def default_prompt_tune(cls):
        request_prompt_tune = PromptTuneRequest(
            # root="./ragtest",
            # config="./ragtest/settings.yaml",
            # domain="Cybersecurity Syllabus",
            # limit=15,
            # language="Chinese",
            # max_tokens=2048,
            # chunk_size=256,
            # no_entity_types=True,
            # output="./ragtest/prompts",
        )
        cls.client.initialize_prompt_tune(request_prompt_tune)


if __name__ == "__main__":
    # InitPipeline.default_init()
    # InitPipeline.default_config()
    # InitPipeline.default_prompt_tune()
    print("Done")
