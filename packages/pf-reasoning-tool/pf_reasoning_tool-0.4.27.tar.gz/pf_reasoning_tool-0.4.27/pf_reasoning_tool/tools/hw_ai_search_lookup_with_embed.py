# -*- coding: utf-8 -*-
"""
HW AI Search Lookup Tool (Internal Embedding - Robust Init - Syntax Fixed v3)
===========================================================================
Performs keyword / semantic / vector / hybrid search over Azure AI Search.
Embeds input queries internally using Azure OpenAI or OpenAI connection.
Uses CustomConnection for Azure AI Search credentials.
Handles CustomConnection(key1/key2) for Search & standard AOAI/OAI Connections for Embeddings.
Corrected ALL indentation syntax errors.
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
    OpenAIConnection,
)
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ClientAuthenticationError
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchFieldDataType
# Embedding library import - Ensure installed
try:
    from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
except ImportError:
     raise ImportError("Could not import langchain_openai. Please ensure 'langchain-openai' is installed in the PromptFlow execution environment.")


# Setup logger for the tool
logger = logging.getLogger(__name__)
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logger.setLevel(getattr(logging, log_level, logging.INFO))


# ------------------------------------------------------------------ #
# constants                                                          #
# ------------------------------------------------------------------ #
VALID_QUERY_TYPES = {"keyword", "semantic", "vector", "hybrid", "hybrid_semantic"}
DEFAULT_EMBED_MODEL = "text-embedding-3-large"

# ------------------------------------------------------------------ #
# 1.  extract endpoint & key from CustomConnection (Checks env vars) #
# ------------------------------------------------------------------ #
def _extract_search_credentials(conn: CustomConnection) -> Tuple[str, str]:
    # --- Keep this function exactly as it was ---
    if not isinstance(conn, CustomConnection): raise TypeError(f"Expected CustomConnection, got {type(conn).__name__}")
    c = dict(conn)
    endpoint = ( c.get("endpoint") or c.get("api_base") or c.get("azure_endpoint") or c.get("value1") or c.get("key1") )
    api_key_from_conn = ( c.get("api_key") or c.get("value2") or c.get("key2") or c.get("key") )
    if not endpoint: raise ValueError("Could not find Azure AI Search endpoint in CustomConnection.")
    if not api_key_from_conn: raise ValueError("Could not find Azure AI Search API key in CustomConnection.")
    resolved_api_key = api_key_from_conn
    if api_key_from_conn == "***":
        logger.info("Found placeholder '***' for Azure AI Search key, resolving from AZURE_SEARCH_KEY env var.")
        resolved_api_key = os.getenv("AZURE_SEARCH_KEY")
        if not resolved_api_key: raise ValueError("Azure AI Search API key is '***', but 'AZURE_SEARCH_KEY' env var is not set.")
    if not resolved_api_key: raise ValueError("Failed to determine a valid Azure AI Search API key.")
    logger.debug(f"Using AI Search Endpoint: {endpoint}")
    return endpoint, resolved_api_key

# ------------------------------------------------------------------ #
# 2.  SDK clients (Robust _index_client)                             #
# ------------------------------------------------------------------ #
def _index_client(conn: Optional[CustomConnection]) -> Optional[SearchIndexClient]:
    # --- Keep this function exactly as it was ---
    if not conn: logger.debug("_index_client called with None connection."); return None
    if not isinstance(conn, CustomConnection): logger.warning(f"_index_client expected CustomConnection, got {type(conn).__name__}."); return None
    try:
        endpoint, key = _extract_search_credentials(conn)
        logger.info(f"Attempting SearchIndexClient for dynamic list (Endpoint: {endpoint})")
        client = SearchIndexClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        logger.debug("SearchIndexClient created successfully for dynamic list.")
        return client
    except ValueError as cred_err: logger.warning(f"Cred extraction failed for dynamic list: {cred_err}."); return None
    except ClientAuthenticationError as auth_err: logger.warning(f"Auth failed creating SearchIndexClient for dynamic list: {auth_err}."); return None
    except Exception as e: logger.error(f"Unexpected error creating SearchIndexClient for dynamic list: {e}", exc_info=True); return None

def _client(conn: CustomConnection, index_name: str) -> SearchClient:
    # --- Keep this function exactly as it was ---
    endpoint, key = _extract_search_credentials(conn)
    logger.info(f"Creating SearchClient for execution: Endpoint={endpoint}, Index='{index_name}'")
    try:
        client = SearchClient(endpoint, index_name, AzureKeyCredential(key))
        return client
    except ClientAuthenticationError as e: logger.error(f"Auth failed for SearchClient: {e}", exc_info=True); raise RuntimeError(f"Auth failed connecting to index '{index_name}'. Check API key.") from e
    except Exception as e: logger.error(f"Failed to create SearchClient for index '{index_name}': {e}", exc_info=True); raise RuntimeError(f"Could not connect to index '{index_name}'. Error: {e}") from e

# ------------------------------------------------------------------ #
# 3.  dynamic-list helpers (Handle None client)                      #
# ------------------------------------------------------------------ #
# --- Keep these functions exactly as they were ---
def list_indexes(connection: Optional[CustomConnection] = None, **_) -> List[Dict[str, str]]:
    logger.debug("Dynamic list: list_indexes...")
    iclient = _index_client(connection)
    if not iclient: logger.warning("list_indexes cannot proceed, _index_client failed."); return []
    try: indexes = list(iclient.list_indexes()); logger.debug(f"list_indexes found {len(indexes)} indexes."); return [{"value": idx.name, "display_value": idx.name} for idx in indexes]
    except Exception as e: logger.error(f"list_indexes SDK call failed: {e}", exc_info=True); return []

def _list_fields(connection: Optional[CustomConnection], index_name: Optional[str]):
    if not index_name: logger.debug("_list_fields: No index name."); return None
    logger.debug(f"_list_fields for index: {index_name}...")
    iclient = _index_client(connection)
    if not iclient: logger.warning(f"_list_fields cannot proceed for '{index_name}', _index_client failed."); return None
    try: index_obj = iclient.get_index(index_name); logger.debug(f"_list_fields retrieved index '{index_name}'."); return index_obj.fields
    except Exception as e: logger.error(f"_list_fields failed for index '{index_name}': {e}", exc_info=True); return None

def list_vector_fields(connection: Optional[CustomConnection]=None, index_name: Optional[str]=None, **_) -> List[Dict[str, str]]:
    logger.debug(f"Dynamic list: list_vector_fields for index: {index_name}")
    fields = _list_fields(connection, index_name)
    if not fields: return []
    names = [ f.name for f in fields if getattr(f,"vector_search_dimensions",None) or getattr(f,"dimensions",None) or (isinstance(f.type,str) and f.type.lower().startswith("collection(edm.single"))]
    logger.debug(f"Found vector fields: {names}")
    return [{"value": n, "display_value": n} for n in names]

def list_text_fields(connection: Optional[CustomConnection]=None, index_name: Optional[str]=None, **_) -> List[Dict[str, str]]:
    logger.debug(f"Dynamic list: list_text_fields for index: {index_name}")
    fields = _list_fields(connection, index_name)
    if not fields: return []
    names = [ f.name for f in fields if f.type==SearchFieldDataType.String and getattr(f,"searchable",False)]
    logger.debug(f"Found text fields: {names}")
    return [{"value": n, "display_value": n} for n in names]

def list_semantic_configs(connection: Optional[CustomConnection]=None, index_name: Optional[str]=None, **_) -> List[Dict[str, str]]:
    logger.debug(f"Dynamic list: list_semantic_configs for index: {index_name}")
    iclient = _index_client(connection)
    if not iclient or not index_name: logger.warning(f"list_semantic_configs cannot proceed (client={iclient is not None}, index='{index_name}')."); return []
    try:
        idx = iclient.get_index(index_name)
        semantic_search_config=getattr(idx,"semantic_search",None)
        configs=[]
        if semantic_search_config and getattr(semantic_search_config,"configurations",None): configs=[{"value":c.name,"display_value":c.name} for c in semantic_search_config.configurations]
        logger.debug(f"Found semantic configs: {[c['value'] for c in configs]}")
        return configs
    except Exception as e: logger.error(f"list_semantic_configs failed: {e}", exc_info=True); return []

# ------------------------------------------------------------------ #
# 4.  embeddings helper (Indentation was already correct here)       #
# ------------------------------------------------------------------ #
def _embeddings(conn: Union[AzureOpenAIConnection, OpenAIConnection], model_name: str):
    # --- Keep this function exactly as it was ---
    conn_type=type(conn).__name__; logger.info(f"Creating embeddings client: Type='{conn_type}', Model/Deployment='{model_name}'")
    try:
        if isinstance(conn,AzureOpenAIConnection):
            endpoint=getattr(conn,"azure_endpoint",None) or getattr(conn,"api_base",None); api_key_from_conn=getattr(conn,"api_key",None); api_version=getattr(conn,"api_version",None) or "2024-02-01"
            if not endpoint: raise ValueError("AzureOpenAIConnection requires 'azure_endpoint' or 'api_base'.")
            if not api_key_from_conn: raise ValueError("AzureOpenAIConnection requires 'api_key'.")
            resolved_api_key=api_key_from_conn
            if api_key_from_conn=="***": logger.info("Resolving AOAI key from env var."); resolved_api_key=os.getenv("AZURE_OPENAI_API_KEY");
            if not resolved_api_key: raise ValueError("AOAI key is '***', but env var not set.")
            logger.debug(f"Using AOAI Endpoint: {endpoint}, API Version: {api_version}")
            return AzureOpenAIEmbeddings(azure_endpoint=endpoint,api_key=resolved_api_key,api_version=api_version,azure_deployment=model_name,)
        elif isinstance(conn,OpenAIConnection):
            api_key_from_conn=getattr(conn,"api_key",None); base_url=getattr(conn,"base_url",None) or getattr(conn,"api_base",None)
            if not api_key_from_conn: raise ValueError("OpenAIConnection requires 'api_key'.")
            resolved_api_key=api_key_from_conn
            if api_key_from_conn=="***": logger.info("Resolving OpenAI key from env var."); resolved_api_key=os.getenv("OPENAI_API_KEY");
            if not resolved_api_key: raise ValueError("OpenAI key is '***', but env var not set.")
            logger.debug(f"Using OpenAI Base URL: {base_url or 'Default'}")
            return OpenAIEmbeddings(api_key=resolved_api_key,base_url=base_url,model=model_name,)
        else: raise TypeError(f"Unsupported embeddings connection type: {conn_type}")
    except(ValueError,TypeError) as config_err: logger.error(f"Embeddings client config error: {config_err}"); raise config_err
    except Exception as e: logger.error(f"Unexpected error creating embeddings client: {e}",exc_info=True); raise RuntimeError(f"Failed to init embedding client: {e}") from e

# ------------------------------------------------------------------ #
# 5.  small helper                                                   #
# ------------------------------------------------------------------ #
def _text_from_doc(doc: Dict[str, Any], text_field: str) -> str:
    # --- Keep this function exactly as it was ---
    if not isinstance(doc,dict): logger.warning(f"Expected dict, got {type(doc)}."); return ""
    content=doc.get(text_field) or doc.get("content") or doc.get("text") or ""
    if not content and not doc.get(text_field): logger.warning(f"Could not find text in field '{text_field}' or fallbacks.")
    return content

# ------------------------------------------------------------------ #
# 6.  Main search execution logic (INDENTATION FIXED)                #
# ------------------------------------------------------------------ #
def _execute_search(
    query_text: str,
    search_client: SearchClient,
    query_type: str,
    top_k: int,
    text_field: str,
    vector_field: str,
    search_filters: Optional[str],
    select_fields: Optional[List[str]],
    semantic_config: Optional[str],
    embeddings_connection: Optional[Union[AzureOpenAIConnection, OpenAIConnection]],
    embedding_model_name: str,
) -> List[Dict[str, Any]]:
    """Generates embedding if needed, executes search, returns formatted results.  Raises errors on failure."""
    logger.info(f"Executing search: Type='{query_type}', Query='{query_text[:50]}...'")
    vector: Optional[List[float]] = None
    needs_vec = query_type in {'vector', 'hybrid', 'hybrid_semantic'}
    needs_sem = query_type in {'semantic', 'hybrid_semantic'}

    if needs_vec:
        if not embeddings_connection:
            raise ValueError('Internal Error: Embeddings connection missing.')
        if not embedding_model_name:
            raise ValueError('Internal Error: Embedding model name missing.')
        logger.debug(f'Generating embedding: {embedding_model_name}...')
        try:
            embeddings_client = _embeddings(embeddings_connection, embedding_model_name)
            vector = embeddings_client.embed_query(query_text)
            if not vector:
                raise ValueError('Embedding returned None/empty.')
            logger.debug(f'Embedding len={len(vector)}.')
        except Exception as e:
            logger.error(f'Embedding failed: {e}', exc_info=True)
            raise ValueError(f'Embedding failed: {e}') from e

    if needs_sem and not semantic_config:
        raise ValueError('Semantic config needed.')
    if needs_vec and not vector_field:
        raise ValueError('Vector field needed.')

    params: Dict[str, Any] = {
        'top': top_k,
        'filter': search_filters,
        'select': ','.join(select_fields) if select_fields else None,
        'include_total_count': False,
    }
    needs_text_search = query_type in {'keyword', 'semantic', 'hybrid', 'hybrid_semantic'}
    if needs_text_search:
        params['search_text'] = query_text

    if needs_vec:
        vector_query = {'vector': vector, 'k': top_k, 'fields': vector_field}
        if hasattr(search_client, 'search') and 'vector_queries' in getattr(search_client.search, '__kwdefaults__', {}):
            params['vector_queries'] = [vector_query]
        if query_type == 'vector':
            params.pop('top', None)
        else:
            params['vector'] = vector_query

    if needs_sem:
        params['semantic_configuration_name'] = semantic_config

    # remove any None values
    params = {k: v for k, v in params.items() if v is not None}

    logger.debug(f"Sending search request to index '{search_client.index_name}'...")
    try:
        results = search_client.search(**params)
        results_list = list(results)
        logger.info(f'Search successful, received {len(results_list)} results.')
    except Exception as e:
        logger.error(f'Search request failed: {e}', exc_info=True)
        logger.error(f'Params (vector omitted): {[ (k, v) for k, v in params.items() if k not in {"vector","vector_queries"} ]}')
        if needs_vec and vector_field:
            logger.error(f"Hint: Verify vector field name ('{vector_field}') and dimensions.")
        if search_filters:
            logger.error(f"Hint: Verify OData filter syntax ('{search_filters}').")
        if needs_sem and semantic_config:
            logger.error(f"Hint: Verify semantic config name ('{semantic_config}').")
        raise RuntimeError(f'Search request failed: {e}') from e

    # Format and return
    output: List[Dict[str, Any]] = []
    for doc in results_list:
        metadata = {
            k: v for k, v in doc.items()
            if isinstance(doc, dict)
               and k != text_field
               and not k.startswith('@search.')
        }
        if isinstance(doc, dict) and doc.get('@search.reranker_score') is not None:
            metadata['reranker_score'] = doc.get('@search.reranker_score')
        output.append({
            'text': _text_from_doc(doc, text_field),
            'vector': doc.get(vector_field) if isinstance(doc, dict) else None,
            'score': doc.get('@search.score') if isinstance(doc, dict) else None,
            'metadata': metadata,
            'original_entity': doc
        })

    return output

# ------------------------------------------------------------------ #
# 7.  main PromptFlow tool (@tool function)                          #
# ------------------------------------------------------------------ #
@tool
def hw_ai_search_lookup_with_embed(
    connection: CustomConnection, index_name: str, queries: Union[str, List[str]],
    embeddings_connection: Optional[Union[AzureOpenAIConnection, OpenAIConnection]]=None,
    embedding_model_name: str=DEFAULT_EMBED_MODEL, query_type: str="hybrid", top_k: int=3,
    text_field: str="content", vector_field: str="vector", search_filters: Optional[str]=None,
    select_fields: Optional[List[str]]=None, semantic_config: Optional[str]=None,
) -> List[List[Dict[str, Any]]]:
    """
    (Robust Init - Syntax Fixed v3) Performs lookup on Azure AI Search, embedding queries internally.
    """
    # --- Keep this function exactly as it was ---
    run_id = os.getenv("PROMPTFLOW_RUN_ID", "local"); logger.info(f"Starting HW AI Search Lookup Tool (Run ID: {run_id}).")
    logger.debug(f"Params: index='{index_name}', query_type='{query_type}', top_k={top_k}...")
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
    search_client = _client(connection, index_name); logger.info(f"Search client initialized for index '{index_name}'.")
    all_results = []
    search_func_partial = partial( _execute_search, search_client=search_client, query_type=query_type, top_k=top_k, text_field=text_field, vector_field=vector_field, search_filters=search_filters, select_fields=select_fields, semantic_config=semantic_config, embeddings_connection=embeddings_connection, embedding_model_name=embedding_model_name,)
    parent_context = contextvars.copy_context();
    def run_with_context(func, *args): return parent_context.run(func,*args) # Correct syntax
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
                logger.error(f"Search task ({query_preview}) failed in thread: {type(e).__name__} - {e}", exc_info=False)
                all_results.append([])
    logger.info(f"Finished processing. Returning {len(all_results)} result lists.")
    return all_results