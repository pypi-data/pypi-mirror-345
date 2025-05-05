# -*- coding: utf-8 -*-
# pf_reasoning_tool/tools/hw_ai_search_lookup_tool.py
"""
HW AI Search Lookup Tool
------------------------
Supports five modes that mirror the built-in Index Lookup node:

    keyword           – classic keyword search
    semantic          – keyword + semantic ranking
    vector            – pure vector search
    hybrid            – keyword + vector
    hybrid_semantic   – keyword + vector + semantic ranking

Dynamic-list helpers expose:
    • all indexes in the service
    • vector-capable fields
    • searchable text fields
    • semantic configurations of the selected index
"""

from typing import List, Dict, Any, Optional
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchFieldDataType
from promptflow.core import tool
from promptflow.connections import (
    CustomConnection,
    AzureOpenAIConnection,
    OpenAIConnection,
)
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings

VALID_TYPES = {"keyword", "semantic", "vector", "hybrid", "hybrid_semantic"}


# ------------------------------------------------------------------ #
# dynamic-list helpers (for UI dropdowns)                            #
# ------------------------------------------------------------------ #
def _index_client(conn: CustomConnection) -> SearchIndexClient:
    return SearchIndexClient(
        endpoint=conn.endpoint, credential=AzureKeyCredential(conn.api_key)
    )


def list_indexes(connection: CustomConnection, **_) -> List[Dict[str, str]]:
    try:
        return [
            {"value": idx.name, "display_value": idx.name}
            for idx in _index_client(connection).list_indexes()
        ]
    except Exception as e:
        print(f"[INFO] list_indexes failed: {e}")
        return []


def _list_fields(connection: CustomConnection, index_name: str):
    return _index_client(connection).get_index(index_name).fields


def list_vector_fields(connection: CustomConnection, index_name: str, **_) -> List[Dict[str, str]]:
    try:
        names = [
            f.name
            for f in _list_fields(connection, index_name)
            if getattr(f, "dimensions", None)
            or (isinstance(f.type, str) and f.type.lower().startswith("collection(edm.single"))
        ]
        return [{"value": n, "display_value": n} for n in names]
    except Exception as e:
        print(f"[INFO] list_vector_fields failed: {e}")
        return []


def list_text_fields(connection: CustomConnection, index_name: str, **_) -> List[Dict[str, str]]:
    try:
        names = [
            f.name
            for f in _list_fields(connection, index_name)
            if f.type == SearchFieldDataType.String and getattr(f, "searchable", False)
        ]
        return [{"value": n, "display_value": n} for n in names]
    except Exception as e:
        print(f"[INFO] list_text_fields failed: {e}")
        return []


def list_semantic_configs(
    connection: CustomConnection, index_name: str, **_
) -> List[Dict[str, str]]:
    try:
        idx = _index_client(connection).get_index(index_name)
        configs = getattr(idx, "semantic_search", None)
        if configs and configs.configurations:
            return [{"value": c.name, "display_value": c.name} for c in configs.configurations]
    except Exception as e:
        print(f"[INFO] list_semantic_configs failed: {e}")
    return []


# ------------------------------------------------------------------ #
# internal helpers                                                   #
# ------------------------------------------------------------------ #
def _embeddings(conn, model):
    if isinstance(conn, AzureOpenAIConnection):
        return AzureOpenAIEmbeddings(connection=conn, deployment=model)
    if isinstance(conn, OpenAIConnection):
        return OpenAIEmbeddings(connection=conn, model=model)
    raise ValueError("embeddings_connection must be AzureOpenAIConnection or OpenAIConnection.")


def _client(c: CustomConnection, idx: str) -> SearchClient:
    return SearchClient(c.endpoint, idx, AzureKeyCredential(c.api_key))


def _text_from_doc(doc: Dict[str, Any], field: str) -> str:
    return doc.get(field) or doc.get("content") or doc.get("text") or ""


# ------------------------------------------------------------------ #
# main PromptFlow tool                                               #
# ------------------------------------------------------------------ #
@tool
def hw_ai_search_lookup(
    connection: CustomConnection,
    index_name: str,
    #   ONE OF:
    query_text: Optional[str] = None,
    vector: Optional[List[float]] = None,
    #   embedding for query_text
    embeddings_connection: Optional[AzureOpenAIConnection | OpenAIConnection] = None,
    embedding_model_name: str = "text-embedding-3-large",
    #   search knobs
    search_type: str = "hybrid",
    top_k: int = 3,
    text_field: str = "content",
    vector_field: str = "vector",
    filter_expression: Optional[str] = None,
    select_fields: Optional[List[str]] = None,
    semantic_config: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Returns list[{text, vector, score, metadata, original_entity}]
    """

    search_type = (search_type or "hybrid").lower()
    if search_type not in VALID_TYPES:
        raise ValueError(f"search_type must be one of {VALID_TYPES}")
    if top_k <= 0:
        raise ValueError("top_k must be > 0")

    # requirement matrix
    needs_text = search_type in {"keyword", "semantic", "hybrid", "hybrid_semantic"}
    needs_vec = search_type in {"vector", "hybrid", "hybrid_semantic"}
    needs_sem = search_type in {"semantic", "hybrid_semantic"}

    if needs_text and not query_text:
        raise ValueError("query_text required for this search_type.")
    if needs_sem and not semantic_config:
        raise ValueError("semantic_config required for semantic search.")
    if needs_vec and vector is None:
        if embeddings_connection is None:
            raise ValueError("Provide vector or embeddings_connection to compute it.")
        emb = _embeddings(embeddings_connection, embedding_model_name)
        vector = emb.embed_query(query_text)

    client = _client(connection, index_name)

    params: Dict[str, Any] = {
        "top": top_k,
        "filter": filter_expression,
        "select": ",".join(select_fields) if select_fields else None,
    }
    if needs_text:
        params["search_text"] = query_text
    if needs_vec:
        params["vector"] = vector
        params["vector_fields"] = vector_field
    if needs_sem:
        params["semantic_configuration_name"] = semantic_config

    params = {k: v for k, v in params.items() if v is not None}
    results = client.search(**params)

    out: List[Dict[str, Any]] = []
    for doc in results:
        out.append(
            {
                "text": _text_from_doc(doc, text_field),
                "vector": doc.get(vector_field),
                "score": doc.get("@search.score"),
                "metadata": {k: v for k, v in doc.items() if k not in (text_field, vector_field)},
                "original_entity": doc,
            }
        )
    return out
