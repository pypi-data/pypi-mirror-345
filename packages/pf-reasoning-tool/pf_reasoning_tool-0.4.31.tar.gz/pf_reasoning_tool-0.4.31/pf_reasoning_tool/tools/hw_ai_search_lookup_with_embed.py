# -*- coding: utf-8 -*-
"""
HW AI Search Lookup Tool (Internal Embedding - Manual Input v1 - patched)
=========================================================================
Performs keyword / semantic / vector / hybrid search over Azure AI Search.  
Embeds input queries internally using Azure OpenAI or OpenAI connection.  
Uses CustomConnection for Azure AI Search credentials.  
REMOVED DYNAMIC LISTS – user must manually specify index, fields, etc.  
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

# Embedding library import – ensure installed
try:
    from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
except ImportError:
    raise ImportError(
        'Could not import langchain_openai.  Please ensure "langchain-openai" is installed in the PromptFlow execution environment.'
    )

# ------------------------------------------------------------------ #
# logging setup                                                      #
# ------------------------------------------------------------------ #
logger = logging.getLogger(__name__)
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logger.setLevel(getattr(logging, log_level, logging.INFO))

# ------------------------------------------------------------------ #
# constants                                                          #
# ------------------------------------------------------------------ #
VALID_QUERY_TYPES = {'keyword', 'semantic', 'vector', 'hybrid', 'hybrid_semantic'}
DEFAULT_EMBED_MODEL = 'text-embedding-3-large'

# ------------------------------------------------------------------ #
# 1.  extract endpoint & key from CustomConnection                   #
# ------------------------------------------------------------------ #
def _extract_search_credentials(conn: CustomConnection) -> Tuple[str, str]:
    if not isinstance(conn, CustomConnection):
        raise TypeError(f'Expected CustomConnection, got {type(conn).__name__}')
    c = dict(conn)
    endpoint = (
        c.get('endpoint')
        or c.get('api_base')
        or c.get('azure_endpoint')
        or c.get('value1')
        or c.get('key1')
    )
    api_key_from_conn = (
        c.get('api_key') or c.get('value2') or c.get('key2') or c.get('key')
    )
    if not endpoint:
        raise ValueError('Could not find Azure AI Search endpoint in CustomConnection.')
    if not api_key_from_conn:
        raise ValueError('Could not find Azure AI Search API key in CustomConnection.')

    resolved_api_key = api_key_from_conn
    if api_key_from_conn == '***':
        logger.info(
            'Found placeholder "***" for Azure AI Search key, resolving from AZURE_SEARCH_KEY env var.'
        )
        resolved_api_key = os.getenv('AZURE_SEARCH_KEY')
        if not resolved_api_key:
            raise ValueError(
                'Azure AI Search API key is "***", but "AZURE_SEARCH_KEY" env var is not set.'
            )

    logger.debug(f'Using AI Search Endpoint: {endpoint}')
    return endpoint, resolved_api_key


# ------------------------------------------------------------------ #
# 2.  create SearchClient                                            #
# ------------------------------------------------------------------ #
def _client(conn: CustomConnection, index_name: str) -> SearchClient:
    endpoint, key = _extract_search_credentials(conn)
    logger.info(
        f'Creating SearchClient for execution: Endpoint={endpoint}, Index="{index_name}"'
    )
    try:
        return SearchClient(endpoint, index_name, AzureKeyCredential(key))
    except ClientAuthenticationError as e:
        logger.error(f'Auth failed for SearchClient: {e}', exc_info=True)
        raise RuntimeError(
            f'Auth failed connecting to index "{index_name}".  Check API key.'
        ) from e
    except Exception as e:
        logger.error(f'Failed to create SearchClient: {e}', exc_info=True)
        raise RuntimeError(
            f'Could not connect to index "{index_name}".  Error: {e}'
        ) from e


# ------------------------------------------------------------------ #
# 3.  embeddings helper                                              #
# ------------------------------------------------------------------ #
def _embeddings(conn: Union[AzureOpenAIConnection, OpenAIConnection], model_name: str):
    conn_type = type(conn).__name__
    logger.info(
        f'Creating embeddings client: Type="{conn_type}", Model/Deployment="{model_name}"'
    )
    try:
        if isinstance(conn, AzureOpenAIConnection):
            endpoint = getattr(conn, 'azure_endpoint', None) or getattr(
                conn, 'api_base', None
            )
            api_key_from_conn = getattr(conn, 'api_key', None)
            api_version = getattr(conn, 'api_version', None) or '2024-02-01'
            if not endpoint:
                raise ValueError(
                    "AzureOpenAIConnection requires 'azure_endpoint' or 'api_base'."
                )
            if not api_key_from_conn:
                raise ValueError("AzureOpenAIConnection requires 'api_key'.")
            resolved_api_key = api_key_from_conn
            if api_key_from_conn == '***':
                logger.info('Resolving AOAI key from env var.')
                resolved_api_key = os.getenv('AZURE_OPENAI_API_KEY')
            if not resolved_api_key:
                raise ValueError('AOAI key is "***", but env var not set.')
            return AzureOpenAIEmbeddings(
                azure_endpoint=endpoint,
                api_key=resolved_api_key,
                api_version=api_version,
                azure_deployment=model_name,
            )

        if isinstance(conn, OpenAIConnection):
            api_key_from_conn = getattr(conn, 'api_key', None)
            base_url = getattr(conn, 'base_url', None) or getattr(
                conn, 'api_base', None
            )
            if not api_key_from_conn:
                raise ValueError("OpenAIConnection requires 'api_key'.")
            resolved_api_key = api_key_from_conn
            if api_key_from_conn == '***':
                logger.info('Resolving OpenAI key from env var.')
                resolved_api_key = os.getenv('OPENAI_API_KEY')
            if not resolved_api_key:
                raise ValueError('OpenAI key is "***", but env var not set.')
            return OpenAIEmbeddings(
                api_key=resolved_api_key, base_url=base_url, model=model_name
            )

        raise TypeError(f'Unsupported embeddings connection type: {conn_type}')

    except (ValueError, TypeError) as config_err:
        logger.error(f'Embeddings client config error: {config_err}')
        raise
    except Exception as e:
        logger.error(f'Unexpected error creating embeddings client: {e}', exc_info=True)
        raise RuntimeError(f'Failed to init embedding client: {e}') from e


# ------------------------------------------------------------------ #
# 4.  helper to pull text from document                              #
# ------------------------------------------------------------------ #
def _text_from_doc(doc: Dict[str, Any], text_field: str) -> str:
    if not isinstance(doc, dict):
        logger.warning(f'Expected dict, got {type(doc)}.')
        return ''
    content = doc.get(text_field) or doc.get('content') or doc.get('text') or ''
    if text_field not in doc:
        logger.warning(
            f'Specified text_field "{text_field}" not found in document.  Used fallbacks if available.'
        )
    elif not content:
        logger.warning(f'Field "{text_field}" found but was empty.')
    return str(content)


# ------------------------------------------------------------------ #
# 5.  main search execution                                          #
# ------------------------------------------------------------------ #
def _execute_search(
    query_text: str,
    search_client: SearchClient,
    index_name: str,
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
    logger.info(
        f'Executing search: Type="{query_type}", Query="{query_text[:50]}..."'
    )
    vector: Optional[List[float]] = None
    needs_vec = query_type in {'vector', 'hybrid', 'hybrid_semantic'}
    needs_sem = query_type in {'semantic', 'hybrid_semantic'}

    if needs_vec:
        if not embeddings_connection:
            raise ValueError(
                f'Embeddings connection is required for query_type "{query_type}".'
            )
        if not embedding_model_name:
            raise ValueError('Embedding model name is required.')
        if not vector_field:
            raise ValueError('Vector field name is required for vector searches.')

        embeddings_client = _embeddings(embeddings_connection, embedding_model_name)
        vector = embeddings_client.embed_query(query_text)
        if not isinstance(vector, list) or not vector:
            raise ValueError(
                'Embedding generation returned an invalid result (None or empty list).'
            )

    if needs_sem and not semantic_config:
        raise ValueError(
            f'Semantic configuration name is required for query_type "{query_type}".'
        )

    params: Dict[str, Any] = {
        'top': top_k,
        'filter': search_filters,
        'select': ','.join(select_fields) if select_fields else None,
        'include_total_count': False,
    }
    if query_type in {'keyword', 'semantic', 'hybrid', 'hybrid_semantic'}:
        params['search_text'] = query_text

    if needs_vec:
        if vector is None:
            raise RuntimeError('Internal Error: Vector required but None.')
        params['vector_queries'] = [{'vector': vector, 'k': top_k, 'fields': vector_field}]
        if query_type == 'vector':
            params.pop('top', None)
            params.pop('search_text', None)

    if needs_sem:
        params['query_type'] = 'semantic'
        params['semantic_configuration_name'] = semantic_config

    params = {k: v for k, v in params.items() if v is not None}

    logger.debug(
        'Sending search request to index "%s" with params (vector omitted): %s',
        index_name,
        {k: v for k, v in params.items() if k != 'vector_queries'},
    )

    try:
        results = search_client.search(**params)
        docs = list(results)
        logger.info('Search successful, received %d results.', len(docs))
    except Exception as e:
        logger.error('Search request failed: %s', e, exc_info=True)
        logger.error(
            'Failed search params (vector omitted): %s',
            {k: v for k, v in params.items() if k != 'vector_queries'},
        )
        raise RuntimeError(f'Search request failed for index "{index_name}".  Error: {e}') from e

    output: List[Dict[str, Any]] = []
    for doc_dict in docs:
        if not isinstance(doc_dict, dict):
            logger.warning(
                'Received non-dictionary item in search results: %s.  Skipping.',
                type(doc_dict),
            )
            continue

        doc_text = _text_from_doc(doc_dict, text_field)
        doc_vector = doc_dict.get(vector_field) if vector_field else None
        doc_score = doc_dict.get('@search.score')
        reranker_score = doc_dict.get('@search.reranker_score')

        metadata = {
            k: v
            for k, v in doc_dict.items()
            if k not in {text_field, vector_field} and not k.startswith('@search.')
        }
        if reranker_score is not None:
            metadata['reranker_score'] = reranker_score

        output.append(
            {
                'text': doc_text,
                'vector': doc_vector,
                'score': doc_score,
                'metadata': metadata,
                'original_entity': doc_dict,
            }
        )

    return output


# ------------------------------------------------------------------ #
# 6.  main PromptFlow tool                                           #
# ------------------------------------------------------------------ #
@tool
def hw_ai_search_lookup_with_embed(
    connection: CustomConnection,
    index_name: str,
    queries: Union[str, List[str]],
    embeddings_connection: Optional[Union[AzureOpenAIConnection, OpenAIConnection]] = None,
    embedding_model_name: str = DEFAULT_EMBED_MODEL,
    query_type: str = 'hybrid',
    top_k: int = 3,
    text_field: str = 'content',
    vector_field: str = 'vector',
    search_filters: Optional[str] = None,
    select_fields: Optional[List[str]] = None,
    semantic_config: Optional[str] = None,
) -> List[List[Dict[str, Any]]]:
    run_id = os.getenv('PROMPTFLOW_RUN_ID', 'local')
    logger.info(
        f'Starting HW AI Search Lookup Tool (Manual Input v1 - Run ID: {run_id}).'
    )

    query_type = (query_type or 'hybrid').lower()
    if query_type not in VALID_QUERY_TYPES:
        raise ValueError(f'Invalid query_type "{query_type}".')
    if not index_name:
        raise ValueError('"index_name" cannot be empty.')
    if top_k <= 0:
        raise ValueError('"top_k" must be greater than zero.')

    if isinstance(queries, str):
        query_list = [queries]
    elif isinstance(queries, list) and all(isinstance(q, str) for q in queries):
        query_list = queries
    elif isinstance(queries, list) and not queries:
        logger.warning('Received empty query list.  Returning empty results.')
        return []
    else:
        raise TypeError('Invalid "queries" value.  Must be str or List[str].')

    needs_vec = query_type in {'vector', 'hybrid', 'hybrid_semantic'}
    if needs_vec:
        if not embeddings_connection:
            raise ValueError('Embeddings connection required for vector searches.')
        if not isinstance(
            embeddings_connection, (AzureOpenAIConnection, OpenAIConnection)
        ):
            raise TypeError('Invalid embeddings_connection type.')
        if not embedding_model_name:
            raise ValueError('Embedding model name is required.')
        if not vector_field:
            raise ValueError('Vector field name is required for vector searches.')

    needs_sem = query_type in {'semantic', 'hybrid_semantic'}
    if needs_sem and not semantic_config:
        raise ValueError('Semantic configuration name is required for semantic modes.')

    search_client = _client(connection, index_name)
    logger.info(f'Search client initialised for index "{index_name}".')

    search_func_partial = partial(
        _execute_search,
        search_client=search_client,
        index_name=index_name,
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

    results_map = {}
    with ThreadPoolExecutor() as executor:
        tasks = {
            executor.submit(run_with_context, search_func_partial, query): query
            for query in query_list
        }
        for future in tasks:
            query_text = tasks[future]
            try:
                results_map[query_text] = future.result()
            except Exception as e:
                logger.error(
                    'Search task for query "%s" failed: %s', query_text, e, exc_info=False
                )
                results_map[query_text] = []

    return [results_map[q] for q in query_list]