# -*- coding: utf-8 -*-
"""
HW AI Search Lookup Tool
========================
keyword / semantic / vector / hybrid search over Azure AI Search.

Dynamic-list helpers populate dropdowns for:
    • index_name
    • text_field
    • vector_field
    • semantic_config
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional, Tuple

from promptflow.core import tool
from promptflow.connections import (
    CustomConnection,
    AzureOpenAIConnection,
    OpenAIConnection,
)
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchFieldDataType
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings

# ------------------------------------------------------------------ #
# constants                                                          #
# ------------------------------------------------------------------ #
VALID_TYPES = {"keyword", "semantic", "vector", "hybrid", "hybrid_semantic"}
DEFAULT_EMBED_MODEL = "text-embedding-3-large"

# ------------------------------------------------------------------ #
# 1.  extract endpoint & key from CustomConnection                   #
# ------------------------------------------------------------------ #
def _extract_search_credentials(conn: CustomConnection) -> Tuple[str, str]:
    """Return (endpoint, api_key) regardless of field names used in CustomConnection."""
    c = dict(conn)                           # CustomConnection behaves like Mapping
    endpoint = (
        c.get("endpoint")
        or c.get("api_base")
        or c.get("azure_endpoint")
        or c.get("value1")
        or c.get("key1")
    )
    api_key = (
        c.get("api_key")
        or c.get("value2")
        or c.get("key2")
        or c.get("key")
    )
    if not endpoint or not api_key:
        raise ValueError(
            "CustomConnection must include both search *endpoint* and *api key*.\n"
            "Common field names: endpoint / key1 for URL, api_key / key2 for key."
        )
    return endpoint, api_key

# ------------------------------------------------------------------ #
# 2.  SDK clients                                                    #
# ------------------------------------------------------------------ #
def _index_client(conn: Optional[CustomConnection]) -> Optional[SearchIndexClient]:
    if not conn:
        return None
    try:
        endpoint, key = _extract_search_credentials(conn)
        return SearchIndexClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    except Exception as e:
        # return None so dynamic list falls back to free-text instead of raising
        print(f"[INFO] _index_client: {e}")
        return None


def _client(conn: CustomConnection, index_name: str) -> SearchClient:
    endpoint, key = _extract_search_credentials(conn)
    return SearchClient(endpoint, index_name, AzureKeyCredential(key))

# ------------------------------------------------------------------ #
# 3.  dynamic-list helpers                                           #
# ------------------------------------------------------------------ #
def list_indexes(connection: Optional[CustomConnection] = None, **_) -> List[Dict[str, str]]:
    iclient = _index_client(connection)
    if not iclient:
        return []
    try:
        return [{"value": idx.name, "display_value": idx.name} for idx in iclient.list_indexes()]
    except Exception as e:
        print(f"[INFO] list_indexes failed: {e}")
        return []


def _list_fields(connection: Optional[CustomConnection], index_name: Optional[str]):
    iclient = _index_client(connection)
    if not iclient or not index_name:
        return None
    try:
        return iclient.get_index(index_name).fields
    except Exception as e:
        print(f"[INFO] get_index failed: {e}")
        return None


def list_vector_fields(
    connection: Optional[CustomConnection] = None, index_name: Optional[str] = None, **_
) -> List[Dict[str, str]]:
    fields = _list_fields(connection, index_name)
    if not fields:
        return []
    names = [
        f.name
        for f in fields
        if getattr(f, "dimensions", None)
        or (isinstance(f.type, str) and f.type.lower().startswith("collection(edm.single"))
    ]
    return [{"value": n, "display_value": n} for n in names]


def list_text_fields(
    connection: Optional[CustomConnection] = None, index_name: Optional[str] = None, **_
) -> List[Dict[str, str]]:
    fields = _list_fields(connection, index_name)
    if not fields:
        return []
    names = [
        f.name
        for f in fields
        if f.type == SearchFieldDataType.String and getattr(f, "searchable", False)
    ]
    return [{"value": n, "display_value": n} for n in names]


def list_semantic_configs(
    connection: Optional[CustomConnection] = None, index_name: Optional[str] = None, **_
) -> List[Dict[str, str]]:
    iclient = _index_client(connection)
    if not iclient or not index_name:
        return []
    try:
        idx = iclient.get_index(index_name)
        cfgs = getattr(idx, "semantic_search", None)
        if cfgs and cfgs.configurations:
            return [{"value": c.name, "display_value": c.name} for c in cfgs.configurations]
    except Exception as e:
        print(f"[INFO] list_semantic_configs failed: {e}")
    return []

# ------------------------------------------------------------------ #
# 4.  embeddings helper                                              #
# ------------------------------------------------------------------ #
def _embeddings(conn, model_name: str):
    """Return LangChain embeddings client from AzureOpenAIConnection or OpenAIConnection."""
    if isinstance(conn, AzureOpenAIConnection):
        cd = dict(conn)
        endpoint = cd.get("azure_endpoint") or cd.get("api_base") or cd.get("endpoint")
        api_key = cd.get("api_key")
        if not endpoint or not api_key:
            raise ValueError("AzureOpenAIConnection missing endpoint or api_key.")
        api_version = cd.get("api_version") or "2023-12-01-preview"
        return AzureOpenAIEmbeddings(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
            azure_deployment=model_name,
        )

    if isinstance(conn, OpenAIConnection):
        if not getattr(conn, "api_key", None):
            raise ValueError("OpenAIConnection missing api_key.")
        return OpenAIEmbeddings(
            api_key=conn.api_key,
            base_url=getattr(conn, "api_base", None),
            model=model_name,
        )

    raise ValueError("embeddings_connection must be AzureOpenAIConnection or OpenAIConnection.")

# ------------------------------------------------------------------ #
# 5.  small helper                                                   #
# ------------------------------------------------------------------ #
def _text_from_doc(doc: Dict[str, Any], field: str) -> str:
    return doc.get(field) or doc.get("content") or doc.get("text") or ""

# ------------------------------------------------------------------ #
# 6.  main PromptFlow tool                                           #
# ------------------------------------------------------------------ #
@tool
def hw_ai_search_lookup(
    connection: CustomConnection,
    index_name: str,
    query_text: Optional[str] = None,
    vector: Optional[List[float]] = None,
    embeddings_connection: Optional[AzureOpenAIConnection | OpenAIConnection] = None,
    embedding_model_name: str = DEFAULT_EMBED_MODEL,
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

    needs_text = search_type in {"keyword", "semantic", "hybrid", "hybrid_semantic"}
    needs_vec = search_type in {"vector", "hybrid", "hybrid_semantic"}
    needs_sem = search_type in {"semantic", "hybrid_semantic"}

    if needs_text and not query_text:
        raise ValueError("query_text required for this search_type.")
    if needs_sem and not semantic_config:
        raise ValueError("semantic_config required for semantic search.")

    if needs_vec and vector is None:
        if embeddings_connection is None:
            raise ValueError("Provide vector or embeddings_connection to generate one.")
        vector = _embeddings(embeddings_connection, embedding_model_name).embed_query(query_text)

    client = _client(connection, index_name)

    params: Dict[str, Any] = {
        "top": top_k,
        "filter": filter_expression,
        "select": ",".join(select_fields) if select_fields else None,
    }
    if needs_text:
        params["search_text"] = query_text
    if needs_vec:
        params["vector"] = {
            "value": vector,          # the embedding
            "fields": vector_field,   # name of the vector field
            "k": top_k,               # how many neighbours
        }
        # 'top' stays for keyword/semantic part; SDK ignores it for pure vector
    if needs_sem:
        params["semantic_configuration_name"] = semantic_config

    params = {k: v for k, v in params.items() if v is not None}
    results = client.search(**params)

    output: List[Dict[str, Any]] = []
    for doc in results:
        output.append(
            {
                "text": _text_from_doc(doc, text_field),
                "vector": doc.get(vector_field),
                "score": doc.get("@search.score"),
                "metadata": {k: v for k, v in doc.items() if k not in {text_field, vector_field}},
                "original_entity": doc,
            }
        )
    return output
