
# general
import os
import asyncio

import pandas as pd
import tiktoken

# data
from typing import Optional
from pydantic import BaseModel

# graphrag
from graphrag.query.structured_search.global_search.community_context import (
    GlobalCommunityContext,
)
from graphrag.query.structured_search.global_search.search import GlobalSearch

from graphrag.query.context_builder.entity_extraction import EntityVectorStoreKey
from graphrag.query.indexer_adapters import (
    read_indexer_covariates,
    read_indexer_entities,
    read_indexer_relationships,
    read_indexer_reports,
    read_indexer_text_units,
)
from graphrag.query.input.loaders.dfs import (
    store_entity_semantic_embeddings,
)
from graphrag.query.llm.oai.chat_openai import ChatOpenAI
from graphrag.query.llm.oai.embedding import OpenAIEmbedding
from graphrag.query.llm.oai.typing import OpenaiApiType
from graphrag.query.question_gen.local_gen import LocalQuestionGen
from graphrag.query.structured_search.local_search.mixed_context import (
    LocalSearchMixedContext,
)
from graphrag.query.structured_search.local_search.search import LocalSearch
from graphrag.vector_stores.lancedb import LanceDBVectorStore

# model
API_KEY = "wow, such a long key"
LLM_MODEL = "glm-4"
EMBEDDING_MODEL = "embedding-3"
API_BASE = "https://open.bigmodel.cn/api/paas/v4/"

# parquet files generated from indexing pipeline
INPUT_DIR = "./ragtest/output/20240917-211927/artifacts"
COMMUNITY_REPORT_TABLE = "create_final_community_reports"
ENTITY_TABLE = "create_final_nodes"
ENTITY_EMBEDDING_TABLE = "create_final_entities"
RELATIONSHIP_TABLE = "create_final_relationships"
COVARIATE_TABLE = "create_final_covariates"
TEXT_UNIT_TABLE = "create_final_text_units"
COMMUNITY_LEVEL = 2

LANCEDB_URI = f"{INPUT_DIR}/lancedb"


class GlobalSearchRequest(BaseModel):
    api_key: str = API_KEY
    model: str = LLM_MODEL
    api_base: str = API_BASE
    input_dir: str = INPUT_DIR
    entity_table: str = ENTITY_TABLE
    community_report_table: str = COMMUNITY_REPORT_TABLE
    entity_embedding_table: str = ENTITY_EMBEDDING_TABLE
    community_level: int = COMMUNITY_LEVEL

class LocalSearchRequest(BaseModel):
    api_key: str = API_KEY
    model: str = LLM_MODEL
    embedding_model: str = EMBEDDING_MODEL
    api_base: str = API_BASE
    input_dir: str = INPUT_DIR
    lancedb_uri: str = LANCEDB_URI
    entity_table: str = ENTITY_TABLE
    community_report_table: str = COMMUNITY_REPORT_TABLE
    relationship_table: str = RELATIONSHIP_TABLE
    covariate_table: str = COVARIATE_TABLE
    entity_embedding_table: str = ENTITY_EMBEDDING_TABLE
    text_unit_table: str = TEXT_UNIT_TABLE
    community_level: int = COMMUNITY_LEVEL

class GlobalSearchEngine:
    def __init__(self, api_key, model, api_base, input_dir, entity_table, community_report_table, entity_embedding_table, community_level):
        self.llm = ChatOpenAI(
            api_key=api_key,
            model=model,
            api_base=api_base,
            api_type=OpenaiApiType.OpenAI,
            max_retries=20,
        )

        self.token_encoder = tiktoken.get_encoding("cl100k_base")

        entity_df = pd.read_parquet(f"{input_dir}/{entity_table}.parquet")
        report_df = pd.read_parquet(
            f"{input_dir}/{community_report_table}.parquet")
        entity_embedding_df = pd.read_parquet(
            f"{input_dir}/{entity_embedding_table}.parquet")

        reports = read_indexer_reports(
            report_df, entity_df, community_level)
        entities = read_indexer_entities(
            entity_df, entity_embedding_df, community_level)

        print(f"Total report count: {len(report_df)}")
        print(f"Report count after filtering by community level {
              community_level}: {len(reports)}")
        report_df.head()

        self.context_builder = GlobalCommunityContext(
            community_reports=reports,
            entities=entities,
            token_encoder=self.token_encoder,
        )

        self.context_builder_params = {
            "use_community_summary": False,
            "shuffle_data": True,
            "include_community_rank": True,
            "min_community_rank": 0,
            "community_rank_name": "rank",
            "include_community_weight": True,
            "community_weight_name": "occurrence weight",
            "normalize_community_weight": True,
            "max_tokens": 12_000,
            "context_name": "Reports",
        }

        self.map_llm_params = {
            "max_tokens": 1000,
            "temperature": 0.0,
            "response_format": {"type": "json_object"},
        }

        self.reduce_llm_params = {
            "max_tokens": 2000,
            "temperature": 0.0,
        }

        self.search_engine = GlobalSearch(
            llm=self.llm,
            context_builder=self.context_builder,
            token_encoder=self.token_encoder,
            max_data_tokens=12_000,
            map_llm_params=self.map_llm_params,
            reduce_llm_params=self.reduce_llm_params,
            allow_general_knowledge=False,
            json_mode=True,
            context_builder_params=self.context_builder_params,
            concurrent_coroutines=32,
            response_type="multiple paragraphs",
        )

    async def search(self, query: str):
        return await self.search_engine.asearch(query)

    async def run_search(self, query: str):
        result = await self.search(query)
        print(result.response)
        print(result.context_data["reports"])
        print(f"LLM calls: {result.llm_calls}. LLM tokens: {
              result.prompt_tokens}")

class LocalSearchEngine:
    def __init__(self, api_key, model, embedding_model, api_base, input_dir, lancedb_uri, entity_table, community_report_table, relationship_table, covariate_table, entity_embedding_table, text_unit_table, community_level):
        self.llm = ChatOpenAI(
            api_key=api_key,
            model=model,
            api_base=api_base,
            api_type=OpenaiApiType.OpenAI,
            max_retries=20,
        )

        self.token_encoder = tiktoken.get_encoding("cl100k_base")

        self.text_embedder = OpenAIEmbedding(
            api_key=api_key,
            api_base=api_base,
            api_type=OpenaiApiType.OpenAI,
            model=embedding_model,
            deployment_name=embedding_model,
            max_retries=20,
        )

        entity_df = pd.read_parquet(f"{input_dir}/{entity_table}.parquet")
        entity_embedding_df = pd.read_parquet(
            f"{input_dir}/{entity_embedding_table}.parquet")

        entities = read_indexer_entities(
            entity_df, entity_embedding_df, community_level)

        description_embedding_store = LanceDBVectorStore(
            collection_name="entity_description_embeddings",
        )
        description_embedding_store.connect(db_uri=lancedb_uri)
        entity_description_embeddings = store_entity_semantic_embeddings(
            entities=entities, vectorstore=description_embedding_store
        )

        print(f"Entity count: {len(entity_df)}")
        entity_df.head()

        relationship_df = pd.read_parquet(
            f"{input_dir}/{relationship_table}.parquet")
        relationships = read_indexer_relationships(relationship_df)

        print(f"Relationship count: {len(relationship_df)}")
        relationship_df.head()

        covariate_df = pd.read_parquet(
            f"{input_dir}/{covariate_table}.parquet")

        claims = read_indexer_covariates(covariate_df)

        print(f"Claim records: {len(claims)}")
        covariates = {"claims": claims}

        report_df = pd.read_parquet(
            f"{input_dir}/{community_report_table}.parquet")
        reports = read_indexer_reports(
            report_df, entity_df, community_level)

        print(f"Report records: {len(report_df)}")
        report_df.head()

        text_unit_df = pd.read_parquet(
            f"{input_dir}/{text_unit_table}.parquet")
        text_units = read_indexer_text_units(text_unit_df)

        print(f"Text unit records: {len(text_unit_df)}")
        text_unit_df.head()

        self.context_builder = LocalSearchMixedContext(
            community_reports=reports,
            text_units=text_units,
            entities=entities,
            relationships=relationships,
            covariates=covariates,
            entity_text_embeddings=description_embedding_store,
            embedding_vectorstore_key=EntityVectorStoreKey.ID,
            text_embedder=self.text_embedder,
            token_encoder=self.token_encoder,
        )

        self.local_context_params = {
            "text_unit_prop": 0.5,
            "community_prop": 0.1,
            "conversation_history_max_turns": 5,
            "conversation_history_user_turns_only": True,
            "top_k_mapped_entities": 10,
            "top_k_relationships": 10,
            "include_entity_rank": True,
            "include_relationship_weight": True,
            "include_community_rank": False,
            "return_candidate_context": False,
            "embedding_vectorstore_key": EntityVectorStoreKey.ID,
            "max_tokens": 12_000,
        }

        self.llm_params = {
            "max_tokens": 2_000,
            "temperature": 0.0,
        }

        self.search_engine = LocalSearch(
            llm=self.llm,
            context_builder=self.context_builder,
            token_encoder=self.token_encoder,
            llm_params=self.llm_params,
            context_builder_params=self.local_context_params,
            response_type="multiple paragraphs",
        )

    async def search(self, query: str):
        return await self.search_engine.asearch(query)

    async def run_search(self, query: str):
        result = await self.search(query)
        print(result.response)
        print(result.context_data["reports"])
        print(result.context_data["entities"].head())
        print(result.context_data["relationships"].head())
        print(result.context_data["sources"].head())
        if "claims" in result.context_data:
            print(result.context_data["claims"].head())
        print(f"LLM calls: {result.llm_calls}. LLM tokens: {
              result.prompt_tokens}")

if __name__ == "__main__":
    # Example usage
    search_engine_g = GlobalSearchEngine(API_KEY, LLM_MODEL, API_BASE, INPUT_DIR,
                                        ENTITY_TABLE, COMMUNITY_REPORT_TABLE, ENTITY_EMBEDDING_TABLE, COMMUNITY_LEVEL)
    asyncio.run(search_engine_g.run_search("介绍一下网络空间安全课程"))

    # Example usage
    search_engine_l = LocalSearchEngine(API_KEY, LLM_MODEL, EMBEDDING_MODEL, API_BASE, INPUT_DIR, LANCEDB_URI, ENTITY_TABLE,
                                        COMMUNITY_REPORT_TABLE, RELATIONSHIP_TABLE, COVARIATE_TABLE, ENTITY_EMBEDDING_TABLE, TEXT_UNIT_TABLE, COMMUNITY_LEVEL)
    asyncio.run(search_engine_l.run_search("介绍一下肖凌老师"))
