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

# config
from api_utils.default_config import (
    API_KEY, LLM_MODEL, EMBEDDING_MODEL, 
    API_BASE, INPUT_DIR, COMMUNITY_REPORT_TABLE, 
    ENTITY_TABLE, ENTITY_EMBEDDING_TABLE, RELATIONSHIP_TABLE, 
    COVARIATE_TABLE, TEXT_UNIT_TABLE, COMMUNITY_LEVEL, 
    LANCEDB_URI,
)


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
    def __init__(self, request: GlobalSearchRequest):
        self.llm = ChatOpenAI(
            api_key=(request.api_key).strip("'\""),
            model=request.model,
            api_base=request.api_base,
            api_type=OpenaiApiType.OpenAI,
            max_retries=20,
        )

        self.token_encoder = tiktoken.get_encoding("cl100k_base")

        entity_df = pd.read_parquet(f"{request.input_dir}/{request.entity_table}.parquet")
        self.report_df = pd.read_parquet(
            f"{request.input_dir}/{request.community_report_table}.parquet")
        entity_embedding_df = pd.read_parquet(
            f"{request.input_dir}/{request.entity_embedding_table}.parquet")

        self.reports = read_indexer_reports(
            self.report_df, entity_df, request.community_level)
        entities = read_indexer_entities(
            entity_df, entity_embedding_df, request.community_level)

        # output
        print(f"Total report count: {len(self.report_df)}")
        print(f"Report count after filtering by community level {
              request.community_level}: {len(self.reports)}")
        self.report_df.head()

        self.context_builder = GlobalCommunityContext(
            community_reports=self.reports,
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
    def __init__(self, request: LocalSearchRequest):
        self.llm = ChatOpenAI(
            api_key=(request.api_key).strip("'\""),
            model=request.model,
            api_base=request.api_base,
            api_type=OpenaiApiType.OpenAI,
            max_retries=20,
        )

        self.token_encoder = tiktoken.get_encoding("cl100k_base")

        self.text_embedder = OpenAIEmbedding(
            api_key=(request.api_key).strip("'\""),
            api_base=request.api_base,
            api_type=OpenaiApiType.OpenAI,
            model=request.embedding_model,
            deployment_name=request.embedding_model,
            max_retries=20,
        )

        self.entity_df = pd.read_parquet(f"{request.input_dir}/{request.entity_table}.parquet")
        entity_embedding_df = pd.read_parquet(
            f"{request.input_dir}/{request.entity_embedding_table}.parquet")

        entities = read_indexer_entities(
            self.entity_df, entity_embedding_df, request.community_level)

        description_embedding_store = LanceDBVectorStore(
            collection_name="entity_description_embeddings",
        )
        description_embedding_store.connect(db_uri=request.lancedb_uri)
        entity_description_embeddings = store_entity_semantic_embeddings(
            entities=entities, vectorstore=description_embedding_store
        )

        print(f"Entity count: {len(self.entity_df)}")
        self.entity_df.head()

        self.relationship_df = pd.read_parquet(
            f"{request.input_dir}/{request.relationship_table}.parquet")
        relationships = read_indexer_relationships(self.relationship_df)

        print(f"Relationship count: {len(self.relationship_df)}")
        self.relationship_df.head()

        covariate_df = pd.read_parquet(
            f"{request.input_dir}/{request.covariate_table}.parquet")

        self.claims = read_indexer_covariates(covariate_df)

        print(f"Claim records: {len(self.claims)}")
        covariates = {"claims": self.claims}

        self.report_df = pd.read_parquet(
            f"{request.input_dir}/{request.community_report_table}.parquet")
        reports = read_indexer_reports(
            self.report_df, self.entity_df, request.community_level)

        print(f"Report records: {len(self.report_df)}")
        self.report_df.head()

        self.text_unit_df = pd.read_parquet(
            f"{request.input_dir}/{request.text_unit_table}.parquet")
        text_units = read_indexer_text_units(self.text_unit_df)

        print(f"Text unit records: {len(self.text_unit_df)}")
        self.text_unit_df.head()

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
    # global_search_params = GlobalSearchRequest()
    # search_engine_g = GlobalSearchEngine(global_search_params)
    # asyncio.run(search_engine_g.run_search("query1"))

    # Example usage
    # local_search_params = LocalSearchRequest()
    # search_engine_l = LocalSearchEngine(local_search_params)
    # asyncio.run(search_engine_l.run_search("query2"))
    print("Done")
