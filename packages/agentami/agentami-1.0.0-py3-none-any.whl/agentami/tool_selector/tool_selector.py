from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List, Optional
from langchain_core.tools import Tool


class ToolRetriever:
    """
    A retriever that uses semantic similarity to find relevant tools
    based on a natural language query using FAISS and sentence embeddings.
    """

    def __init__(self, tools: Optional[List[Tool]] = None) -> None:
        """
        Initialize the ToolRetriever with an optional list of tools.

        Args:
            tools (Optional[List[Tool]]): A list of LangChain Tool objects.
        """
        if not tools:
            raise ValueError("Tool list cannot be empty or None.")

        self.tools: List[Tool] = tools
        self._model: Optional[SentenceTransformer] = None
        self._index: Optional[faiss.IndexFlatL2] = None
        self._desc_embeddings: Optional[np.ndarray] = None
        self._tool_index_map: dict[int, Tool] = {}
        self._initialize_model()
        self._initialize_faiss_index()

    def _initialize_model(self) -> None:
        """Initialize the SentenceTransformer model."""
        self._model = SentenceTransformer('BAAI/bge-large-en')

    def _initialize_faiss_index(self) -> None:
        """
        Encode tool descriptions and initialize the FAISS index.
        Raises:
            ValueError: If any tool lacks a description.
        """
        desc_list = [tool.description for tool in self.tools]

        if not all(desc_list):
            raise ValueError("All tools must have a non-empty description.")

        embeddings = self._batch_encode(desc_list)
        self._desc_embeddings = np.vstack(embeddings).astype(np.float32)

        dimension = self._desc_embeddings.shape[1]
        self._index = faiss.IndexFlatL2(dimension)
        self._index.add(self._desc_embeddings)

        self._tool_index_map = {i: tool for i, tool in enumerate(self.tools)}

    def _batch_encode(self, descriptions: List[str]) -> List[np.ndarray]:
        """
        Encode a list of tool descriptions in batches.

        Args:
            descriptions (List[str]): List of tool descriptions.

        Returns:
            List[np.ndarray]: List of numpy arrays with encoded embeddings.
        """
        batch_size = 32
        all_embeddings = []

        for start in range(0, len(descriptions), batch_size):
            batch = descriptions[start:start + batch_size]
            result = self._model.encode(batch, convert_to_numpy=True, normalize_embeddings=True)
            all_embeddings.append(result)

        return all_embeddings

    def get_relevant_tools_only(self, query: str, top_k: int = 7) -> List[str]:
        """
        Retrieve the top K most relevant tool names for a given query.

        Args:
            query (str): Natural language query.
            top_k (int): Number of top tools to return.

        Returns:
            List[str]: List of tool names most relevant to the query.
        """
        if not self._model or not self._index:
            raise RuntimeError("ToolRetriever is not properly initialized.")

        query_embed = self._model.encode(query, convert_to_numpy=True, normalize_embeddings=True)
        query_embed = np.expand_dims(query_embed, axis=0)

        distances, indices = self._index.search(query_embed, top_k)
        return [self._tool_index_map[idx].name for idx in indices[0] if idx in self._tool_index_map]
