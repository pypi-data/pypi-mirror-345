# -*- coding: utf-8 -*-
# pf_reasoning_tool/tools/vector_lookup_tool.py
'''
HW Vector Lookup Tool – portable vector search across Azure AI Search, Weaviate,
FAISS and Chroma.  Requires an AzureOpenAIConnection or OpenAIConnection for
embeddings.  Single quotes.  Two spaces after full stop.
'''

from typing import List, Dict, Any, Optional
from pathlib import Path
from importlib import import_module

from promptflow.core import tool
from promptflow.connections import (
    CustomConnection, AzureOpenAIConnection, OpenAIConnection
)
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings

# -------------------------------------------------------------------------- #
# Lazy import helpers                                                        #
# -------------------------------------------------------------------------- #

def _safe_import(module_path: str, attr: str):
    """Return imported attr or None if the module isn't installed."""
    try:
        return getattr(import_module(module_path), attr)
    except ModuleNotFoundError:
        return None


def _lazy_load_vectorstores():
    """Loads vectorstore classes on first use, returns a dict."""
    return {
        'azure_search': _safe_import('langchain_community.vectorstores.azure_search', 'AzureSearch'),
        'weaviate':     _safe_import('langchain_community.vectorstores.weaviate', 'Weaviate'),
        'faiss':        _safe_import('langchain_community.vectorstores.faiss', 'FAISS'),
        'chroma':       _safe_import('langchain_community.vectorstores.chroma', 'Chroma'),
    }


VECTORSTORES = _lazy_load_vectorstores()
VALID_BACKENDS = set(VECTORSTORES.keys())
VALID_SEARCH_TYPES = {'similarity', 'mmr', 'hybrid'}

# -------------------------------------------------------------------------- #
# Embeddings helper                                                          #
# -------------------------------------------------------------------------- #

def _get_embeddings(conn: object, model_name: str):
    if isinstance(conn, AzureOpenAIConnection):
        return AzureOpenAIEmbeddings(connection=conn, deployment=model_name)
    if isinstance(conn, OpenAIConnection):
        return OpenAIEmbeddings(connection=conn, model=model_name)
    raise ValueError('embeddings_connection must be AzureOpenAIConnection or OpenAIConnection.')

# -------------------------------------------------------------------------- #
# Vectorstore factory                                                        #
# -------------------------------------------------------------------------- #

def _require_keys(c: CustomConnection, keys: List[str], backend: str):
    missing = [k for k in keys if not getattr(c, k, None)]
    if missing:
        raise ValueError(f'Missing key(s) {missing} in CustomConnection for backend "{backend}".')


def _get_store(
    backend: str,
    conn: CustomConnection,
    embeddings,
    *,
    index_name: str,
    namespace: Optional[str],
    search_type: str,
):
    b = backend.lower()
    store_cls = VECTORSTORES.get(b)

    if store_cls is None:
        raise ModuleNotFoundError(
            f'Backend "{b}" requires an extra dependency.  Install with '
            f'"pip install pf-reasoning-tool[{b}]" and try again.'
        )

    if b == 'azure_search':
        _require_keys(conn, ['endpoint', 'api_key'], b)
        return store_cls(
            azure_search_endpoint=conn.endpoint,
            azure_search_key=conn.api_key,
            index_name=index_name,
            embedding_function=embeddings,
            search_type=search_type,
        )

    if b == 'weaviate':
        _require_keys(conn, ['host'], b)
        import weaviate
        client = weaviate.Client(
            url=conn.host,
            additional_headers={'X-OpenAI-Api-Key': getattr(conn, 'api_key', '')},
        )
        return store_cls(
            client=client,
            index_name=index_name,
            text_key='text',
            embedding=embeddings,
            by_text=False,
            namespace=namespace,
        )

    if b == 'faiss':
        _require_keys(conn, ['index_path'], b)
        idx = Path(conn.index_path)
        if not idx.exists():
            raise FileNotFoundError(f'FAISS index not found: {idx}')
        return store_cls.load_local(folder_path=str(idx), embeddings=embeddings)

    if b == 'chroma':
        _require_keys(conn, ['persist_dir'], b)
        return store_cls(
            collection_name=index_name,
            persist_directory=conn.persist_dir,
            embedding_function=embeddings,
        )

    raise ValueError(f'Unsupported backend "{backend}".  Valid: {sorted(VALID_BACKENDS)}.')

# -------------------------------------------------------------------------- #
# Main PromptFlow tool                                                       #
# -------------------------------------------------------------------------- #

@tool
def hw_vector_lookup(
    query: str,
    backend: str,
    connection: CustomConnection,
    index_name: str,
    top_k: int = 5,
    namespace: Optional[str] = None,
    embeddings_connection: AzureOpenAIConnection | OpenAIConnection = None,
    model_name: str = 'text-embedding-ada-002',
    include_scores: bool = False,
    search_type: str = 'similarity',
    score_threshold: Optional[float] = None,
) -> List[Dict[str, Any]]:
    '''Return top-k similar documents (plus scores if requested).'''

    if not query:
        raise ValueError('query cannot be blank.')
    if top_k <= 0:
        raise ValueError('top_k must be greater than zero.')
    if backend.lower() not in VALID_BACKENDS:
        raise ValueError(f'backend "{backend}" invalid.  Valid: {sorted(VALID_BACKENDS)}')
    if search_type not in VALID_SEARCH_TYPES:
        raise ValueError(f'search_type "{search_type}" invalid.  Valid: {sorted(VALID_SEARCH_TYPES)}')
    if embeddings_connection is None:
        raise ValueError('embeddings_connection is required.')

    embeddings = _get_embeddings(embeddings_connection, model_name)
    store = _get_store(
        backend, connection, embeddings,
        index_name=index_name,
        namespace=namespace,
        search_type=search_type,
    )

    # Pick search strategy
    if search_type == 'mmr' and hasattr(store, 'max_marginal_relevance_search'):
        docs_scores = store.max_marginal_relevance_search(
            query, k=top_k, fetch_k=max(10, top_k * 3)
        )
    else:
        docs_scores = store.similarity_search_with_score(
            query, k=top_k, score_threshold=score_threshold
        )

    results: List[Dict[str, Any]] = []
    for doc, score in docs_scores:
        item = {'text': doc.page_content, 'metadata': doc.metadata}
        if include_scores:
            item['score'] = score
        results.append(item)
    return results
