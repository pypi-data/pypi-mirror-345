# -*- coding: utf-8 -*-
# pf_reasoning_tool/tools/hw_acs_vector_lookup_tool.py
"""
HW ACS Vector Lookup Tool
-------------------------
Vector / text / hybrid search against Azure AI Search, matching the input
contract of promptflow-vectordb’s Azure Cognitive Search flavour.

Inputs
------
connection           : CustomConnection   (endpoint, api_key)
index_name           : str               (Azure AI Search index)
# Either supply *vector* OR (*query_text* + embeddings_connection):
vector               : list[float]       (optional)
query_text           : str               (optional)
embeddings_connection: Azure/OpenAI conn (required if query_text given)
text_field           : str = "content"
vector_field         : str = "vector"
top_k                : int = 3
search_type          : "vector" | "text" | "hybrid"  (auto-picked if blank)
search_params        : dict   (extra REST params, e.g. {"select": "id,url"})
search_filters       : dict   ({"filter": "category eq 'legal'"})
"""

from typing import List, Dict, Any, Optional
from importlib import import_module

from promptflow.core import tool
from promptflow.connections import (
    CustomConnection, AzureOpenAIConnection, OpenAIConnection
)
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings

VALID_SEARCH = {"vector", "text", "hybrid"}


def _embeddings(conn, model="text-embedding-ada-002"):
    if isinstance(conn, AzureOpenAIConnection):
        return AzureOpenAIEmbeddings(connection=conn, deployment=model)
    if isinstance(conn, OpenAIConnection):
        return OpenAIEmbeddings(connection=conn, model=model)
    raise ValueError("embeddings_connection must be AzureOpenAIConnection or OpenAIConnection")


def _client(c: CustomConnection, index: str) -> SearchClient:
    if not c.endpoint or not c.api_key:
        raise ValueError("CustomConnection must contain endpoint and api_key")
    return SearchClient(c.endpoint, index, AzureKeyCredential(c.api_key))


def _vectorise(q: str, emb) -> List[float]:
    return emb.embed_query(q)


def _extract_text(doc: Dict[str, Any], text_field: str) -> str:
    return doc.get(text_field) or doc.get("content") or doc.get("text") or ""


@tool
def hw_acs_vector_lookup(
    connection: CustomConnection,
    index_name: str,
    # one of the next two is required
    vector: Optional[List[float]] = None,
    query_text: Optional[str] = None,
    # embedding for query_text
    embeddings_connection: Optional[AzureOpenAIConnection | OpenAIConnection] = None,
    embedding_model_name: str = "text-embedding-ada-002",
    # search settings
    top_k: int = 3,
    text_field: str = "content",
    vector_field: str = "vector",
    search_type: Optional[str] = None,           # auto if None
    search_params: Optional[dict] = None,
    search_filters: Optional[dict] = None,
) -> List[Dict[str, Any]]:
    """
    Return promptflow-vectordb schema:
        {text, vector, score, metadata, original_entity}
    """

    if vector is None and query_text is None:
        raise ValueError("Provide either 'vector' or 'query_text'.")
    if vector is not None and query_text is not None:
        raise ValueError("Provide only one of 'vector' or 'query_text'.")
    if query_text and embeddings_connection is None:
        raise ValueError("embeddings_connection required when using query_text.")
    if search_type is None:
        search_type = "vector" if vector else "text"
    search_type = search_type.lower()
    if search_type not in VALID_SEARCH:
        raise ValueError(f"search_type must be one of {VALID_SEARCH}")

    # vectorise if needed
    if vector is None:
        vector = _vectorise(query_text, _embeddings(embeddings_connection, embedding_model_name))

    client = _client(connection, index_name)

    # compose Azure Search parameters
    extra = search_params or {}
    extra.update(search_filters or {})
    extra.setdefault("top", top_k)

    if search_type in {"vector", "hybrid"}:
        extra["vector"] = vector
        extra["vector_fields"] = vector_field

    if search_type in {"text", "hybrid"}:
        extra["search_text"] = query_text or ""

    results = client.search(**extra)

    out: List[Dict[str, Any]] = []
    for doc in results:
        out.append(
            {
                "text": _extract_text(doc, text_field),
                "vector": doc.get(vector_field),
                "score": doc.get("@search.score"),
                "metadata": {k: v for k, v in doc.items() if k not in (text_field, vector_field)},
                "original_entity": doc,  # entire response row
            }
        )
    return out
