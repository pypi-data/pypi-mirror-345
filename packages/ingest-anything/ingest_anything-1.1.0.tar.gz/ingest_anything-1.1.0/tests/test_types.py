from add_types import IngestionInput, Chunking, Tokenizer, TokenChunker, CodeChunking, CodeChunker, CodeFiles
from chonkie.embeddings import BaseEmbeddings
import os
from pydantic import ValidationError
import pathlib
from collections import Counter

def test_chunking():
    test_cases = [
        {
            "chunker": "slumber",
            "chunk_size": 129,
            "chunk_overlap": 100,
            "similarity_threshold": 0.1,
            "min_characters_per_chunk": 100,
            "min_sentences": 4,
            "gemini_model": None,
            "expected": ["slumber", 129, 100, 0.1, 100, 4, "gemini-2.0-flash"]
        },
        {
            "chunker": "token",
            "chunk_size": None,
            "chunk_overlap": None,
            "similarity_threshold": None,
            "min_characters_per_chunk": None,
            "min_sentences": None,
            "gemini_model": "gemini-1.5-flash",
            "expected": ["token", 512, 128, 0.7, 24, 1, "gemini-1.5-flash"]
        },
        {
            "chunker": "toke",
            "chunk_size": 129,
            "chunk_overlap": 100,
            "similarity_threshold": 0.1,
            "min_characters_per_chunk": 100,
            "min_sentences": 4,
            "gemini_model": None,
            "expected": None
        },
    ]
    for c in test_cases:
        try:
            chunks = Chunking(chunker=c["chunker"], chunk_size=c["chunk_size"], chunk_overlap=c["chunk_overlap"], similarity_threshold = c["similarity_threshold"], min_characters_per_chunk=c["min_characters_per_chunk"], min_sentences=c["min_sentences"], gemini_model=c["gemini_model"])
        except ValidationError:
            outcome = None
        else:
            outcome = [chunks.chunker, chunks.chunk_size, chunks.chunk_overlap, chunks.similarity_threshold, chunks.min_characters_per_chunk, chunks.min_sentences, chunks.gemini_model]
        assert outcome == c["expected"]

def test_code_files():
    test_cases = [
        {
            "files": ["tests/code/acronym.go", "tests/code/animal_magic.go", "tests/code/atbash_cipher_test.go"],
            "expected": Counter(["tests/code/acronym.go", "tests/code/animal_magic.go", "tests/code/atbash_cipher_test.go"]),
        },
        {
            "files": ["tests/code/acrony.go", "tests/code/animal_magic.go", "tests/code/atbash_cipher_test.go"],
            "expected": Counter(["tests/code/animal_magic.go", "tests/code/atbash_cipher_test.go"]),
        },
        {
            "files": ["tests/code/acrony.go", "tests/code/animal_magc.go", "tests/code/atbash_cipher_tes.go"],
            "expected": None,
        },
    ]
    for c in test_cases:
        try:
            cfl = CodeFiles(files=c["files"])
        except ValidationError:
            outcome = None
        else:
            outcome = Counter(cfl.files)
        assert outcome == c["expected"]


def test_code_chunker():
    test_cases = [
        {
            "language": "go",
            "return_type": None,
            "chunk_size": None,
            "tokenizer": "gpt2",
            "include_nodes": True,
            "expected": ["go","chunks",512,True, True,True],
        },
        {
            "language": "pokemon",
            "return_type": None,
            "chunk_size": None,
            "include_nodes": None,
            "tokenizer": "gpt2",
            "expected": None,
        },
        {
            "language": "python",
            "return_type": "text",
            "chunk_size": None,
            "tokenizer": "gpt2",
            "include_nodes": None,
            "expected": None,
        },
    ]
    for c in test_cases:
        try:
            chunks = CodeChunking(chunk_size=c["chunk_size"], language=c["language"], return_type=c["return_type"],tokenizer=c["tokenizer"],include_nodes=c["include_nodes"])
        except Exception:
            outcome = None
        else:
            outcome = [chunks.language, chunks.return_type, chunks.chunk_size, chunks.include_nodes, isinstance(chunks.tokenizer, Tokenizer), isinstance(chunks.chunker, CodeChunker)]
        assert outcome == c["expected"]

def test_ingestion_input():
    test_cases = [
        {
            "chunker": "token",
            "chunk_size": None,
            "chunk_overlap": None,
            "similarity_threshold": None,
            "min_characters_per_chunk": None,
            "min_sentences": None,
            "files_or_dir": "tests/data",
            "tokenizer": "gpt2",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "gemini_model": None,
            "expected": [Counter(['tests/data/test.pdf', 'tests/data/test0.pdf', 'tests/data/test1.pdf', 'tests/data/test2.pdf', 'tests/data/test3.pdf', 'tests/data/test4.pdf', 'tests/data/test5.pdf']), True, True, True],
        },
        {
            "chunker": "token",
            "chunk_size": None,
            "chunk_overlap": None,
            "similarity_threshold": None,
            "min_characters_per_chunk": None,
            "min_sentences": None,
            "files_or_dir": ['tests/data/test.docx', 'tests/data/test0.png', 'tests/data/test1.csv', 'tests/data/test2.json', 'tests/data/test3.md', 'tests/data/test4.xml', 'tests/data/test5.zip'],
            "tokenizer": "gpt2",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "gemini_model": None,
            "expected": [Counter(['tests/data/test.pdf', 'tests/data/test0.pdf', 'tests/data/test1.pdf', 'tests/data/test2.pdf', 'tests/data/test3.pdf', 'tests/data/test4.pdf', 'tests/data/test5.pdf']), True, True, True]
        },
        {
            "chunker": "token",
            "chunk_size": None,
            "chunk_overlap": None,
            "similarity_threshold": None,
            "min_characters_per_chunk": None,
            "min_sentences": None,
            "files_or_dir": "tests/data",
            "tokenizer": None,
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "gemini_model": None,
            "expected": None
        },
        {
            "chunker": "token",
            "chunk_size": None,
            "chunk_overlap": None,
            "similarity_threshold": None,
            "min_characters_per_chunk": None,
            "min_sentences": None,
            "files_or_dir": "tests/err",
            "tokenizer": "gpt2",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "gemini_model": None,
            "expected": None
        },
        {
            "chunker": "token",
            "chunk_size": None,
            "chunk_overlap": None,
            "similarity_threshold": None,
            "min_characters_per_chunk": None,
            "min_sentences": None,
            "files_or_dir": 3,
            "tokenizer": "gpt2",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "gemini_model": None,
            "expected": None
        },
    ]
    for c in test_cases:
        try:
            chunks = Chunking(chunker=c["chunker"], chunk_size=c["chunk_size"], chunk_overlap=c["chunk_overlap"], similarity_threshold = c["similarity_threshold"], min_characters_per_chunk=c["min_characters_per_chunk"], min_sentences=c["min_sentences"], gemini_model=c["gemini_model"])
            ingestion = IngestionInput(chunking=chunks, files_or_dir=c["files_or_dir"], tokenizer=c["tokenizer"], embedding_model=c["embedding_model"])
        except ValidationError:
            outcome = None
        else:
            outcome = [Counter(ingestion.files_or_dir), isinstance(ingestion.chunking, TokenChunker), isinstance(ingestion.tokenizer, Tokenizer), isinstance(ingestion.embedding_model, BaseEmbeddings)]
        for f in ['tests/data/test.pdf', 'tests/data/test0.pdf', 'tests/data/test1.pdf', 'tests/data/test2.pdf', 'tests/data/test3.pdf', 'tests/data/test4.pdf', 'tests/data/test5.pdf']:
            if pathlib.Path(f).is_file():
                os.remove(f)
        assert outcome == c["expected"]
