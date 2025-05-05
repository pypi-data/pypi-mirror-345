# -*- coding: utf-8 -*-
"""
HW AI Search Lookup Tool (Internal Embedding - Manual Input v1)
===============================================================
Performs keyword / semantic / vector / hybrid search over Azure AI Search.
Embeds input queries internally using Azure OpenAI or OpenAI connection.
Uses CustomConnection for Azure AI Search credentials.
Handles CustomConnection(key1/key2) for Search & standard AOAI/OAI Connections for Embeddings.
REMOVED DYNAMIC LISTS - User must manually specify index, fields, etc.
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
# Removed: SearchIndexClient, SearchFieldDataType

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
# 2.  SDK clients (Only SearchClient needed now)                     #
# ------------------------------------------------------------------ #
# Removed _index_client function as it's no longer used

def _client(conn: CustomConnection, index_name: str) -> SearchClient:
    """Creates the SearchClient needed for executing searches."""
    # --- Keep this function exactly as it was ---
    endpoint, key = _extract_search_credentials(conn)
    logger.info(f"Creating SearchClient for execution: Endpoint={endpoint}, Index='{index_name}'")
    try:
        client = SearchClient(endpoint, index_name, AzureKeyCredential(key))
        return client
    except ClientAuthenticationError as e:
        logger.error(f"Auth failed for SearchClient: {e}", exc_info=True)
        raise RuntimeError(f"Auth failed connecting to index '{index_name}'. Check API key.") from e
    except Exception as e:
        logger.error(f"Failed to create SearchClient for index '{index_name}': {e}", exc_info=True)
        raise RuntimeError(f"Could not connect to index '{index_name}'. Error: {e}") from e

# ------------------------------------------------------------------ #
# 3.  dynamic-list helpers                                           #
# ------------------------------------------------------------------ #
# --- ENTIRE SECTION REMOVED ---

# ------------------------------------------------------------------ #
# 4.  embeddings helper                                              #
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
    # Simplified warning: If the specified text_field is not found, warn.
    if text_field not in doc:
        logger.warning(f"Specified text_field '{text_field}' not found in document. Used fallbacks if available.")
    elif not content:
         logger.warning(f"Field '{text_field}' found but was empty.")
    return str(content) # Ensure string return

# ------------------------------------------------------------------ #
# 6.  Main search execution logic                                    #
# ------------------------------------------------------------------ #
def _execute_search(
    query_text: str,
    search_client: SearchClient,
    query_type: str,
    top_k: int,
    text_field: str,        # Must be provided correctly by user
    vector_field: str,      # Must be provided correctly by user (if needed)
    search_filters: Optional[str],
    select_fields: Optional[List[str]],
    semantic_config: Optional[str], # Must be provided correctly by user (if needed)
    embeddings_connection: Optional[Union[AzureOpenAIConnection, OpenAIConnection]],
    embedding_model_name: str,
) -> List[Dict[str, Any]]:
    """Generates embedding if needed, executes search, returns formatted results. Raises errors on failure."""
    # --- Logic remains largely the same, relies on inputs being correct ---
    logger.info(f"Executing search: Type='{query_type}', Query='{query_text[:50]}...'")
    vector: Optional[List[float]] = None
    needs_vec = query_type in {'vector', 'hybrid', 'hybrid_semantic'}
    needs_sem = query_type in {'semantic', 'hybrid_semantic'}

    # --- Embedding Generation (No changes needed here) ---
    if needs_vec:
        if not embeddings_connection:
            raise ValueError(f"Embeddings connection is required for query_type '{query_type}' but was not provided.")
        if not embedding_model_name:
            raise ValueError(f"Embedding model name is required for query_type '{query_type}' but was not provided.")
        if not vector_field:
             raise ValueError(f"Vector field name is required for query_type '{query_type}' but was not provided.")
        logger.debug(f'Generating embedding using model/deployment: {embedding_model_name}...')
        try:
            embeddings_client = _embeddings(embeddings_connection, embedding_model_name)
            vector = embeddings_client.embed_query(query_text)
            if not isinstance(vector, list) or not vector: # More robust check
                raise ValueError('Embedding generation returned an invalid result (None or empty list).')
            logger.debug(f'Embedding generated successfully, length={len(vector)}.')
        except Exception as e:
            logger.error(f'Embedding generation failed: {e}', exc_info=True)
            # Provide more context in the error
            raise ValueError(f"Failed to generate embedding for query using model '{embedding_model_name}'. Error: {e}") from e

    # --- Input Validation (Crucial now) ---
    if needs_sem and not semantic_config:
        raise ValueError(f"Semantic configuration name is required for query_type '{query_type}' but was not provided.")
    # vector_field check moved to embedding generation block above

    # --- Search Parameter Construction (No changes needed here) ---
    params: Dict[str, Any] = {
        'top': top_k,
        'filter': search_filters,
        'select': ','.join(select_fields) if select_fields else None,
        'include_total_count': False,
    }
    needs_text_search = query_type in {'keyword', 'semantic', 'hybrid', 'hybrid_semantic'}
    if needs_text_search:
        params['search_text'] = query_text # Use the original query text

    if needs_vec:
        # Ensure vector is not None before creating the query object
        if vector is None:
             raise RuntimeError("Internal Error: Vector was required but is None before search.") # Should be caught earlier
        vector_query = {'vector': vector, 'k': top_k, 'fields': vector_field} # vector_field must be correct now
        params['vector_queries'] = [vector_query] # Use the newer vector_queries parameter
        # Remove conflicting/redundant parameters based on query type
        if query_type == 'vector':
            params.pop('top', None) # k in vector_query controls results for pure vector
            params.pop('search_text', None) # No text search needed
        # For hybrid, both 'top' (for text) and 'k' (for vector) are used by the service

    if needs_sem:
        params['query_type'] = 'semantic' # Explicitly set for semantic/hybrid_semantic
        params['semantic_configuration_name'] = semantic_config # semantic_config must be correct now

    # remove any None values
    params = {k: v for k, v in params.items() if v is not None}

    # --- Execute Search (Error messages might be more direct now) ---
    logger.debug(f"Sending search request to index '{search_client.index_name}' with params (vector omitted): "
                 f"{ {k: v for k, v in params.items() if k != 'vector_queries'} }")
    try:
        results = search_client.search(**params)
        results_list = list(results)
        logger.info(f'Search successful, received {len(results_list)} results.')
    except Exception as e:
        logger.error(f'Search request failed: {e}', exc_info=True)
        logger.error(f"Failed Search Params (vector omitted): { {k: v for k, v in params.items() if k != 'vector_queries'} }")
        # Add hints focusing on user-provided names
        if index_name: logger.error(f"Hint: Verify the index name ('{index_name}') exists and the connection key has permissions.")
        if needs_vec and vector_field: logger.error(f"Hint: Verify the vector field name ('{vector_field}') exists in index '{index_name}' and matches the embedding dimensions.")
        if needs_sem and semantic_config: logger.error(f"Hint: Verify the semantic configuration name ('{semantic_config}') exists in index '{index_name}'.")
        if text_field: logger.error(f"Hint: Verify the text field name ('{text_field}') exists in the index.")
        if search_filters: logger.error(f"Hint: Verify OData filter syntax ('{search_filters}').")
        raise RuntimeError(f"Search request failed for index '{index_name}'. Error: {e}") from e

    # --- Format Results (No changes needed here) ---
    output: List[Dict[str, Any]] = []
    for doc_dict in results_list:
        # Ensure doc is a dict before processing
        if not isinstance(doc_dict, dict):
            logger.warning(f"Received non-dictionary item in search results: {type(doc_dict)}. Skipping.")
            continue

        doc_text = _text_from_doc(doc_dict, text_field) # Uses the user-provided text_field
        doc_vector = doc_dict.get(vector_field) if vector_field else None
        doc_score = doc_dict.get('@search.score')
        reranker_score = doc_dict.get('@search.reranker_score') # Specific to semantic

        metadata = {
            k: v for k, v in doc_dict.items()
            if k != text_field and k != vector_field and not k.startswith('@search.')
        }
        # Add scores to metadata if they exist
        if reranker_score is not None:
            metadata['reranker_score'] = reranker_score
        # Optionally add original score to metadata too, or keep it separate
        # metadata['search_score'] = doc_score

        output.append({
            'text': doc_text,
            'vector': doc_vector, # Include the vector if retrieved
            'score': doc_score, # Original search score
            'metadata': metadata,
            'original_entity': doc_dict # Keep the full original document
        })

    return output


# ------------------------------------------------------------------ #
# 7.  main PromptFlow tool (@tool function)                          #
# ------------------------------------------------------------------ #
@tool
def hw_ai_search_lookup_with_embed(
    # Inputs requiring manual entry now:
    connection: CustomConnection,
    index_name: str,            # User MUST provide the correct index name
    queries: Union[str, List[str]],
    embeddings_connection: Optional[Union[AzureOpenAIConnection, OpenAIConnection]]=None,
    embedding_model_name: str=DEFAULT_EMBED_MODEL,
    query_type: str="hybrid",
    top_k: int=3,
    text_field: str="content",   # User can override, must be correct text field
    vector_field: str="vector",  # User can override, must be correct vector field (if needed)
    search_filters: Optional[str]=None,
    select_fields: Optional[List[str]]=None,
    semantic_config: Optional[str]=None, # User must provide correct name (if needed)
) -> List[List[Dict[str, Any]]]:
    """
    (Manual Input v1) Performs lookup on Azure AI Search, embedding queries internally.
    Requires manual input for index name, text field, vector field, and semantic config.
    """
    # --- Keep this function largely as it was, input validation happens in _execute_search ---
    run_id = os.getenv("PROMPTFLOW_RUN_ID", "local")
    logger.info(f"Starting HW AI Search Lookup Tool (Manual Input v1 - Run ID: {run_id}).")
    logger.debug(f"Params: index='{index_name}', query_type='{query_type}', top_k={top_k}, text_field='{text_field}', vector_field='{vector_field}', semantic_config='{semantic_config}'...")

    # Basic validation
    query_type = (query_type or "hybrid").lower()
    if query_type not in VALID_QUERY_TYPES:
        raise ValueError(f"Invalid 'query_type': '{query_type}'. Must be one of {VALID_QUERY_TYPES}.")
    if not index_name:
         raise ValueError("'index_name' cannot be empty.")
    if top_k <= 0:
        raise ValueError("'top_k' must be > 0")

    # Query processing
    if isinstance(queries, str):
        query_list = [queries]
    elif isinstance(queries, list) and all(isinstance(q, str) for q in queries):
        query_list = queries
    elif isinstance(queries, list) and not queries:
        logger.warning("Received an empty list for 'queries'. Returning empty results.")
        return []
    else:
        raise TypeError(f"Invalid 'queries' type: {type(queries).__name__}. Expected 'str' or 'List[str]'.")

    # Check embedding requirements *before* creating client/threads
    needs_vector_embedding = query_type in {"vector", "hybrid", "hybrid_semantic"}
    if needs_vector_embedding:
        if not embeddings_connection:
            raise ValueError(f"Embeddings connection ('embeddings_connection') is required for query_type '{query_type}'.")
        if not isinstance(embeddings_connection, (AzureOpenAIConnection, OpenAIConnection)):
            raise TypeError(f"Invalid 'embeddings_connection' type: {type(embeddings_connection).__name__}. Expected AzureOpenAIConnection or OpenAIConnection.")
        if not embedding_model_name:
            raise ValueError(f"Embedding model name ('embedding_model_name') is required when embeddings_connection is provided.")
        if not vector_field:
             raise ValueError(f"Vector field name ('vector_field') is required for query_type '{query_type}'.")

    # Check semantic requirements
    needs_semantic = query_type in {"semantic", "hybrid_semantic"}
    if needs_semantic and not semantic_config:
        raise ValueError(f"Semantic configuration name ('semantic_config') is required for query_type '{query_type}'.")


    # Create search client (will raise error if connection or index name is bad)
    search_client = _client(connection, index_name)
    logger.info(f"Search client initialized successfully for index '{index_name}'.")

    all_results = []
    # --- Threading logic remains the same ---
    search_func_partial = partial(
        _execute_search,
        search_client=search_client,
        query_type=query_type,
        top_k=top_k,
        text_field=text_field,
        vector_field=vector_field,
        search_filters=search_filters,
        select_fields=select_fields,
        semantic_config=semantic_config,
        embeddings_connection=embeddings_connection,
        embedding_model_name=embedding_model_name,
    )

    parent_context = contextvars.copy_context()
    def run_with_context(func, *args):
        return parent_context.run(func, *args)

    # Use ThreadPoolExecutor for concurrent searches
    with ThreadPoolExecutor() as executor:
        logger.info(f"Submitting {len(query_list)} search tasks to thread pool...")
        # Create tasks {future: query_text}
        tasks = {executor.submit(run_with_context, search_func_partial, query): query for query in query_list}

        results_map = {} # Store results keyed by original query to maintain order if needed
        for future in tasks:
            query_text = tasks[future]
            query_preview = f"'{query_text[:50]}...'" if len(query_text) > 50 else f"'{query_text}'"
            try:
                # result() blocks until the future completes and raises exceptions if the task failed
                result_for_query: List[Dict] = future.result()
                logger.info(f"Search task for query {query_preview} completed successfully. Found {len(result_for_query)} results.")
                results_map[query_text] = result_for_query
            except Exception as e:
                # Log the specific error from the thread
                logger.error(f"Search task for query {query_preview} failed in thread: {type(e).__name__} - {e}", exc_info=False) # exc_info=False to avoid duplicate stack trace if already logged in _execute_search
                results_map[query_text] = [] # Append an empty list for failed queries

        # Reconstruct the results list in the original order of queries
        all_results = [results_map[query] for query in query_list]


    logger.info(f"Finished processing all {len(query_list)} queries. Returning {len(all_results)} result lists.")
    return all_results