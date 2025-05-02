# -*- coding: utf-8 -*-
# pf_reasoning_tool/tools/hw_vector_lookup_tool.py
'''
HW Vector Lookup Tool – portable vector search across Azure AI Search, Weaviate,
FAISS and Chroma.  Imports are lazy, so missing libraries do not block other
tools.  Requires an AzureOpenAIConnection or OpenAIConnection for embeddings.
'''

from typing import List, Dict, Any, Optional
from pathlib import Path
from importlib import import_module

from promptflow.core import tool
from promptflow.connections import (
    CustomConnection, AzureOpenAIConnection, OpenAIConnection
)
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings

VALID_BACKENDS = {'azure_search', 'weaviate', 'faiss', 'chroma'}
VALID_SEARCH_TYPES = {'similarity', 'mmr', 'hybrid'}


# -------------------------------------------------------------------------- #
# Embeddings helper                                                          #
# -------------------------------------------------------------------------- #

def _get_embeddings(conn: object, model_name: str):
    if isinstance(conn, AzureOpenAIConnection):
        return AzureOpenAIEmbeddings(connection=conn, deployment=model_name)
    if isinstance(conn, OpenAIConnection):
        return OpenAIEmbeddings(connection=conn, model=model_name)
    raise ValueError(
        'embeddings_connection must be AzureOpenAIConnection or OpenAIConnection.'
    )


# -------------------------------------------------------------------------- #
# Vectorstore lazy imports                                                   #
# -------------------------------------------------------------------------- #

def _import_azure_vectorstore():
    """
    AzureSearch moved from '...azure_search' (<=0.1.x) to '...azuresearch' (0.2.x).
    Try both paths so the tool works with any LangChain version.
    """
    for path in (
        'langchain_community.vectorstores.azuresearch',    # LangChain ≥ 0.2
        'langchain_community.vectorstores.azure_search',   # LangChain 0.1.x
    ):
        try:
            return import_module(path).AzureSearch
        except ModuleNotFoundError:
            continue
    raise ModuleNotFoundError(
        'AzureSearch vectorstore not found.  Install/upgrade LangChain and '
        'azure-search-documents, or reinstall pf-reasoning-tool[azure].'
    )


def _import_optional_vectorstore(path: str, attr: str, extra: str):
    try:
        return getattr(import_module(path), attr)
    except ModuleNotFoundError:
        raise ModuleNotFoundError(
            f'{attr} vectorstore not found.  Install with '
            f'"pip install pf-reasoning-tool[{extra}]" and try again.'
        )


# -------------------------------------------------------------------------- #
# Vectorstore factory                                                        #
# -------------------------------------------------------------------------- #

def _require_keys(c: CustomConnection, keys: List[str], backend: str):
    missing = [k for k in keys if not getattr(c, k, None)]
    if missing:
        raise ValueError(
            f'Missing key(s) {missing} in CustomConnection for backend "{backend}".'
        )


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

    # ------- Azure AI Search ---------------------------------------------
    if b == 'azure_search':
        AzureSearch = _import_azure_vectorstore()
        _require_keys(conn, ['endpoint', 'api_key'], b)
        return AzureSearch(
            azure_search_endpoint=conn.endpoint,
            azure_search_key=conn.api_key,
            index_name=index_name,
            embedding_function=embeddings,
            search_type=search_type,
        )

    # ------- Weaviate -----------------------------------------------------
    if b == 'weaviate':
        Weaviate = _import_optional_vectorstore(
            'langchain_community.vectorstores.weaviate', 'Weaviate', 'weaviate'
        )
        _require_keys(conn, ['host'], b)
        import weaviate
        client = weaviate.Client(
            url=conn.host,
            additional_headers={'X-OpenAI-Api-Key': getattr(conn, 'api_key', '')},
        )
        return Weaviate(
            client=client,
            index_name=index_name,
            text_key='text',
            embedding=embeddings,
            by_text=False,
            namespace=namespace,
        )

    # ------- FAISS --------------------------------------------------------
    if b == 'faiss':
        FAISS = _import_optional_vectorstore(
            'langchain_community.vectorstores.faiss', 'FAISS', 'faiss'
        )
        _require_keys(conn, ['index_path'], b)
        idx = Path(conn.index_path)
        if not idx.exists():
            raise FileNotFoundError(f'FAISS index not found: {idx}')
        return FAISS.load_local(folder_path=str(idx), embeddings=embeddings)

    # ------- Chroma -------------------------------------------------------
    if b == 'chroma':
        Chroma = _import_optional_vectorstore(
            'langchain_community.vectorstores.chroma', 'Chroma', 'chroma'
        )
        _require_keys(conn, ['persist_dir'], b)
        return Chroma(
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

    # Choose search algorithm
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
