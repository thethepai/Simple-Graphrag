import os
from dotenv import load_dotenv, set_key, unset_key
import yaml


class DotenvManager:
    def __init__(self, dotenv_path=".env"):
        self.dotenv_path = dotenv_path
        if not os.path.exists(self.dotenv_path):
            open(self.dotenv_path, "a").close()
            print("当前位置没有.env文件, 新创建了.env文件")
        load_dotenv(self.dotenv_path)

    def read_env(self):
        env_vars = {}
        with open(self.dotenv_path, "r") as file:
            for line in file:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    env_vars[key] = value
        return env_vars

    def write_env(self, new_vars):
        for key, value in new_vars.items():
            set_key(self.dotenv_path, key, value)

    def delete_env(self, keys):
        for key in keys:
            unset_key(self.dotenv_path, key)


class YamlManager:
    def __init__(self, yaml_path="settings.yaml"):
        self.yaml_path = yaml_path
        if not os.path.exists(self.yaml_path):
            with open(self.yaml_path, "w") as file:
                yaml.dump({}, file)
            print("当前位置没有配置文件, 新创建了配置文件")

    def read_yaml(self):
        with open(self.yaml_path, "r") as file:
            return yaml.safe_load(file)

    def write_yaml(self, data):
        with open(self.yaml_path, "w") as file:
            yaml.safe_dump(data, file)


def dot_test():
    dotenv_manager = DotenvManager(".env")
    # Reading .env file
    env_vars = dotenv_manager.read_env()
    print("Current .env variables:", env_vars)

    # Writing to .env file
    new_vars = {"NEW_KEY": "new_value", "ANOTHER_KEY": "another_value_new"}
    dotenv_manager.write_env(new_vars)
    # Deleting from .env file
    keys_to_delete = ["NEW_KEY"]
    dotenv_manager.delete_env(keys_to_delete)


def yaml_test():
    yaml_manager = YamlManager("./ragtest/settings.yaml")

    # Reading YAML file
    config = yaml_manager.read_yaml()
    print("Current YAML configuration:", config)

    # Modifying the 'model' field under 'llm'
    if "llm" in config:
        config["llm"]["model"] = "glm-4"
        config["llm"]["api_base"] = "your_api_base_value"
    if "embeddings" in config:
        config["embeddings"]["llm"]["model"] = "embedding-3"
        config["embeddings"]["llm"]["api_base"] = "your_api_base_value"
    if "claim_extraxtion" in config:
        config["claim_extraction"]["enabled"] = "true"

    # Writing the updated configuration back to the YAML file
    yaml_manager.write_yaml(config)
    print("Updated YAML configuration:", yaml_manager.read_yaml())


if __name__ == "__main__":
    # dot_test()
    yaml_test()
