from pydantic import BaseModel, model_validator
from typing import List, Literal, Optional
import pathlib
from typing_extensions import Self
from chonkie import (
    SemanticChunker,
    SDPMChunker,
    TokenChunker,
    SentenceChunker,
    LateChunker,
    CodeChunker,
    SlumberChunker,
    NeuralChunker,
)
from chonkie.genie import GeminiGenie
from tokenizers import Tokenizer
from pdfitdown.pdfconversion import Converter

try:
    from embeddings import AutoEmbeddings
except ModuleNotFoundError:
    from .embeddings import AutoEmbeddings

pdf_converter = Converter()


class Chunking(BaseModel):
    """
    A Pydantic model for configuring text chunking parameters.

    This class defines the configuration for different text chunking strategies and their associated parameters.

    Attributes:
        chunker (Literal["token", "sentence", "semantic", "sdpm", "late", "slumber", "neural"]):
            The chunking strategy to use. Options are:
            - "token": Split by number of tokens
            - "sentence": Split by sentences
            - "semantic": Split by semantic similarity
            - "sdpm": Split using sentence distance probability matrix
            - "late": Delayed chunking strategy
            - "slumber": LLM-based chunking using Gemini
            - "neural": Finetuned-for-chunking BERT-based chunking

        chunk_size (Optional[int]):
            The target size for each chunk. Defaults to 512 if not specified.

        chunk_overlap (Optional[int]):
            The number of overlapping units between consecutive chunks. Defaults to 128 if not specified.

        similarity_threshold (Optional[float]):
            The minimum similarity threshold for semantic and SDPM chunking. Defaults to 0.7 if not specified.

        min_characters_per_chunk (Optional[int]):
            The minimum number of characters required for a valid chunk. Defaults to 24 if not specified.

        min_sentences (Optional[int]):
            The minimum number of sentences required for a valid chunk. Defaults to 1 if not specified.

        gemini_model (Optional[str]):
            The Gemini model name to use for "slumber" chunking. Defaults to "gemini-2.0-flash" if not specified and "slumber" is chosen.
    """

    chunker: Literal[
        "token", "sentence", "semantic", "sdpm", "late", "slumber", "neural"
    ]
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    similarity_threshold: Optional[float] = None
    min_characters_per_chunk: Optional[int] = None
    min_sentences: Optional[int] = None
    gemini_model: Optional[str] = None

    @model_validator(mode="after")
    def validate_chunking(self) -> Self:
        if self.chunk_size is None:
            self.chunk_size = 512
        if self.chunk_overlap is None:
            self.chunk_overlap = 128
        if self.similarity_threshold is None:
            self.similarity_threshold = 0.7
        if self.min_characters_per_chunk is None:
            self.min_characters_per_chunk = 24
        if self.min_sentences is None:
            self.min_sentences = 1
        if self.chunker == "slumber" and self.gemini_model is None:
            self.gemini_model = "gemini-2.0-flash"
        return self


class CodeFiles(BaseModel):
    """A Pydantic model for validating and processing lists of code file paths.

    This class extends BaseModel to handle file path validation, ensuring that all
    provided paths exist in the filesystem.

    Attributes:
        files (List[str]): A list of file paths to be validated.

    Raises:
        ValueError: When none of the provided file paths exist in the filesystem.
    """

    files: List[str]

    @model_validator(mode="after")
    def valid_files(self) -> Self:
        fs = []
        for f in self.files:
            if pathlib.Path(f).is_file():
                fs.append(f)
        if len(fs) == 0:
            raise ValueError("The files you provided do not exist")
        self.files = fs
        return self


class CodeChunking(BaseModel):
    """A Pydantic model for configuring code chunking parameters.

    This class handles the configuration and validation of parameters used for chunking code
    into smaller segments, with support for different programming languages and tokenization methods.

    Attributes:
        language (str): The programming language of the code to be chunked.
        return_type (Optional[Literal["chunks", "texts"]]): The format of the chunked output.
            Defaults to "chunks" if not specified.
        tokenizer (Optional[str]): The name of the tokenizer to use. Defaults to "gpt2".
        chunk_size (Optional[int]): The maximum size of each chunk in tokens. Defaults to 512.
        include_nodes (Optional[bool]): Whether to include AST nodes in the output.
            Defaults to False.
    """

    language: str
    return_type: Optional[Literal["chunks", "texts"]] = None
    tokenizer: Optional[str] = None
    chunk_size: Optional[int] = None
    include_nodes: Optional[bool] = None
    chunker: Optional[Literal["code"]] = None

    @model_validator(mode="after")
    def validate_chunking(self) -> Self:
        if self.chunk_size is None:
            self.chunk_size = 512
        if self.return_type is None:
            self.return_type = "chunks"
        if self.tokenizer is None:
            self.tokenizer = "gpt2"
        self.tokenizer = Tokenizer.from_pretrained(self.tokenizer)
        if self.include_nodes is None:
            self.include_nodes = False
        self.chunker = CodeChunker(
            tokenizer_or_token_counter=self.tokenizer,
            chunk_size=self.chunk_size,
            language=self.language,
            include_nodes=self.include_nodes,
            return_type=self.return_type,
        )
        return self


class IngestionInput(BaseModel):
    """
    A class that validates and processes ingestion inputs for document processing.

    This class handles different types of document inputs and chunking strategies, converting
    files and setting up appropriate chunking mechanisms based on the specified configuration.

    Attributes:

        files_or_dir : Union[str, List[str]]
            Path to directory containing files or list of file paths to process

        chunking : Chunking
            Configuration for the chunking strategy to be used

        tokenizer : Optional[str], default=None
            Name or path of the tokenizer model to be used (required for 'token' and 'sentence' chunking)

        embedding_model : str
            Name or path of the embedding model to be used
    """

    files_or_dir: str | List[str]
    chunking: Chunking
    tokenizer: Optional[str] = None
    embedding_model: str

    @model_validator(mode="after")
    def validate_ingestion(self) -> Self:
        if isinstance(self.files_or_dir, str):
            self.files_or_dir = pdf_converter.convert_directory(self.files_or_dir)
            if len(self.files_or_dir) == 0:
                raise ValueError(
                    "The directory or files input you provided was not convertible to PDF at all"
                )
        elif isinstance(self.files_or_dir, list):
            self.files_or_dir = pdf_converter.multiple_convert(
                file_paths=self.files_or_dir
            )
            if len(self.files_or_dir) == 0:
                raise ValueError(
                    "The directory or files input you provided was not convertible to PDF at all"
                )
        self.embedding_model = AutoEmbeddings.get_embeddings(model=self.embedding_model)
        if self.chunking.chunker == "token":
            if self.tokenizer is None:
                raise ValueError(
                    f"Tokenizer cannot be None if {self.chunking.chunker} chunking approach is chosen"
                )
            self.tokenizer = Tokenizer.from_pretrained(self.tokenizer)
            self.chunking = TokenChunker(
                tokenizer=self.tokenizer,
                chunk_size=self.chunking.chunk_size,
                chunk_overlap=self.chunking.chunk_overlap,
            )
        elif self.chunking.chunker == "sentence":
            if self.tokenizer is None:
                raise ValueError(
                    f"Tokenizer cannot be None if {self.chunking.chunker} chunking approach is chosen"
                )
            self.tokenizer = Tokenizer.from_pretrained(self.tokenizer)
            self.chunking = SentenceChunker(
                tokenizer_or_token_counter=self.tokenizer,
                chunk_size=self.chunking.chunk_size,
                chunk_overlap=self.chunking.chunk_overlap,
                min_sentences_per_chunk=self.chunking.min_sentences,
            )
        elif self.chunking.chunker == "late":
            self.chunking = LateChunker(
                embedding_model=self.embedding_model,
                chunk_size=self.chunking.chunk_size,
                min_characters_per_chunk=self.chunking.min_characters_per_chunk,
            )
        elif self.chunking.chunker == "sdpm":
            self.chunking = SDPMChunker(
                embedding_model=self.embedding_model,
                chunk_size=self.chunking.chunk_size,
                threshold=self.chunking.similarity_threshold,
                min_sentences=self.chunking.min_sentences,
            )
        elif self.chunking.chunker == "semantic":
            self.chunking = SemanticChunker(
                embedding_model=self.embedding_model,
                threshold=self.chunking.similarity_threshold,
                min_sentences=self.chunking.min_sentences,
                chunk_size=self.chunking.chunk_size,
            )
        elif self.chunking.chunker == "slumber":
            genie = GeminiGenie(model=self.chunking.gemini_model)
            self.chunking = SlumberChunker(
                genie=genie,
                tokenizer_or_token_counter=self.tokenizer,
                chunk_size=self.chunking.chunk_size,
                min_characters_per_chunk=self.chunking.min_characters_per_chunk,
            )
        elif self.chunking.chunker == "neural":
            self.chunking = NeuralChunker(
                min_characters_per_chunk=self.chunking.min_characters_per_chunk
            )
        return self
