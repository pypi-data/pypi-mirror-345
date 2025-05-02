# -*- coding: utf-8 -*-
# pf_reasoning_tool/tools/vector_lookup_tool.py
'''
Portable vector search PromptFlow tool.  Supports Azure AI Search, Weaviate, FAISS,
Chroma (and any LangChain VectorStore).  Requires an AzureOpenAIConnection or
OpenAIConnection for embeddings.  Single quotes, two spaces after full stop.
'''

from typing import List, Dict, Any, Optional
from pathlib import Path

from promptflow.core import tool
from promptflow.connections import (
    CustomConnection, AzureOpenAIConnection, OpenAIConnection
)

# LangChain vectorstores
from langchain_community.vectorstores import AzureSearch, Weaviate, FAISS, Chroma
# Embeddings
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings

VALID_BACKENDS = {'azure_search', 'weaviate', 'faiss', 'chroma'}
VALID_SEARCH_TYPES = {'similarity', 'mmr', 'hybrid'}


# -------------------------------------------------------------------------- #
# Helpers                                                                    #
# -------------------------------------------------------------------------- #

def _get_embeddings(emb_conn: object, model_name: str):
    '''Return a LangChain embeddings object.  emb_conn must be Azure/OpenAI.'''
    if isinstance(emb_conn, AzureOpenAIConnection):
        return AzureOpenAIEmbeddings(connection=emb_conn, deployment=model_name)
    if isinstance(emb_conn, OpenAIConnection):
        return OpenAIEmbeddings(connection=emb_conn, model=model_name)
    raise ValueError(
        'embeddings_connection must be an AzureOpenAIConnection or OpenAIConnection.'
    )


def _require_keys(conn: CustomConnection, keys: List[str], backend: str):
    missing = [k for k in keys if not getattr(conn, k, None)]
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
    search_type: str
):
    b = backend.lower()

    if b == 'azure_search':
        _require_keys(conn, ['endpoint', 'api_key'], b)
        return AzureSearch(
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
        return Weaviate(
            client=client,
            index_name=index_name,
            text_key='text',
            embedding=embeddings,
            by_text=False,
            namespace=namespace,
        )

    if b == 'faiss':
        _require_keys(conn, ['index_path'], b)
        idx_path = Path(conn.index_path)
        if not idx_path.exists():
            raise FileNotFoundError(f'FAISS index not found: {idx_path}')
        return FAISS.load_local(folder_path=str(idx_path), embeddings=embeddings)

    if b == 'chroma':
        _require_keys(conn, ['persist_dir'], b)
        return Chroma(
            collection_name=index_name,
            persist_directory=conn.persist_dir,
            embedding_function=embeddings,
        )

    raise ValueError(f'Unsupported backend "{backend}".  Valid: {sorted(VALID_BACKENDS)}')


# -------------------------------------------------------------------------- #
# Main PromptFlow tool                                                       #
# -------------------------------------------------------------------------- #

@tool
def vector_lookup(
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
    '''
    Retrieve the top-k most similar documents for *query*.

    Returns
    -------
    A list of dicts:
        { 'text': str, 'metadata': dict, 'score': float (optional) }
    '''

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
        backend,
        connection,
        embeddings,
        index_name=index_name,
        namespace=namespace,
        search_type=search_type,
    )

    # Choose search variant
    if search_type == 'mmr' and hasattr(store, 'max_marginal_relevance_search'):
        docs_and_scores = store.max_marginal_relevance_search(
            query, k=top_k, fetch_k=max(top_k * 3, 10)
        )
    else:
        docs_and_scores = store.similarity_search_with_score(
            query, k=top_k, score_threshold=score_threshold
        )

    results: List[Dict[str, Any]] = []
    for doc, score in docs_and_scores:
        item = {'text': doc.page_content, 'metadata': doc.metadata}
        if include_scores:
            item['score'] = score
        results.append(item)

    return results
