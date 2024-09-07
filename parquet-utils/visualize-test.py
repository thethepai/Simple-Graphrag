from yfiles_jupyter_graphs import GraphWidget
import os

import pandas as pd
import tiktoken

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
from graphrag.query.structured_search.local_search.mixed_context import (
    LocalSearchMixedContext,
)
from graphrag.query.structured_search.local_search.search import LocalSearch
from graphrag.vector_stores.lancedb import LanceDBVectorStore

INPUT_DIR = "./output/artifacts"
LANCEDB_URI = f"{INPUT_DIR}/lancedb"

COMMUNITY_REPORT_TABLE = "create_final_community_reports"
ENTITY_TABLE = "create_final_nodes"
ENTITY_EMBEDDING_TABLE = "create_final_entities"
RELATIONSHIP_TABLE = "create_final_relationships"
COVARIATE_TABLE = "create_final_covariates"
TEXT_UNIT_TABLE = "create_final_text_units"
COMMUNITY_LEVEL = 2

# read nodes table to get community and degree data
entity_df = pd.read_parquet(f"{INPUT_DIR}/{ENTITY_TABLE}.parquet")
entity_embedding_df = pd.read_parquet(
    f"{INPUT_DIR}/{ENTITY_EMBEDDING_TABLE}.parquet")

relationship_df = pd.read_parquet(f"{INPUT_DIR}/{RELATIONSHIP_TABLE}.parquet")
relationships = read_indexer_relationships(relationship_df)


# converts the entities dataframe to a list of dicts for yfiles-jupyter-graphs
def convert_entities_to_dicts(df):
    """Convert the entities dataframe to a list of dicts for yfiles-jupyter-graphs."""
    nodes_dict = {}
    for _, row in df.iterrows():
        # Create a dictionary for each row and collect unique nodes
        node_id = row["title"]
        if node_id not in nodes_dict:
            nodes_dict[node_id] = {
                "id": node_id,
                "properties": row.to_dict(),
            }
    return list(nodes_dict.values())


# converts the relationships dataframe to a list of dicts for yfiles-jupyter-graphs
def convert_relationships_to_dicts(df):
    """Convert the relationships dataframe to a list of dicts for yfiles-jupyter-graphs."""
    relationships = []
    for _, row in df.iterrows():
        # Create a dictionary for each row
        relationships.append({
            "start": row["source"],
            "end": row["target"],
            "properties": row.to_dict(),
        })
    return relationships


w = GraphWidget()
w.directed = True
w.nodes = convert_entities_to_dicts(entity_df)
w.edges = convert_relationships_to_dicts(relationship_df)

# show title on the node
w.node_label_mapping = "title"


# map community to a color
def community_to_color(community):
    """Map a community to a color."""
    colors = [
        "crimson",
        "darkorange",
        "indigo",
        "cornflowerblue",
        "cyan",
        "teal",
        "green",
    ]
    return (
        colors[int(community) % len(colors)
               ] if community is not None else "lightgray"
    )


def edge_to_source_community(edge):
    """Get the community of the source node of an edge."""
    source_node = next(
        (entry for entry in w.nodes if entry["properties"]
         ["title"] == edge["start"]),
        None,
    )
    source_node_community = source_node["properties"]["community"]
    return source_node_community if source_node_community is not None else None


w.node_color_mapping = lambda node: community_to_color(
    node["properties"]["community"])
w.edge_color_mapping = lambda edge: community_to_color(
    edge_to_source_community(edge))
# map size data to a reasonable factor
w.node_scale_factor_mapping = lambda node: 0.5 + \
    node["properties"]["size"] * 1.5 / 20
# use weight for edge thickness
w.edge_thickness_factor_mapping = "weight"

# Use the circular layout for this visualization. For larger graphs, the default organic layout is often preferrable.
w.circular_layout()
