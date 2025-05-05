# -*- coding: utf-8 -*-
# pf_reasoning_tool/tools/hw_ai_search_lookup_tool.py
"""
HW AI Search Lookup Tool
------------------------
Vector, text or hybrid search over Azure AI Search.

Required packages
    azure-search-documents>=11.4.0b7
    langchain-openai>=0.1.5   (for embeddings helpers)

Required connections
    connection            -> CustomConnection with fields: endpoint, api_key
    embeddings_connection -> AzureOpenAIConnection or OpenAIConnection
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from importlib import import_module

from promptflow.core import tool
from promptflow.connections import (
    CustomConnection, AzureOpenAIConnection, OpenAIConnection
)
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings

VALID_SEARCH = {"vector", "text", "hybrid"}


@dataclass
class _SearchParams:
    query: str
    vector: List[float]
    top_k: int
    search_type: str
    filter_expr: Optional[str]
    vector_fields: str
    text_fields: str
    semantic_config: Optional[str]


# ------------------------------------------------------------------ #
# helpers                                                            #
# ------------------------------------------------------------------ #

def _get_embeddings(conn, model) -> AzureOpenAIEmbeddings | OpenAIEmbeddings:
    if isinstance(conn, AzureOpenAIConnection):
        return AzureOpenAIEmbeddings(connection=conn, deployment=model)
    if isinstance(conn, OpenAIConnection):
        return OpenAIEmbeddings(connection=conn, model=model)
    raise ValueError("embeddings_connection must be AzureOpenAIConnection or OpenAIConnection.")


def _vectorize(embeddings, text: str) -> List[float]:
    return embeddings.embed_query(text)


def _client(conn: CustomConnection, index_name: str) -> SearchClient:
    if not conn.endpoint or not conn.api_key:
        raise ValueError("CustomConnection requires 'endpoint' and 'api_key'.")
    return SearchClient(
        endpoint=conn.endpoint,
        index_name=index_name,
        credential=AzureKeyCredential(conn.api_key),
    )


def _first_text_field(doc: Dict[str, Any], pref_fields: List[str]) -> str:
    # Explicit preference list wins
    for f in pref_fields:
        if f in doc and isinstance(doc[f], str):
            return doc[f]
    # Fallbacks
    return doc.get("content") or doc.get("text") or ""


# ------------------------------------------------------------------ #
# main tool                                                          #
# ------------------------------------------------------------------ #

@tool
def hw_ai_search_lookup(
    query: str,
    connection: CustomConnection,
    index_name: str,
    embeddings_connection: AzureOpenAIConnection | OpenAIConnection,
    model_name: str = "text-embedding-ada-002",
    search_type: str = "hybrid",        # 'vector', 'text', or 'hybrid'
    top_k: int = 5,
    filter_expression: Optional[str] = None,
    vector_fields: Optional[List[str]] = None,   # e.g. ["vector"]
    text_fields: Optional[List[str]] = None,     # e.g. ["chunk_text"]
    semantic_configuration: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Returns top-K docs from Azure AI Search.

    Output list items:
        { "text": str, "metadata": dict, "score": float }
    """

    if not query:
        raise ValueError("query cannot be blank.")
    if search_type not in VALID_SEARCH:
        raise ValueError(f"search_type must be one of {VALID_SEARCH}.")
    if top_k <= 0:
        raise ValueError("top_k must be > 0.")

    embeddings = _get_embeddings(embeddings_connection, model_name)
    vector = _vectorize(embeddings, query)
    client = _client(connection, index_name)

    # prepare common kwargs
    kwargs = {
        "top": top_k,
        "filter": filter_expression,
    }
    if text_fields:
        kwargs["search_fields"] = ",".join(text_fields)
    if semantic_configuration:
        kwargs["semantic_configuration_name"] = semantic_configuration

    # dispatch by search_type
    if search_type == "vector":
        results = client.search(
            search_text="",
            vector=vector,
            vector_fields=",".join(vector_fields or ["vector"]),
            **kwargs,
        )
    elif search_type == "text":
        results = client.search(search_text=query, **kwargs)
    else:  # hybrid
        results = client.search(
            search_text=query,
            vector=vector,
            vector_fields=",".join(vector_fields or ["vector"]),
            **kwargs,
        )

    pref_text_fields = text_fields or []
    items: List[Dict[str, Any]] = []
    for doc in results:
        items.append(
            {
                "text": _first_text_field(doc, pref_text_fields),
                "metadata": {k: v for k, v in doc.items() if k not in ("content", "text")},
                "score": doc.get("@search.score"),
            }
        )
    return items
