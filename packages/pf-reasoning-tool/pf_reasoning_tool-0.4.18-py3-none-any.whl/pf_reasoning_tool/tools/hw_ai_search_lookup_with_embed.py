# -*- coding: utf-8 -*-
"""
HW AI Search Lookup Tool (with Internal Embedding) - Robust Init
===============================================================
Performs keyword / semantic / vector / hybrid search over Azure AI Search.
Embeds input queries internally using Azure OpenAI or OpenAI connection.
Uses CustomConnection for Azure AI Search credentials.
Enhanced error handling and robust dynamic list initialization.
"""

from __future__ import annotations

import contextvars
import logging # Use logging instead of print for better tracking
import os
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import List, Dict, Any, Optional, Tuple, Union

from promptflow.core import tool
from promptflow.connections import (
    CustomConnection,
    AzureOpenAIConnection,
    OpenAIConnection,
)
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ClientAuthenticationError # Import specific error
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchFieldDataType
# Ensure langchain_openai is installed in the environment
try:
    from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
except ImportError:
     # This error will occur on import if langchain-openai is missing
     raise ImportError("Could not import langchain_openai. Please ensure 'langchain-openai' is installed in the PromptFlow environment.")


# Setup logger for the tool
logger = logging.getLogger(__name__)
# Set level based on environment or default - adjust as needed
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logger.setLevel(getattr(logging, log_level, logging.INFO))


# ------------------------------------------------------------------ #
# constants                                                          #
# ------------------------------------------------------------------ #
VALID_QUERY_TYPES = {"keyword", "semantic", "vector", "hybrid", "hybrid_semantic"}
DEFAULT_EMBED_MODEL = "text-embedding-3-large" # Default embedding model

# ------------------------------------------------------------------ #
# 1.  extract endpoint & key from CustomConnection (Checks env vars) #
# ------------------------------------------------------------------ #
def _extract_search_credentials(conn: CustomConnection) -> Tuple[str, str]:
    """Return (endpoint, api_key) from CustomConnection with env var fallback."""
    if not isinstance(conn, CustomConnection):
         # This case should ideally be caught by PF type validation, but good practice
         raise TypeError(f"Expected CustomConnection, got {type(conn).__name__}")

    c = dict(conn) # Convert to dict for easier access
    endpoint = (
        c.get("endpoint")
        or c.get("api_base")
        or c.get("azure_endpoint")
        or c.get("value1")
        or c.get("key1")
    )
    api_key_from_conn = (
        c.get("api_key")
        or c.get("value2")
        or c.get("key2")
        or c.get("key")
    )

    if not endpoint:
        raise ValueError(
            "Could not find Azure AI Search endpoint in CustomConnection. "
            "Searched keys: 'endpoint', 'api_base', 'azure_endpoint', 'value1', 'key1'."
        )
    if not api_key_from_conn:
        raise ValueError(
            "Could not find Azure AI Search API key in CustomConnection. "
            "Searched keys: 'api_key', 'value2', 'key2', 'key'."
        )

    # Handle placeholder key
    resolved_api_key = api_key_from_conn
    if api_key_from_conn == "***":
        logger.info("Found placeholder '***' for Azure AI Search key, attempting to resolve from AZURE_SEARCH_KEY environment variable.")
        resolved_api_key = os.getenv("AZURE_SEARCH_KEY")
        if not resolved_api_key:
            raise ValueError(
                "Azure AI Search API key is '***' in connection, but the "
                "'AZURE_SEARCH_KEY' environment variable is not set or is empty in the runtime."
            )

    # Final check on resolved key
    if not resolved_api_key:
         # Should not happen if logic above is correct, but belt-and-suspenders
         raise ValueError("Failed to determine a valid Azure AI Search API key.")

    logger.debug(f"Using AI Search Endpoint: {endpoint}") # Key is not logged
    return endpoint, resolved_api_key

# ------------------------------------------------------------------ #
# 2.  SDK clients (Robust _index_client)                             #
# ------------------------------------------------------------------ #
def _index_client(conn: Optional[CustomConnection]) -> Optional[SearchIndexClient]:
    """
    Creates SearchIndexClient safely for dynamic lists.
    Returns None if connection is None, invalid, or credentials fail.
    """
    if not conn:
        logger.debug("_index_client called with None connection. Returning None.")
        return None
    if not isinstance(conn, CustomConnection):
         # Log if type is wrong, though PF should enforce this via YAML type hint
         logger.warning(f"_index_client expected CustomConnection, got {type(conn).__name__}. Returning None.")
         return None

    try:
        # --- Attempt credential extraction INSIDE the try block ---
        endpoint, key = _extract_search_credentials(conn)
        logger.info(f"Attempting to create SearchIndexClient for dynamic list population (Endpoint: {endpoint})")
        client = SearchIndexClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        # Optional: Add a lightweight test call if absolutely necessary, e.g., client.get_service_statistics()
        # but this adds latency and may fail for other reasons. Best avoided if possible.
        logger.debug("SearchIndexClient created successfully for dynamic list.")
        return client

    except ValueError as cred_err:
        # Catch specific errors from _extract_search_credentials
        logger.warning(f"Could not extract valid credentials for dynamic list: {cred_err}. Check connection/env vars. Returning None.")
        return None # <<<<<<<<< Explicitly return None on credential errors
    except ClientAuthenticationError as auth_err:
        # Catch authentication errors from the SDK itself
        logger.warning(f"Authentication failed when creating SearchIndexClient for dynamic list: {auth_err}. Returning None.")
        return None # <<<<<<<<< Explicitly return None on auth errors
    except Exception as e:
        # Catch any other unexpected error during client creation
        logger.error(f"Unexpected error creating SearchIndexClient for dynamic list: {e}", exc_info=True)
        return None # <<<<<<<<< Return None for any other exception


def _client(conn: CustomConnection, index_name: str) -> SearchClient:
    """Creates SearchClient for actual execution, raises error on failure."""
    # No change needed here - failure during execution should propagate
    endpoint, key = _extract_search_credentials(conn)
    logger.info(f"Creating SearchClient for endpoint: {endpoint}, index: {index_name}")
    try:
        client = SearchClient(endpoint, index_name, AzureKeyCredential(key))
        # Optional: Add a simple test call like getting index stats if needed,
        # but it adds latency and might require different permissions.
        return client
    except Exception as e:
        logger.error(f"Failed to create SearchClient for index '{index_name}': {e}", exc_info=True)
        # Re-raise a more informative error potentially
        raise RuntimeError(f"Could not initialize connection to Azure AI Search index '{index_name}'. Check connection details and index existence. Error: {e}") from e


# ------------------------------------------------------------------ #
# 3.  dynamic-list helpers (Handle None client)                      #
# ------------------------------------------------------------------ #
def list_indexes(connection: Optional[CustomConnection] = None, **_) -> List[Dict[str, str]]:
    logger.debug("Dynamic list: Attempting list_indexes...")
    iclient = _index_client(connection) # Uses the safer version now
    if not iclient:
        logger.warning("Dynamic list: list_indexes cannot proceed, _index_client failed.")
        return [] # Return empty list if client creation failed
    try:
        indexes = list(iclient.list_indexes()) # Consume iterator
        logger.debug(f"Dynamic list: list_indexes found {len(indexes)} indexes.")
        return [{"value": idx.name, "display_value": idx.name} for idx in indexes]
    except Exception as e:
        logger.error(f"Dynamic list: list_indexes failed during SDK call: {e}", exc_info=True)
        return []

def _list_fields(connection: Optional[CustomConnection], index_name: Optional[str]):
    # Add check for empty index name string
    if not index_name:
        logger.debug("Dynamic list: _list_fields called with no index name.")
        return None
    logger.debug(f"Dynamic list: Attempting _list_fields for index: {index_name}...")
    iclient = _index_client(connection) # Uses the safer version
    if not iclient:
         logger.warning(f"Dynamic list: _list_fields cannot proceed for '{index_name}', _index_client failed.")
         return None
    try:
        index_obj = iclient.get_index(index_name)
        logger.debug(f"Dynamic list: _list_fields retrieved index '{index_name}'.")
        return index_obj.fields
    except Exception as e:
        # Log common errors like index not found
        logger.error(f"Dynamic list: _list_fields failed for index '{index_name}': {e}", exc_info=True)
        return None

def list_vector_fields(
    connection: Optional[CustomConnection] = None, index_name: Optional[str] = None, **_
) -> List[Dict[str, str]]:
    logger.debug(f"Dynamic list: Attempting list_vector_fields for index: {index_name}")
    fields = _list_fields(connection, index_name)
    if not fields:
        # Log already happened in _list_fields or _index_client
        return []
    names = [
        f.name
        for f in fields
        # Check for dimension attribute (new SDK) or Collection(Edm.Single) type (older definition)
        if getattr(f, "vector_search_dimensions", None) # Preferred check
        or getattr(f, "dimensions", None) # Fallback check
        or (isinstance(f.type, str) and f.type.lower().startswith("collection(edm.single"))
    ]
    logger.debug(f"Dynamic list: Found vector fields for '{index_name}': {names}")
    return [{"value": n, "display_value": n} for n in names]


def list_text_fields(
    connection: Optional[CustomConnection] = None, index_name: Optional[str] = None, **_
) -> List[Dict[str, str]]:
    logger.debug(f"Dynamic list: Attempting list_text_fields for index: {index_name}")
    fields = _list_fields(connection, index_name)
    if not fields:
        # Log already happened in _list_fields or _index_client
        return []
    names = [
        f.name
        for f in fields
        if f.type == SearchFieldDataType.String and getattr(f, "searchable", False)
    ]
    logger.debug(f"Dynamic list: Found text fields for '{index_name}': {names}")
    return [{"value": n, "display_value": n} for n in names]


def list_semantic_configs(
    connection: Optional[CustomConnection] = None, index_name: Optional[str] = None, **_
) -> List[Dict[str, str]]:
    logger.debug(f"Dynamic list: Attempting list_semantic_configs for index: {index_name}")
    # Need _index_client directly here
    iclient = _index_client(connection) # Uses safer version
    if not iclient or not index_name:
        if not iclient: logger.warning(f"Dynamic list: list_semantic_configs cannot proceed for '{index_name}', _index_client failed.")
        if not index_name: logger.debug("Dynamic list: list_semantic_configs cannot proceed, no index name.")
        return []
    try:
        idx = iclient.get_index(index_name)
        semantic_search_config = getattr(idx, "semantic_search", None)
        configs = []
        if semantic_search_config and getattr(semantic_search_config, "configurations", None):
            configs = [{"value": c.name, "display_value": c.name} for c in semantic_search_config.configurations]
        logger.debug(f"Dynamic list: Found semantic configs for '{index_name}': {[c['value'] for c in configs]}")
        return configs
    except Exception as e:
        logger.error(f"Dynamic list: list_semantic_configs failed for index '{index_name}': {e}", exc_info=True)
        return []


# ------------------------------------------------------------------ #
# 4.  embeddings helper (Enhanced Check)                             #
# ------------------------------------------------------------------ #
def _embeddings(conn: Union[AzureOpenAIConnection, OpenAIConnection], model_name: str):
    """Return LangChain embeddings client with enhanced checks."""
    conn_type = type(conn).__name__
    logger.info(f"Creating embeddings client for connection type: {conn_type}, model/deployment: {model_name}")

    try:
        if isinstance(conn, AzureOpenAIConnection):
            # Use getattr for safer access, provide default None
            endpoint = getattr(conn, "azure_endpoint", None) or getattr(conn, "api_base", None)
            api_key_from_conn = getattr(conn, "api_key", None)
            api_version = getattr(conn, "api_version", None) or "2024-02-01" # Default API version

            if not endpoint: raise ValueError("Azure endpoint ('azure_endpoint' or 'api_base') missing in AzureOpenAIConnection.")
            if not api_key_from_conn: raise ValueError("'api_key' missing in AzureOpenAIConnection.")

            resolved_api_key = api_key_from_conn
            if api_key_from_conn == "***":
                logger.info("Found placeholder '***' for Azure OpenAI key, resolving from AZURE_OPENAI_API_KEY env var.")
                resolved_api_key = os.getenv("AZURE_OPENAI_API_KEY")
                if not resolved_api_key:
                    raise ValueError("Azure OpenAI API key is '***', but 'AZURE_OPENAI_API_KEY' env var is not set.")

            logger.debug(f"Using Azure OpenAI Endpoint: {endpoint}, API Version: {api_version}")
            return AzureOpenAIEmbeddings(
                azure_endpoint=endpoint,
                api_key=resolved_api_key,
                api_version=api_version,
                azure_deployment=model_name, # model_name is deployment name here
            )

        elif isinstance(conn, OpenAIConnection):
            api_key_from_conn = getattr(conn, "api_key", None)
            base_url = getattr(conn, "base_url", None) or getattr(conn, "api_base", None) # Allow base_url override

            if not api_key_from_conn: raise ValueError("'api_key' missing in OpenAIConnection.")

            resolved_api_key = api_key_from_conn
            if api_key_from_conn == "***":
                logger.info("Found placeholder '***' for OpenAI key, resolving from OPENAI_API_KEY env var.")
                resolved_api_key = os.getenv("OPENAI_API_KEY")
                if not resolved_api_key:
                    raise ValueError("OpenAI API key is '***', but 'OPENAI_API_KEY' env var is not set.")

            logger.debug(f"Using OpenAI Base URL: {base_url or 'Default'}")
            return OpenAIEmbeddings(
                api_key=resolved_api_key,
                base_url=base_url, # Pass resolved base_url
                model=model_name, # model_name is model name here
            )
        else:
            # Should be caught by type hint, but good defense
            raise TypeError(f"Unsupported embeddings connection type: {conn_type}")

    except (ValueError, TypeError) as config_err:
         logger.error(f"Configuration error creating embeddings client: {config_err}")
         raise config_err # Re-raise config errors
    except Exception as e:
        logger.error(f"Unexpected error creating embeddings client: {e}", exc_info=True)
        raise RuntimeError(f"Failed to initialize embedding client: {e}") from e


# ------------------------------------------------------------------ #
# 5.  small helper                                                   #
# ------------------------------------------------------------------ #
def _text_from_doc(doc: Dict[str, Any], text_field: str) -> str:
    """Extracts text, prioritizing specified field then common fallbacks."""
    # Check if doc is a dict
    if not isinstance(doc, dict):
        logger.warning(f"Expected dict, got {type(doc)} when extracting text. Returning empty string.")
        return ""
    content = doc.get(text_field) or doc.get("content") or doc.get("text") or ""
    if not content:
         # Log only if the primary field was also missing
         if not doc.get(text_field):
              logger.warning(f"Could not find text in field '{text_field}' or fallbacks ('content', 'text') in doc: {list(doc.keys())[:5]}...") # Log first few keys
    return content

# ------------------------------------------------------------------ #
# 6.  Main search execution logic for a single query (More logging)  #
# ------------------------------------------------------------------ #
def _execute_search(
    query_text: str,
    # Required arguments passed via partial:
    client: SearchClient,
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
    """Generates embedding if needed, executes search, returns formatted results."""
    logger.info(f"Executing search for query_type '{query_type}', query: '{query_text[:50]}...'") # Log truncated query

    vector: Optional[List[float]] = None
    needs_vec = query_type in {"vector", "hybrid", "hybrid_semantic"}
    needs_sem = query_type in {"semantic", "hybrid_semantic"}

    # --- Generate Embedding if required ---
    if needs_vec:
        if embeddings_connection is None:
            # This should be caught earlier, but double-check
            raise ValueError(f"Embeddings connection is required for query_type '{query_type}' but was not provided.")
        logger.debug("Embedding required, attempting to generate...")
        try:
            embeddings_client = _embeddings(embeddings_connection, embedding_model_name)
            vector = embeddings_client.embed_query(query_text)
            logger.debug(f"Embedding generated successfully, vector length: {len(vector) if vector else 'None'}")
        except Exception as e:
            logger.error(f"Failed to generate embedding for query: '{query_text[:50]}...'. Error: {e}", exc_info=True)
            # Re-raise to fail this specific search execution clearly
            raise ValueError(f"Embedding generation failed: {e}") from e

    # --- Validate Inputs based on query_type ---
    if needs_sem and not semantic_config:
        raise ValueError(f"Semantic configuration name ('semantic_config') required for query_type '{query_type}'.")
    if needs_vec and not vector_field:
         raise ValueError(f"Vector field name ('vector_field') required for query_type '{query_type}'.")

    # --- Build search parameters ---
    logger.debug("Building search parameters...")
    params: Dict[str, Any] = {
        "top": top_k,
        "filter": search_filters,
        "select": ",".join(select_fields) if select_fields else None,
        "include_total_count": False, # Usually false for RAG
    }

    needs_text_search = query_type in {"keyword", "semantic", "hybrid", "hybrid_semantic"}

    if needs_text_search:
        params["search_text"] = query_text
    if needs_vec:
        if not vector: # Should exist if we got here
             raise RuntimeError("Internal Error: Vector required but not available.")
        vector_query = {
            "vector": vector,
            "k": top_k, # K for vector search
            "fields": vector_field, # Must be the correct field name in the index
        }
        # Check for vector_queries support (newer SDKs)
        # Use hasattr for safer check on potentially None client or missing attributes
        if hasattr(client, 'search') and 'vector_queries' in getattr(getattr(client, 'search', None), '__kwdefaults__', {}):
            logger.debug("Using 'vector_queries' parameter for search SDK.")
            params["vector_queries"] = [vector_query]
            if query_type == "vector": params.pop("top", None) # 'top' may conflict in pure vector
        else:
            # Fallback to older 'vector' parameter
            logger.debug("Using older 'vector' parameter for search SDK.")
            params["vector"] = vector_query

    if needs_sem:
        params["semantic_configuration_name"] = semantic_config
        # Optional: May need to explicitly set query type for semantic
        # params["query_type"] = "semantic" # Uncomment if required by your setup

    # Remove None values from params
    params = {k: v for k, v in params.items() if v is not None}
    logger.debug(f"Final search parameters (excluding vector): { {k:v for k,v in params.items() if k not in ['vector', 'vector_queries']} }")

    # --- Execute search ---
    logger.debug("Executing search request...")
    try:
        results = client.search(**params)
        results_list = list(results) # Consume iterator to catch potential errors early
        logger.info(f"Search successful, received {len(results_list)} results.")
    except Exception as e:
        logger.error(f"Azure AI Search request failed for query '{query_text[:50]}...'. Error: {e}", exc_info=True)
        logger.error(f"Search parameters used (excluding vector): { {k:v for k,v in params.items() if k not in ['vector', 'vector_queries']} }")
        # Check common issues:
        if needs_vec and vector_field: logger.error(f"Verify that '{vector_field}' is a valid, indexed vector field.")
        if search_filters: logger.error(f"Verify OData filter syntax: {search_filters}")
        if needs_sem and semantic_config: logger.error(f"Verify semantic configuration name: {semantic_config}")
        # Re-raise to fail this execution
        raise RuntimeError(f"Azure AI Search request failed: {e}") from e

    # --- Format output ---
    logger.debug("Formatting search results...")
    output: List[Dict[str, Any]] = []
    for i, doc in enumerate(results_list):
        metadata = {
            k: v
            for k, v in doc.items()
            if k != text_field and not k.startswith("@search.")
        }
        reranker_score = doc.get("@search.reranker_score")
        search_score = doc.get("@search.score")

        if reranker_score is not None:
             metadata["reranker_score"] = reranker_score # Add to metadata
        # Consider adding search_score to metadata too for clarity if needed
        # metadata["search_score"] = search_score

        extracted_text = _text_from_doc(doc, text_field)
        output.append(
            {
                "text": extracted_text,
                "score": search_score, # Primary score from search
                "metadata": metadata,
            }
        )
        if not extracted_text:
             # Reduce noise: only warn if primary field was requested but missing
             if not doc.get(text_field):
                  logger.warning(f"Result {i+1} had empty text extracted for field '{text_field}'.")

    logger.debug("Finished formatting results.")
    return output

# ------------------------------------------------------------------ #
# 7.  main PromptFlow tool (@tool function)                          #
# ------------------------------------------------------------------ #
@tool
def hw_ai_search_lookup_with_embed(
    # Inputs for Search Service
    connection: CustomConnection,
    index_name: str,
    # Inputs for Querying / Embedding
    queries: Union[str, List[str]],
    embeddings_connection: Optional[Union[AzureOpenAIConnection, OpenAIConnection]] = None,
    embedding_model_name: str = DEFAULT_EMBED_MODEL,
    # Search Configuration
    query_type: str = "hybrid",
    top_k: int = 3,
    text_field: str = "content",
    vector_field: str = "vector",
    search_filters: Optional[str] = None,
    select_fields: Optional[List[str]] = None,
    semantic_config: Optional[str] = None,
) -> List[List[Dict[str, Any]]]:
    """
    (Robust Init Version) Performs lookup on Azure AI Search, embedding queries internally.
    Uses CustomConnection for AI Search and AzureOpenAI/OpenAI Connection for embeddings.
    Accepts single or multiple queries, returns a list of lists of results. Enhanced logging.

    Returns: List[List[dict]], where each inner list contains results for a query.
             Each result dict has keys: {'text', 'score', 'metadata'}.
    """
    logger.info("Starting HW AI Search Lookup Tool execution.")
    # Log input parameters (be careful about sensitive info like filter content)
    logger.debug(f"Parameters: index_name='{index_name}', query_type='{query_type}', top_k={top_k}, "
                 f"text_field='{text_field}', vector_field='{vector_field}', "
                 f"embedding_model='{embedding_model_name}', "
                 f"has_search_connection={connection is not None}, "
                 f"has_embedding_connection={embeddings_connection is not None}, "
                 f"filter_present={search_filters is not None}, select='{select_fields}', semantic_config='{semantic_config}'")


    query_type = (query_type or "hybrid").lower()
    if query_type not in VALID_QUERY_TYPES:
        msg = f"Invalid 'query_type': '{query_type}'. Must be one of {VALID_QUERY_TYPES}"
        logger.error(msg)
        raise ValueError(msg)
    if top_k <= 0:
        msg = f"'top_k' must be greater than 0, got {top_k}."
        logger.error(msg)
        raise ValueError(msg)

    # --- Input Handling ---
    if isinstance(queries, str):
        query_list = [queries]
        logger.debug(f"Received single query string.")
    elif isinstance(queries, list) and all(isinstance(q, str) for q in queries):
         query_list = queries
         logger.debug(f"Received list of {len(query_list)} queries.")
    elif isinstance(queries, list) and not queries: # Empty list case
         logger.warning("Input 'queries' is an empty list. Returning empty list.")
         return []
    else:
        # Improve error message for non-string list items
        offending_type = "mixed types"
        if isinstance(queries, list):
            for item in queries:
                if not isinstance(item, str):
                    offending_type = type(item).__name__
                    break
        else:
            offending_type = type(queries).__name__
        msg = f"Invalid type for 'queries'. Expected 'str' or 'List[str]', but got {offending_type}."
        logger.error(msg)
        raise TypeError(msg)


    # --- Validate embedding connection if needed ---
    needs_vector_embedding = query_type in {"vector", "hybrid", "hybrid_semantic"}
    if needs_vector_embedding:
        logger.debug(f"Query type '{query_type}' requires embeddings.")
        if not embeddings_connection:
            msg = (f"An 'embeddings_connection' (AzureOpenAI or OpenAI) is required "
                   f"when query_type is '{query_type}', but none was provided.")
            logger.error(msg)
            raise ValueError(msg)
        # Check connection type compatibility early
        if not isinstance(embeddings_connection, (AzureOpenAIConnection, OpenAIConnection)):
             msg = f"Invalid type for 'embeddings_connection'. Expected AzureOpenAIConnection or OpenAIConnection, got {type(embeddings_connection).__name__}."
             logger.error(msg)
             raise TypeError(msg)

        if not embedding_model_name:
             msg = ("'embedding_model_name' is required when embeddings are needed, "
                    f"but it was empty or None.")
             logger.error(msg)
             raise ValueError(msg)
        logger.debug("Embeddings connection and model name provided.")


    # --- Prepare Search Client ---
    logger.debug("Initializing Azure AI Search client...")
    try:
        client = _client(connection, index_name)
        logger.info("Azure AI Search client initialized successfully.")
    except (ValueError, TypeError, RuntimeError) as client_err:
        # Error already logged in _client or _extract_search_credentials
        logger.critical(f"Failed to initialize Azure AI Search client. Cannot proceed. Error: {client_err}")
        # Re-raise the original error to fail the flow clearly
        raise client_err
    except Exception as e:
         # Catch any other unexpected error during client creation
         logger.critical(f"Unexpected error initializing Azure AI Search client: {e}", exc_info=True)
         raise RuntimeError(f"Unexpected error initializing Azure AI Search client: {e}") from e

    # --- Execute Search for each query (potentially in parallel) ---
    all_results = []
    logger.debug(f"Preparing to execute search for {len(query_list)} queries using ThreadPoolExecutor.")

    # Prepare partial function with fixed arguments for mapping
    search_func_partial = partial(
        _execute_search,
        # Pass required arguments that are constant for all queries
        client=client,
        query_type=query_type,
        top_k=top_k,
        text_field=text_field,
        vector_field=vector_field,
        search_filters=search_filters,
        select_fields=select_fields,
        semantic_config=semantic_config,
        embeddings_connection=embeddings_connection, # Pass the whole connection object
        embedding_model_name=embedding_model_name,
    )

    # Use ThreadPoolExecutor for potential parallelism
    parent_context = contextvars.copy_context()
    def run_with_context(func, *args):
        # Propagate contextvars to the thread
        return parent_context.run(func, *args)

    # Max workers can be adjusted if needed
    # max_workers = min(5, len(query_list)) # Example: Limit workers
    # with ThreadPoolExecutor(max_workers=max_workers) as executor:
    with ThreadPoolExecutor() as executor:
        # Map queries to the partial search function
        # The first argument to the partial function will be the query_text
        logger.info(f"Submitting {len(query_list)} search tasks to executor...")
        # Pass query itself as the first arg to the partial func via map/submit
        tasks = [executor.submit(run_with_context, search_func_partial, query) for query in query_list]

        # Retrieve results
        for i, task in enumerate(tasks):
            query_preview = f"'{query_list[i][:50]}...'" # For logging
            try:
                # result() will re-raise exceptions from the thread
                result_for_query = task.result() # This is List[Dict]
                logger.info(f"Successfully completed search task for query {i+1}/{len(tasks)} ({query_preview}). Found {len(result_for_query)} results.")
                all_results.append(result_for_query)
            except Exception as e:
                # Log the error associated with this specific query
                # Error should have been logged within _execute_search already, but log again here for task context
                logger.error(f"Search task failed for query {i+1}/{len(tasks)} ({query_preview}). See previous logs for details. Error type: {type(e).__name__}", exc_info=False) # Avoid duplicate traceback
                # Append an empty list for this failed query to maintain output structure
                all_results.append([])
                # Note: Depending on desired behavior, you might want to stop all execution
                # or collect all errors and raise a combined exception at the end.
                # Current behavior: Continue processing other queries.

    # --- Return results ---
    logger.info(f"Finished processing all {len(query_list)} queries. Returning results.")
    # Output structure is List[List[Dict]]
    return all_results