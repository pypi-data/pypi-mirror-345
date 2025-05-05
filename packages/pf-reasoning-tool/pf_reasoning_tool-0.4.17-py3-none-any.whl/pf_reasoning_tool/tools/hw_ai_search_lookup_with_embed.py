# -*- coding: utf-8 -*-
"""
HW AI Search Lookup Tool (with Internal Embedding)
=================================================
Performs keyword / semantic / vector / hybrid search over Azure AI Search.
Embeds input queries internally using Azure OpenAI or OpenAI connection.
Uses CustomConnection for Azure AI Search credentials.

Dynamic-list helpers populate dropdowns for:
    • index_name
    • text_field
    • vector_field
    • semantic_config
"""

from __future__ import annotations

import contextvars
import os
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import List, Dict, Any, Optional, Tuple, Union

from promptflow.core import tool
from promptflow.connections import (
    CustomConnection,  # Using CustomConnection as requested
    AzureOpenAIConnection,
    OpenAIConnection,
)
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchFieldDataType
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings # Re-added for internal embedding

# ------------------------------------------------------------------ #
# constants                                                          #
# ------------------------------------------------------------------ #
VALID_QUERY_TYPES = {"keyword", "semantic", "vector", "hybrid", "hybrid_semantic"}
DEFAULT_EMBED_MODEL = "text-embedding-3-large" # Default embedding model

# ------------------------------------------------------------------ #
# 1.  extract endpoint & key from CustomConnection                   #
# ------------------------------------------------------------------ #
def _extract_search_credentials(conn: CustomConnection) -> Tuple[str, str]:
    """Return (endpoint, api_key) regardless of field names used in CustomConnection."""
    c = dict(conn) # CustomConnection behaves like Mapping
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
            "Common field names: endpoint / api_base / value1 / key1 for URL, "
            "api_key / value2 / key2 / key for the key."
        )
    # Handle placeholder key commonly used in PF connections stored in workspace
    key_to_use = os.getenv("AZURE_SEARCH_KEY", api_key) if api_key == "***" else api_key
    if not key_to_use or key_to_use == "***":
         raise ValueError("Could not resolve Azure AI Search API key. Ensure it's set in the connection or as AZURE_SEARCH_KEY environment variable.")

    return endpoint, key_to_use

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
        print(f"[INFO] _index_client creation failed: {e}")
        return None


def _client(conn: CustomConnection, index_name: str) -> SearchClient:
    endpoint, key = _extract_search_credentials(conn)
    return SearchClient(endpoint, index_name, AzureKeyCredential(key))

# ------------------------------------------------------------------ #
# 3.  dynamic-list helpers (using original names)                    #
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
        print(f"[INFO] get_index for fields failed: {e}")
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
        if getattr(f, "vector_search_dimensions", None)
        or getattr(f, "dimensions", None)
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
        semantic_search_config = getattr(idx, "semantic_search", None)
        if semantic_search_config and getattr(semantic_search_config, "configurations", None):
            return [{"value": c.name, "display_value": c.name} for c in semantic_search_config.configurations]
    except Exception as e:
        print(f"[INFO] list_semantic_configs failed: {e}")
    return []

# ------------------------------------------------------------------ #
# 4.  embeddings helper (Re-instated)                                #
# ------------------------------------------------------------------ #
def _embeddings(conn, model_name: str):
    """Return LangChain embeddings client from AzureOpenAIConnection or OpenAIConnection."""
    if isinstance(conn, AzureOpenAIConnection):
        cd = dict(conn)
        endpoint = cd.get("azure_endpoint") or cd.get("api_base") or cd.get("endpoint")
        api_key = cd.get("api_key")
        # Handle placeholder key for AOAI connection
        resolved_api_key = os.getenv("AZURE_OPENAI_API_KEY", api_key) if api_key == "***" else api_key
        if not endpoint or not resolved_api_key or resolved_api_key == "***":
            raise ValueError("AzureOpenAIConnection missing endpoint or resolvable api_key. Check connection or AZURE_OPENAI_API_KEY env var.")
        api_version = cd.get("api_version") or "2024-02-01" # Use a recent stable version
        return AzureOpenAIEmbeddings(
            azure_endpoint=endpoint,
            api_key=resolved_api_key,
            api_version=api_version,
            azure_deployment=model_name, # Model name here is deployment name for Azure
        )

    if isinstance(conn, OpenAIConnection):
        api_key = getattr(conn, "api_key", None)
        # Handle placeholder key for OpenAI connection
        resolved_api_key = os.getenv("OPENAI_API_KEY", api_key) if api_key == "***" else api_key
        if not resolved_api_key or resolved_api_key == "***":
             raise ValueError("OpenAIConnection missing resolvable api_key. Check connection or OPENAI_API_KEY env var.")
        return OpenAIEmbeddings(
            api_key=resolved_api_key,
            base_url=getattr(conn, "base_url", None) or getattr(conn, "api_base", None), # Allow overriding base_url
            model=model_name, # Model name here is actual model like "text-embedding-3-large"
        )

    # Should not happen if input types are enforced, but good practice
    raise ValueError("embeddings_connection must be AzureOpenAIConnection or OpenAIConnection.")

# ------------------------------------------------------------------ #
# 5.  small helper                                                   #
# ------------------------------------------------------------------ #
def _text_from_doc(doc: Dict[str, Any], text_field: str) -> str:
    """Extracts text, prioritizing specified field then common fallbacks."""
    return doc.get(text_field) or doc.get("content") or doc.get("text") or ""

# ------------------------------------------------------------------ #
# 6.  Main search execution logic for a single query                 #
# ------------------------------------------------------------------ #
def _execute_search(
    query_text: str, # Always expect text now
    client: SearchClient,
    query_type: str,
    top_k: int,
    text_field: str,
    vector_field: str,
    search_filters: Optional[str],
    select_fields: Optional[List[str]],
    semantic_config: Optional[str],
    # Embedding related inputs passed down:
    embeddings_connection: Optional[AzureOpenAIConnection | OpenAIConnection],
    embedding_model_name: str,
) -> List[Dict[str, Any]]:
    """Generates embedding if needed, executes search, returns formatted results."""

    vector: Optional[List[float]] = None # Initialize vector as None

    needs_vec = query_type in {"vector", "hybrid", "hybrid_semantic"}
    needs_sem = query_type in {"semantic", "hybrid_semantic"}

    # --- Generate Embedding if required ---
    if needs_vec:
        if embeddings_connection is None:
            raise ValueError(f"Embeddings connection is required for query_type '{query_type}'.")
        try:
            embeddings_client = _embeddings(embeddings_connection, embedding_model_name)
            vector = embeddings_client.embed_query(query_text)
        except Exception as e:
            print(f"[ERROR] Failed to generate embedding for query: '{query_text}'. Error: {e}")
            raise ValueError(f"Embedding generation failed: {e}") from e # Re-raise to fail the step

    # --- Validate Inputs based on query_type ---
    # Text is always present now. Vector is generated if needed.
    if needs_sem and not semantic_config:
        raise ValueError(f"Semantic configuration required for query_type '{query_type}'.")

    # --- Build search parameters ---
    params: Dict[str, Any] = {
        "top": top_k,
        "filter": search_filters,
        "select": ",".join(select_fields) if select_fields else None,
        "include_total_count": False,
    }

    needs_text_search = query_type in {"keyword", "semantic", "hybrid", "hybrid_semantic"}

    if needs_text_search:
        params["search_text"] = query_text
    if needs_vec:
        if not vector: # Should have been generated above, but double check
             raise RuntimeError("Internal Error: Vector required but not generated.")
        vector_query = {
            "vector": vector,
            "k": top_k,
            "fields": vector_field,
        }
        # Handle SDK version differences for vector parameter
        try:
            SearchClient.search.__kwdefaults__.get('vector_queries')
            params["vector_queries"] = [vector_query]
            if query_type == "vector": params.pop("top", None)
        except AttributeError:
            print("[INFO] Using older 'vector' parameter name for search SDK.")
            params["vector"] = vector_query

    if needs_sem:
        params["semantic_configuration_name"] = semantic_config
        # Consider adding query_type="semantic" if needed by your index/SDK version
        # params["query_type"] = "semantic"

    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}

    # --- Execute search ---
    try:
        results = client.search(**params)
    except Exception as e:
        print(f"[ERROR] Azure AI Search request failed for query '{query_text}'. Error: {e}")
        print(f"[DEBUG] Search parameters used: {params}")
        # Re-raise the exception to make the flow failure clear
        raise RuntimeError(f"Azure AI Search failed: {e}") from e

    # --- Format output ---
    output: List[Dict[str, Any]] = []
    for doc in results:
        metadata = {
            k: v
            for k, v in doc.items()
            # Exclude main text field and internal search fields
            if k != text_field and not k.startswith("@search.")
        }
        # Include reranker score in metadata if present
        reranker_score = doc.get("@search.reranker_score")
        if reranker_score is not None:
             metadata["reranker_score"] = reranker_score
        # Include original vector score in metadata if vector search was done
        vector_score = doc.get("@search.score") # Primary score often reflects vector score in vector/hybrid

        output.append(
            {
                "text": _text_from_doc(doc, text_field),
                "score": vector_score, # Return the primary score
                "metadata": metadata,
            }
        )
    return output

# ------------------------------------------------------------------ #
# 7.  main PromptFlow tool                                           #
# ------------------------------------------------------------------ #
@tool
def hw_ai_search_lookup_with_embed(
    # Inputs for Search Service
    connection: CustomConnection,                         # Changed back to CustomConnection
    index_name: str,
    # Inputs for Querying / Embedding
    queries: Union[str, List[str]],                       # Text query/queries
    embeddings_connection: Optional[AzureOpenAIConnection | OpenAIConnection] = None, # Optional connection for embedding
    embedding_model_name: str = DEFAULT_EMBED_MODEL,      # Embedding model/deployment name
    # Search Configuration
    query_type: str = "hybrid",
    top_k: int = 3,
    text_field: str = "content",                          # Field names reverted
    vector_field: str = "vector",
    search_filters: Optional[str] = None,
    select_fields: Optional[List[str]] = None,
    semantic_config: Optional[str] = None,                # Renamed back
) -> List[List[Dict[str, Any]]]:                          # Output: List[List[results]]
    """
    Performs lookup on Azure AI Search, embedding queries internally.
    Uses CustomConnection for AI Search and AzureOpenAI/OpenAI Connection for embeddings.
    Accepts single or multiple queries, returns a list of lists of results.

    Returns: List[List[dict]], where each inner list contains results for a query.
             Each result dict has keys: {'text', 'score', 'metadata'}.
    """

    query_type = (query_type or "hybrid").lower()
    if query_type not in VALID_QUERY_TYPES:
        raise ValueError(f"query_type must be one of {VALID_QUERY_TYPES}")
    if top_k <= 0:
        raise ValueError("top_k must be > 0")

    # --- Input Handling ---
    is_single_query = isinstance(queries, str)
    query_list = [queries] if is_single_query else queries

    if not query_list:
        return [] # Return empty list if input queries list is empty

    # --- Validate embedding connection if needed ---
    needs_vector_embedding = query_type in {"vector", "hybrid", "hybrid_semantic"}
    if needs_vector_embedding and not embeddings_connection:
        raise ValueError(
            f"An 'embeddings_connection' (AzureOpenAI or OpenAI) is required "
            f"when query_type is '{query_type}'."
        )

    # --- Prepare Search Client ---
    try:
        client = _client(connection, index_name)
    except Exception as e:
        # Fail early if connection details are wrong
        raise ValueError(f"Failed to create Azure AI Search client: {e}") from e

    # --- Execute Search for each query (potentially in parallel) ---
    all_results = []

    # Prepare partial function with fixed arguments for mapping
    # Pass embedding details down to the execution function
    search_func_partial = partial(
        _execute_search,
        client=client,
        query_type=query_type,
        top_k=top_k,
        text_field=text_field,
        vector_field=vector_field,
        search_filters=search_filters,
        select_fields=select_fields,
        semantic_config=semantic_config,
        embeddings_connection=embeddings_connection, # Pass connection object
        embedding_model_name=embedding_model_name,   # Pass model name
    )

    # Use ThreadPoolExecutor for potential parallelism
    parent_context = contextvars.copy_context()
    def run_with_context(func, *args):
        return parent_context.run(func, *args)

    with ThreadPoolExecutor() as executor:
        # Map queries to the partial search function
        # The first argument to the partial function will be the query_text
        tasks = [executor.submit(run_with_context, search_func_partial, query) for query in query_list]

        for task in tasks:
            try:
                # Result from _execute_search is List[Dict]
                all_results.append(task.result())
            except Exception as e:
                # If _execute_search raises an error, catch it here
                # Log or handle as needed, append empty list to maintain structure
                print(f"[ERROR] Search failed for one query: {e}")
                all_results.append([]) # Append empty list for failed query

    # --- Return results ---
    # Output structure is List[List[Dict]]
    return all_results