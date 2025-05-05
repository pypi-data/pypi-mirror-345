# -*- coding: utf-8 -*-
"""
HW AI Search Lookup Tool (Internal Embedding - Minimal Load Changes)
===================================================================
Handles CustomConnection(key1=URL, key2=KEY) for Search
Handles standard AzureOpenAIConnection for Embeddings.
Focuses on ensuring the tool loads correctly in the PromptFlow UI.
"""

from __future__ import annotations

import contextvars
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import List, Dict, Any, Optional, Tuple, Union

# Core PromptFlow and Azure SDK imports
from promptflow.core import tool
from promptflow.connections import (
    CustomConnection,
    AzureOpenAIConnection,
    OpenAIConnection, # Keep for flexibility, though user specified AOAI
)
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ClientAuthenticationError
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchFieldDataType

# Embedding library import - Ensure installed in environment
try:
    from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
except ImportError:
     raise ImportError("Could not import langchain_openai. Please ensure 'langchain-openai' is installed in the PromptFlow execution environment.")

# Basic logger setup
logger = logging.getLogger(__name__)
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logger.setLevel(getattr(logging, log_level, logging.INFO))

# ------------------------------------------------------------------ #
# constants                                                          #
# ------------------------------------------------------------------ #
VALID_QUERY_TYPES = {"keyword", "semantic", "vector", "hybrid", "hybrid_semantic"}
DEFAULT_EMBED_MODEL = "text-embedding-3-large"

# ------------------------------------------------------------------ #
# 1.  extract endpoint & key from CustomConnection                   #
# ------------------------------------------------------------------ #
def _extract_search_credentials(conn: CustomConnection) -> Tuple[str, str]:
    """Return (endpoint, api_key) from CustomConnection with env var fallback."""
    if not isinstance(conn, CustomConnection):
        raise TypeError(f"Internal Error: Expected CustomConnection, got {type(conn).__name__}")

    c = dict(conn)
    # --- Handles key1 for URL ---
    endpoint = ( c.get("endpoint") or c.get("api_base") or c.get("azure_endpoint") or c.get("value1") or c.get("key1") )
    # --- Handles key2 for API Key ---
    api_key_from_conn = ( c.get("api_key") or c.get("value2") or c.get("key2") or c.get("key") )

    if not endpoint: raise ValueError("CustomConnection must include search endpoint (e.g., 'endpoint', 'key1').")
    if not api_key_from_conn: raise ValueError("CustomConnection must include search api key (e.g., 'api_key', 'key2').")

    resolved_api_key = api_key_from_conn
    if api_key_from_conn == "***":
        logger.info("Search key is '***', resolving from AZURE_SEARCH_KEY env var.")
        resolved_api_key = os.getenv("AZURE_SEARCH_KEY")
        if not resolved_api_key:
            raise ValueError("Search key is '***' in connection, but 'AZURE_SEARCH_KEY' environment variable is not set.")

    if not resolved_api_key: raise ValueError("Internal Error: Failed to determine valid Azure AI Search API key.")
    # logger.debug(f"Using AI Search Endpoint: {endpoint}")
    return endpoint, resolved_api_key

# ------------------------------------------------------------------ #
# 2.  SDK clients (Simple _index_client for loading safety)          #
# ------------------------------------------------------------------ #
def _index_client(conn: Optional[CustomConnection]) -> Optional[SearchIndexClient]:
    """Creates SearchIndexClient safely for dynamic lists. Returns None on ANY exception."""
    if not conn: return None
    if not isinstance(conn, CustomConnection):
         print(f"[WARN] _index_client expected CustomConnection, got {type(conn).__name__}.")
         return None
    try:
        # --- Relies on _extract_search_credentials which handles key1/key2 ---
        endpoint, key = _extract_search_credentials(conn)
        # print(f"[DEBUG] Attempting SearchIndexClient for dynamic list: {endpoint}")
        return SearchIndexClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    except Exception as e:
        print(f"[WARN] _index_client (for dynamic list) failed: {type(e).__name__} - {e}. Dynamic lists may be empty.")
        return None # Return None on ANY error during init

def _client(conn: CustomConnection, index_name: str) -> SearchClient:
    """Creates SearchClient for execution. Raises exceptions on failure."""
    # --- Relies on _extract_search_credentials which handles key1/key2 ---
    endpoint, key = _extract_search_credentials(conn)
    logger.info(f"Creating SearchClient for execution: Endpoint={endpoint}, Index='{index_name}'")
    try:
        return SearchClient(endpoint, index_name, AzureKeyCredential(key))
    except ClientAuthenticationError as e:
         logger.error(f"Authentication failed for SearchClient: {e}", exc_info=True)
         raise RuntimeError(f"Authentication failed connecting to Azure AI Search index '{index_name}'. Check API key (key2).") from e
    except Exception as e:
        logger.error(f"Failed to create SearchClient for index '{index_name}': {e}", exc_info=True)
        raise RuntimeError(f"Could not connect to Azure AI Search index '{index_name}'. Check endpoint (key1), key (key2), and index name. Error: {e}") from e

# ------------------------------------------------------------------ #
# 3.  dynamic-list helpers (Fail gracefully returning [])           #
# ------------------------------------------------------------------ #
# --- These all rely on the safe _index_client ---
def list_indexes(connection: Optional[CustomConnection] = None, **_) -> List[Dict[str, str]]:
    iclient = _index_client(connection)
    if not iclient: print("[WARN] Dynamic list 'list_indexes': Could not create index client."); return []
    try:
        return [{"value": idx.name, "display_value": idx.name} for idx in iclient.list_indexes()]
    except Exception as e: print(f"[WARN] Dynamic list 'list_indexes' failed: {type(e).__name__}."); return []

def _list_fields(connection: Optional[CustomConnection], index_name: Optional[str]):
    if not index_name: return None
    iclient = _index_client(connection)
    if not iclient: return None
    try:
        return iclient.get_index(index_name).fields
    except Exception as e: print(f"[WARN] Dynamic list helper '_list_fields' failed for '{index_name}': {type(e).__name__}."); return None

def list_vector_fields(connection: Optional[CustomConnection]=None, index_name: Optional[str]=None, **_) -> List[Dict[str, str]]:
    fields = _list_fields(connection, index_name)
    if not fields: return []
    try:
        names = [ f.name for f in fields if getattr(f,"vector_search_dimensions",None) or getattr(f,"dimensions",None) or (isinstance(f.type,str) and f.type.lower().startswith("collection(edm.single")) ]
        return [{"value": n, "display_value": n} for n in names]
    except Exception as e: print(f"[WARN] Dynamic list 'list_vector_fields' failed: {type(e).__name__}."); return []

def list_text_fields(connection: Optional[CustomConnection]=None, index_name: Optional[str]=None, **_) -> List[Dict[str, str]]:
    fields = _list_fields(connection, index_name)
    if not fields: return []
    try:
        names = [ f.name for f in fields if f.type==SearchFieldDataType.String and getattr(f,"searchable",False) ]
        return [{"value": n, "display_value": n} for n in names]
    except Exception as e: print(f"[WARN] Dynamic list 'list_text_fields' failed: {type(e).__name__}."); return []

def list_semantic_configs(connection: Optional[CustomConnection]=None, index_name: Optional[str]=None, **_) -> List[Dict[str, str]]:
    if not index_name: return []
    iclient = _index_client(connection)
    if not iclient: print("[WARN] Dynamic list 'list_semantic_configs': Could not create index client."); return []
    try:
        idx = iclient.get_index(index_name)
        semantic_search_config=getattr(idx,"semantic_search",None)
        configs=[]
        if semantic_search_config and getattr(semantic_search_config,"configurations",None):
            configs=[{"value":c.name,"display_value":c.name} for c in semantic_search_config.configurations]
        return configs
    except Exception as e: print(f"[WARN] Dynamic list 'list_semantic_configs' failed for '{index_name}': {type(e).__name__}."); return []

# ------------------------------------------------------------------ #
# 4.  embeddings helper (Handles AzureOpenAIConnection)              #
# ------------------------------------------------------------------ #
def _embeddings(conn: Union[AzureOpenAIConnection, OpenAIConnection], model_name: str):
    """Return LangChain embeddings client. Handles AzureOpenAIConnection."""
    conn_type = type(conn).__name__
    logger.info(f"Creating embeddings client: Type='{conn_type}', Model/Deployment='{model_name}'")
    try:
        # --- Handles standard AzureOpenAIConnection ---
        if isinstance(conn, AzureOpenAIConnection):
            endpoint = getattr(conn, "azure_endpoint", None) or getattr(conn, "api_base", None)
            api_key_from_conn = getattr(conn, "api_key", None)
            api_version = getattr(conn, "api_version", None) or "2024-02-01"
            if not endpoint: raise ValueError("AzureOpenAIConnection missing 'azure_endpoint' or 'api_base'.")
            if not api_key_from_conn: raise ValueError("AzureOpenAIConnection missing 'api_key'.")

            resolved_api_key = api_key_from_conn
            if api_key_from_conn == "***":
                logger.info("Resolving AOAI key from AZURE_OPENAI_API_KEY env var.")
                resolved_api_key = os.getenv("AZURE_OPENAI_API_KEY")
                if not resolved_api_key: raise ValueError("AOAI key is '***', but AZURE_OPENAI_API_KEY env var is not set.")

            return AzureOpenAIEmbeddings(
                azure_endpoint=endpoint, api_key=resolved_api_key, api_version=api_version, azure_deployment=model_name
            )
        elif isinstance(conn, OpenAIConnection): # Keep OpenAI handling for flexibility
            api_key_from_conn = getattr(conn, "api_key", None)
            base_url = getattr(conn, "base_url", None) or getattr(conn, "api_base", None)
            if not api_key_from_conn: raise ValueError("OpenAIConnection missing 'api_key'.")

            resolved_api_key = api_key_from_conn
            if api_key_from_conn == "***":
                logger.info("Resolving OpenAI key from OPENAI_API_KEY env var.")
                resolved_api_key = os.getenv("OPENAI_API_KEY")
                if not resolved_api_key: raise ValueError("OpenAI key is '***', but OPENAI_API_KEY env var is not set.")

            return OpenAIEmbeddings(api_key=resolved_api_key, base_url=base_url, model=model_name)
        else:
            raise TypeError(f"Internal Error: Unsupported embeddings connection type: {conn_type}")
    except (ValueError, TypeError) as config_err:
         logger.error(f"Embeddings client config error: {config_err}", exc_info=True); raise config_err
    except Exception as e:
        logger.error(f"Unexpected error creating embeddings client: {e}", exc_info=True); raise RuntimeError(f"Failed to init embedding client: {e}") from e

# ------------------------------------------------------------------ #
# 5.  small helper                                                   #
# ------------------------------------------------------------------ #
def _text_from_doc(doc: Dict[str, Any], text_field: str) -> str:
    """Extracts text, prioritizing specified field then common fallbacks."""
    if not isinstance(doc, dict): return ""
    return doc.get(text_field) or doc.get("content") or doc.get("text") or ""

# ------------------------------------------------------------------ #
# 6.  Search execution logic (Raises errors)                         #
# ------------------------------------------------------------------ #
def _execute_search(
    query_text: str, search_client: SearchClient, query_type: str, top_k: int, text_field: str, vector_field: str,
    search_filters: Optional[str], select_fields: Optional[List[str]], semantic_config: Optional[str],
    embeddings_connection: Optional[Union[AzureOpenAIConnection, OpenAIConnection]], embedding_model_name: str,
) -> List[Dict[str, Any]]:
    """Generates embedding if needed, executes search, returns formatted results. Raises exceptions on error."""
    # --- Keep execution logic robust, raising errors on failure ---
    logger.info(f"Executing search: Type='{query_type}', Query='{query_text[:50]}...'")
    vector: Optional[List[float]] = None; needs_vec = query_type in {"vector","hybrid","hybrid_semantic"}; needs_sem = query_type in {"semantic","hybrid_semantic"}
    if needs_vec:
        if not embeddings_connection: raise ValueError(f"Internal Error: Embeddings connection missing.")
        if not embedding_model_name: raise ValueError(f"Internal Error: Embedding model name missing.")
        logger.debug(f"Generating embedding: {embedding_model_name}...")
        try:
            embeddings_client = _embeddings(embeddings_connection, embedding_model_name)
            vector = embeddings_client.embed_query(query_text)
            if not vector: raise ValueError("Embedding returned None/empty.")
            logger.debug(f"Embedding generated len={len(vector)}.")
        except Exception as e: logger.error(f"Embedding failed: {e}", exc_info=True); raise ValueError(f"Embedding failed: {e}") from e
    if needs_sem and not semantic_config: raise ValueError(f"Semantic config needed for query_type '{query_type}'.")
    if needs_vec and not vector_field: raise ValueError(f"Vector field needed for query_type '{query_type}'.")
    params: Dict[str,Any]={"top":top_k,"filter":search_filters,"select":",".join(select_fields) if select_fields else None,"include_total_count":False}
    needs_text_search=query_type in {"keyword","semantic","hybrid","hybrid_semantic"}
    if needs_text_search: params["search_text"]=query_text
    if needs_vec:
        if not vector: raise RuntimeError("Internal Error: Vector not generated.")
        vector_query={"vector":vector,"k":top_k,"fields":vector_field}
        if hasattr(search_client,'search') and 'vector_queries' in getattr(getattr(search_client,'search',None),'__kwdefaults__',{}):
            params["vector_queries"]=[vector_query]
            if query_type=="vector": params.pop("top",None)
        else: params["vector"]=vector_query
    if needs_sem: params["semantic_configuration_name"]=semantic_config
    params={k:v for k,v in params.items() if v is not None}
    logger.debug(f"Sending search request to index '{search_client.index_name}'...")
    try:
        results=search_client.search(**params); results_list=list(results)
        logger.info(f"Search successful, received {len(results_list)} results.")
    except Exception as e:
        logger.error(f"Search request failed: {e}", exc_info=True)
        logger.error(f"Params (vector omitted): { {k:v for k,v in params.items() if k not in ['vector','vector_queries']} }")
        raise RuntimeError(f"Search request failed: {e}") from e
    output: List[Dict[str,Any]]=[]
    for doc in results_list:
         metadata={k:v for k,v in doc.items() if isinstance(doc,dict) and k!=text_field and not k.startswith("@search.")}
         if isinstance(doc,dict) and doc.get("@search.reranker_score") is not None: metadata["reranker_score"]=doc.get("@search.reranker_score")
         output.append({"text":_text_from_doc(doc,text_field),"score":doc.get("@search.score") if isinstance(doc,dict) else None,"metadata":metadata,})
    return output

# ------------------------------------------------------------------ #
# 7.  main PromptFlow tool (@tool function)                          #
# ------------------------------------------------------------------ #
@tool
def hw_ai_search_lookup_with_embed(
    connection: CustomConnection, # For Azure AI Search (key1/key2)
    index_name: str,
    queries: Union[str, List[str]],
    embeddings_connection: Optional[Union[AzureOpenAIConnection, OpenAIConnection]] = None, # For Embeddings
    embedding_model_name: str = DEFAULT_EMBED_MODEL,
    query_type: str = "hybrid",
    top_k: int = 3,
    text_field: str = "content",
    vector_field: str = "vector",
    search_filters: Optional[str] = None,
    select_fields: Optional[List[str]] = None,
    semantic_config: Optional[str] = None,
) -> List[List[Dict[str, Any]]]:
    """
    (Minimal Load Changes) Performs lookup on Azure AI Search, embedding queries internally.
    Handles CustomConnection(key1/key2) for Search & AzureOpenAIConnection for Embeddings.
    """
    run_id = os.getenv("PROMPTFLOW_RUN_ID", "local")
    logger.info(f"Starting HW AI Search Lookup Tool (Run ID: {run_id}).")

    # --- Input Validation ---
    query_type = (query_type or "hybrid").lower()
    if query_type not in VALID_QUERY_TYPES: raise ValueError(f"Invalid 'query_type': '{query_type}'.")
    if top_k <= 0: raise ValueError("'top_k' must be > 0")
    if isinstance(queries, str): query_list = [queries]
    elif isinstance(queries, list) and all(isinstance(q, str) for q in queries): query_list = queries
    elif isinstance(queries, list) and not queries: logger.warning("Empty query list."); return []
    else: raise TypeError("Invalid 'queries' type. Expected 'str' or 'List[str]'.")
    needs_vector_embedding = query_type in {"vector", "hybrid", "hybrid_semantic"}
    if needs_vector_embedding:
        if not embeddings_connection: raise ValueError(f"Embeddings connection required for query_type '{query_type}'.")
        if not isinstance(embeddings_connection, (AzureOpenAIConnection, OpenAIConnection)): raise TypeError(f"Invalid 'embeddings_connection' type.")
        if not embedding_model_name: raise ValueError("'embedding_model_name' required.")

    # --- Prepare Search Client (Raises RuntimeError on failure) ---
    search_client = _client(connection, index_name)
    logger.info(f"Azure AI Search client for index '{index_name}' initialized.")

    # --- Prepare for Parallel Execution ---
    all_results = []
    search_func_partial = partial( _execute_search, search_client=search_client, query_type=query_type, top_k=top_k,
        text_field=text_field, vector_field=vector_field, search_filters=search_filters, select_fields=select_fields,
        semantic_config=semantic_config, embeddings_connection=embeddings_connection, embedding_model_name=embedding_model_name,
    )
    parent_context = contextvars.copy_context(); def run_with_context(func,*args): return parent_context.run(func,*args)

    # --- Execute Tasks ---
    with ThreadPoolExecutor() as executor:
        logger.info(f"Submitting {len(query_list)} search tasks...")
        tasks = {executor.submit(run_with_context, search_func_partial, query): query for query in query_list}
        for future in tasks:
            query_text = tasks[future]; query_preview = f"'{query_text[:50]}...'"
            try:
                result_for_query: List[Dict] = future.result()
                logger.info(f"Task ({query_preview}) completed. Found {len(result_for_query)} results.")
                all_results.append(result_for_query)
            except Exception as e:
                logger.error(f"Search task ({query_preview}) failed in thread: {type(e).__name__}", exc_info=False)
                all_results.append([]) # Append empty list for failed task

    logger.info(f"Finished processing. Returning {len(all_results)} result lists.")
    return all_results