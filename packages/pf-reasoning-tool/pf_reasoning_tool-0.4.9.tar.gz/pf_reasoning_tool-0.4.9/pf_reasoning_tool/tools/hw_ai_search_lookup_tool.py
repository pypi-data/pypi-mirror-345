# -*- coding: utf-8 -*-
# pf_reasoning_tool/tools/hw_ai_search_lookup_tool.py
"""
HW AI Search Lookup Tool
------------------------
Pure Azure AI Search implementation (no LangChain vectorstores).

Inputs
------
connection           : CustomConnection  (endpoint, api_key)               [required]
index_name           : str                                                  [required]

EITHER
    query_text       : str  + embeddings_connection (Azure/OpenAI)         [hybrid / text]
OR
    vector           : list[float]                                          [vector / hybrid]

Optional pins
-------------
top_k                : int        default 3
search_type          : 'vector' | 'text' | 'hybrid'   (auto‐detect)
text_field           : str        default 'content'   (returned as .text)
vector_field         : str        default 'vector'
filter_expression    : str        OData filter
select_fields        : list[str]  fields to select (comma-joined)
semantic_config      : str        semantic configuration name
"""

from typing import List, Dict, Any, Optional

from promptflow.core import tool
from promptflow.connections import (
    CustomConnection,
    AzureOpenAIConnection,
    OpenAIConnection,
)
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings

VALID_TYPES = {"vector", "text", "hybrid"}


# ---------- helpers -------------------------------------------------- #
def _embeddings(conn, model):
    if isinstance(conn, AzureOpenAIConnection):
        return AzureOpenAIEmbeddings(connection=conn, deployment=model)
    if isinstance(conn, OpenAIConnection):
        return OpenAIEmbeddings(connection=conn, model=model)
    raise ValueError("embeddings_connection must be AzureOpenAIConnection or OpenAIConnection")


def _client(c: CustomConnection, index: str) -> SearchClient:
    if not c.endpoint or not c.api_key:
        raise ValueError("CustomConnection must contain endpoint and api_key.")
    return SearchClient(
        endpoint=c.endpoint,
        index_name=index,
        credential=AzureKeyCredential(c.api_key),
    )


def _text_field_from_doc(doc: Dict[str, Any], field: str) -> str:
    return doc.get(field) or doc.get("content") or doc.get("text") or ""


# ---------- main tool ------------------------------------------------ #
@tool
def hw_ai_search_lookup(
    connection: CustomConnection,
    index_name: str,
    # one of:
    query_text: Optional[str] = None,
    vector: Optional[List[float]] = None,
    embeddings_connection: Optional[AzureOpenAIConnection | OpenAIConnection] = None,
    embedding_model_name: str = "text-embedding-ada-002",
    # options
    search_type: Optional[str] = None,
    top_k: int = 3,
    text_field: str = "content",
    vector_field: str = "vector",
    filter_expression: Optional[str] = None,
    select_fields: Optional[List[str]] = None,
    semantic_config: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Returns list of dicts:  {text, vector, score, metadata, original_entity}
    """

    # -------- sanity checks -----------------
    if (query_text is None) == (vector is None):
        raise ValueError("Provide **either** query_text or vector, not both.")
    if vector is None and embeddings_connection is None:
        raise ValueError("embeddings_connection required when using query_text.")
    if search_type is None:
        search_type = "vector" if vector else "text"
    search_type = search_type.lower()
    if search_type not in VALID_TYPES:
        raise ValueError(f"search_type must be one of {VALID_TYPES}")
    if top_k <= 0:
        raise ValueError("top_k must be > 0")

    # -------- prepare query -----------------
    if vector is None:
        emb = _embeddings(embeddings_connection, embedding_model_name)
        vector = emb.embed_query(query_text)

    client = _client(connection, index_name)

    params = {
        "top": top_k,
        "filter": filter_expression,
        "select": ",".join(select_fields) if select_fields else None,
        "semantic_configuration_name": semantic_config,
    }

    if search_type in {"text", "hybrid"}:
        params["search_text"] = query_text or ""

    if search_type in {"vector", "hybrid"}:
        params["vector"] = vector
        params["vector_fields"] = vector_field

    # remove None params
    params = {k: v for k, v in params.items() if v is not None}

    results = client.search(**params)

    out: List[Dict[str, Any]] = []
    for doc in results:
        out.append(
            {
                "text": _text_field_from_doc(doc, text_field),
                "vector": doc.get(vector_field),
                "score": doc.get("@search.score"),
                "metadata": {k: v for k, v in doc.items() if k not in (text_field, vector_field)},
                "original_entity": doc,
            }
        )
    return out