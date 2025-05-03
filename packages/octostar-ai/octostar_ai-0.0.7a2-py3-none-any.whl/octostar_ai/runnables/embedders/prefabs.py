from typing import Optional
from octostar_ai.utils.gpu import get_device


def default_rag_embedder(openai_api_key: Optional[str] = None):
    """Get the default embedder for Retrieval-Augmented Generation (RAG)."""
    if openai_api_key:
        from octostar_ai.runnables.embedders.commons import OpenAIEmbeddings

        return OpenAIEmbeddings(
            model="text-embedding-3-small", model_version="1", api_key=openai_api_key
        )

    from octostar_ai.runnables.embedders.commons import HuggingFaceEmbeddings

    model_name = "sentence-transformers/all-mpnet-base-v2"
    model_kwargs = {"device": get_device()}
    encode_kwargs = {"normalize_embeddings": False}
    return HuggingFaceEmbeddings(
        model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
    )
