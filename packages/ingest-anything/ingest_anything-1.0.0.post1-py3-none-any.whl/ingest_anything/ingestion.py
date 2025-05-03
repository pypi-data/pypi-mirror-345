try:
    from add_types import IngestionInput, Chunking, CodeChunking, CodeFiles
    from embeddings import ChonkieAutoEmbedding
except ModuleNotFoundError:
    from .add_types import IngestionInput, Chunking, CodeChunking, CodeFiles
    from .embeddings import ChonkieAutoEmbedding
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
from llama_index.core.readers.base import BaseReader
from llama_index.core.vector_stores.types import BasePydanticVectorStore
from llama_index.readers.docling import DoclingReader
from llama_index.core.schema import TextNode
from typing import Optional, Literal, List
import uuid

class IngestAnything:
    """
    IngestAnything provides a high-level interface for ingesting documents, chunking them using various strategies, and indexing them into a vector store for semantic search.

    Parameters
    ----------
    vector_store : BasePydanticVectorStore
        The vector store instance where document embeddings will be stored.
    reader : Optional[BaseReader], default=None
        Optional custom document reader. If not provided, a default DoclingReader is used.
    """
    def __init__(self, vector_store: BasePydanticVectorStore, reader: Optional[BaseReader] = None):
        self.vector_store = vector_store
        if reader is None:
            reader = DoclingReader()
        self.reader = reader
    def ingest(
            self,
            files_or_dir: str | List[str],
            embedding_model: str,
            chunker: Literal["token", "sentence", "semantic", "sdpm", "late", "neural", "slumber"],
            tokenizer: Optional[str] = None,
            chunk_size: Optional[int] = None,
            chunk_overlap: Optional[int] = None,
            similarity_threshold: Optional[float] = None,
            min_characters_per_chunk: Optional[int] = None,
            min_sentences: Optional[int] = None,
            gemini_model: Optional[str] = None
    ):
        """
        Ingest documents from files or directories using the specified chunking strategy and create a searchable vector index.

        Parameters
        ----------
        files_or_dir : str or List[str]
            Path to file(s) or directory to ingest.
        embedding_model : str
            Name of the embedding model to use: supports OpenAI, HuggingFace, Cohere, Jina AI and Model2Vec
        chunker : Literal["token", "sentence", "semantic", "sdpm", "late", "neural", "slumber"]
            Chunking strategy to use.
        tokenizer : str, optional
            Tokenizer to use for chunking.
        chunk_size : int, optional
            Size of chunks.
        chunk_overlap : int, optional
            Number of overlapping tokens/sentences between chunks.
        similarity_threshold : float, optional
            Similarity threshold for semantic chunking.
        min_characters_per_chunk : int, optional
            Minimum number of characters per chunk.
        min_sentences : int, optional
            Minimum number of sentences per chunk.
        gemini_model : str, optional
            Name of Gemini model to use for chunking, if applicable.

        Returns
        -------
        VectorStoreIndex
            Index containing the ingested and embedded document chunks.
        """
        chunking = Chunking(chunker=chunker, chunk_size=chunk_size, chunk_overlap=chunk_overlap, similarity_threshold=similarity_threshold, min_characters_per_chunk=min_characters_per_chunk, min_sentences=min_sentences, gemini_model=gemini_model)
        ingestion_input = IngestionInput(files_or_dir=files_or_dir, chunking=chunking, tokenizer=tokenizer, embedding_model=embedding_model)
        docs = SimpleDirectoryReader(input_files=ingestion_input.files_or_dir, file_extractor={".pdf": self.reader}).load_data()
        text = "\n\n---\n\n".join([d.text for d in docs])
        chunks = ingestion_input.chunking.chunk(text)
        nodes = [TextNode(text=c.text, id_=str(uuid.uuid4())) for c in chunks]
        storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        index = VectorStoreIndex(nodes=nodes, embed_model=ChonkieAutoEmbedding(model_name=embedding_model), show_progress=True, storage_context=storage_context)
        return index
    
class IngestCode:
    """
    IngestCode is a class for ingesting code files, chunking them, embedding the chunks, and storing them in a vector store for efficient search and retrieval.

    Attributes
    ----------

    vector_store : BasePydanticVectorStore
        The vector store instance where embedded code chunks will be stored.
    """
    def __init__(self, vector_store: BasePydanticVectorStore):
        self.vector_store = vector_store
    def ingest(
            self,
            files: List[str],
            embedding_model: str,
            language: str,
            return_type: Optional[Literal["chunks", "texts"]] = None,
            tokenizer: Optional[str] = None,
            chunk_size: Optional[int] = None,
            include_nodes: Optional[bool] = None,
    ):
        """
        Ingest code files and create a searchable vector index.

        Parameters
        ----------
            files (List[str]): List of file paths to ingest
            embedding_model (str): Name of the HuggingFace embedding model to use
            language (str): Programming language of the code files
            return_type (Literal["chunks", "texts"], optional): Type of return value from chunking
            tokenizer (str, optional): Name of tokenizer to use
            chunk_size (int, optional): Size of chunks for text splitting
            include_nodes (bool, optional): Whether to include AST nodes in chunking
        
        Returns
        --------
            VectorStoreIndex: Index containing the ingested and embedded code chunks
        """
        fls = CodeFiles(files=files)
        chunking = CodeChunking(language=language, return_type=return_type, tokenizer=tokenizer, chunk_size=chunk_size, include_nodes=include_nodes)
        docs = SimpleDirectoryReader(input_files=fls.files).load_data()
        text = "\n\n---\n\n".join([d.text for d in docs])
        chunks = chunking.chunker.chunk(text)
        nodes = [TextNode(text=c.text, id_=str(uuid.uuid4())) for c in chunks]
        storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        index = VectorStoreIndex(nodes=nodes, embed_model=ChonkieAutoEmbedding(model_name=embedding_model), show_progress=True, storage_context=storage_context)
        return index