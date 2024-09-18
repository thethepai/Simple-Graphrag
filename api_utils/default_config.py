# model
API_KEY = "your key example"
LLM_MODEL = "glm-4"
EMBEDDING_MODEL = "embedding-3"
API_BASE = "https://open.bigmodel.cn/api/paas/v4/"

# parquet files
OUTPUT_DATE = "20240917-211927"
INPUT_DIR = f"./ragtest/output/{OUTPUT_DATE}/artifacts"
COMMUNITY_REPORT_TABLE = "create_final_community_reports"
ENTITY_TABLE = "create_final_nodes"
ENTITY_EMBEDDING_TABLE = "create_final_entities"
RELATIONSHIP_TABLE = "create_final_relationships"
COVARIATE_TABLE = "create_final_covariates"
TEXT_UNIT_TABLE = "create_final_text_units"
COMMUNITY_LEVEL = 2

LANCEDB_URI = f"{INPUT_DIR}/lancedb"

# index
ROOT_DIR = "./ragtest"
CONFIG_FILE_PATH = "./ragtest/settings.yaml"
OUTPUT_DIR = "./ragtest/prompts"