from ingestion import IngestAnything, VectorStoreIndex, IngestCode
from typing import Any
from qdrant_client import QdrantClient, AsyncQdrantClient
import weaviate
from weaviate import WeaviateClient
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from llama_index.vector_stores.milvus import MilvusVectorStore
from llama_index.vector_stores.qdrant import QdrantVectorStore
import pathlib
import sys
import os
from dotenv import load_dotenv
from pymilvus import MilvusClient
from custom_reader_to_test import MarkItDownReader

load_dotenv()

# Readers config
markitdown_reader = MarkItDownReader()

# Abstract client class for collection check and delete operations
class AbstractClient:
    def __init__(self, client: Any):
        self.client = client
    def delete_collection(self, collection_name: str = "Test") -> None:
        if isinstance(self.client, WeaviateClient):
            self.client.collections.delete(collection_name)
        elif isinstance(self.client, MilvusClient):
            self.client.drop_collection(collection_name)
        elif isinstance(self.client, QdrantClient):
            self.client.delete_collection(collection_name)
        return
    def check_collection_exists(self, collection_name: str = "Test") -> bool:
        if isinstance(self.client, WeaviateClient):
            return self.client.collections.exists(collection_name)
        elif isinstance(self.client, MilvusClient):
            r = self.client.list_collections()
            return collection_name in r
        elif isinstance(self.client, QdrantClient):
            return self.client.collection_exists(collection_name)
        return False

# Qdrant Config
client_qdrant = QdrantClient(api_key=os.getenv("qdrant_api_key"), url=os.getenv("qdrant_url"))
aclient_qdrant = AsyncQdrantClient(api_key=os.getenv("qdrant_api_key"), url=os.getenv("qdrant_url"))
vector_store_qdrant = QdrantVectorStore(collection_name="Test",client=client_qdrant, aclient=aclient_qdrant)
abstract_qdrant_client = AbstractClient(client_qdrant)

# Weaviate config
cluster_url = os.getenv("weaviate_cluster_url")
api_key = os.getenv("weaviate_admin_key")
client_weaviate = weaviate.connect_to_weaviate_cloud(
    cluster_url=cluster_url,
    auth_credentials=weaviate.auth.AuthApiKey(api_key),
)
vector_store_weaviate = WeaviateVectorStore(
    weaviate_client=client_weaviate, index_name="Test"
)
abstract_weaviate_client = AbstractClient(client_weaviate)

# Milvus Config
milvus_uri = os.getenv("milvus_uri")
milvus_token = os.getenv("milvus_token")
client_milvus = MilvusClient(
    uri=milvus_uri,
    token=milvus_token
)
vector_store_milvus = MilvusVectorStore(
    uri=milvus_uri, token=milvus_token,overwrite=True,collection_name="Test",dim=384
)
abstract_milvus_client = AbstractClient(client_milvus)

def test_ingestion():
    test_cases = [
        {
            "chunker": "late",
            "chunk_size": None,
            "chunk_overlap": None,
            "similarity_threshold": None,
            "min_characters_per_chunk": None,
            "min_sentences": None,
            "files_or_dir": "tests/data",
            "tokenizer": "gpt2",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "gemini_model": None,
            "vector_store": vector_store_weaviate,
            "reader": markitdown_reader,
            "client": abstract_qdrant_client,
            "expected": [True, True],
        },
        {
            "chunker": "semantic",
            "chunk_size": None,
            "chunk_overlap": None,
            "similarity_threshold": None,
            "min_characters_per_chunk": None,
            "min_sentences": None,
            "files_or_dir": ['tests/data/test.docx', 'tests/data/test0.png', 'tests/data/test1.csv', 'tests/data/test2.json', 'tests/data/test3.md', 'tests/data/test4.xml', 'tests/data/test5.zip'],
            "tokenizer": "gpt2",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "gemini_model": None,
            "vector_store": vector_store_qdrant,
            "reader": markitdown_reader,
            "client": abstract_qdrant_client,
            "expected": [True, True],
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
            "vector_store": vector_store_weaviate,
            "reader": markitdown_reader,
            "client": abstract_weaviate_client,
            "expected": [True, True],
        },
        {
            "chunker": "sdpm",
            "chunk_size": None,
            "chunk_overlap": None,
            "similarity_threshold": None,
            "min_characters_per_chunk": None,
            "min_sentences": None,
            "files_or_dir": ['tests/data/test.docx', 'tests/data/test0.png', 'tests/data/test1.csv', 'tests/data/test2.json', 'tests/data/test3.md', 'tests/data/test4.xml', 'tests/data/test5.zip'],
            "tokenizer": "gpt2",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "gemini_model": None,
            "vector_store": vector_store_milvus,
            "reader": None,
            "client": abstract_milvus_client,
            "expected": [True, True],
        },
        {
            "chunker": "sentence",
            "chunk_size": None,
            "chunk_overlap": None,
            "similarity_threshold": None,
            "min_characters_per_chunk": None,
            "min_sentences": None,
            "files_or_dir": ['tests/data/test.docx', 'tests/data/test0.png', 'tests/data/test1.csv', 'tests/data/test2.json', 'tests/data/test3.md', 'tests/data/test4.xml', 'tests/data/test5.zip'],
            "tokenizer": "gpt2",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "gemini_model": None,
            "vector_store": vector_store_qdrant,
            "reader": None,
            "client": abstract_qdrant_client,
            "expected": [True, True],
        },
        {
            "chunker": "neural",
            "chunk_size": None,
            "chunk_overlap": None,
            "similarity_threshold": None,
            "min_characters_per_chunk": None,
            "min_sentences": None,
            "files_or_dir": ['tests/data/test.docx', 'tests/data/test0.png', 'tests/data/test1.csv', 'tests/data/test2.json', 'tests/data/test3.md', 'tests/data/test4.xml', 'tests/data/test5.zip'],
            "tokenizer": "gpt2",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "gemini_model": None,
            "vector_store": vector_store_milvus,
            "reader": None,
            "client": abstract_milvus_client,
            "expected": [True, True],
        },
    ]
    for c in test_cases:
        try:
            ingestor = IngestAnything(vector_store=c["vector_store"], reader=c["reader"])
            index = ingestor.ingest(chunker=c["chunker"], chunk_size=c["chunk_size"], chunk_overlap=c["chunk_overlap"], similarity_threshold = c["similarity_threshold"], min_characters_per_chunk=c["min_characters_per_chunk"], min_sentences=c["min_sentences"],files_or_dir=c["files_or_dir"], tokenizer=c["tokenizer"], embedding_model=c["embedding_model"], gemini_model = c["gemini_model"])
            outcome = [isinstance(index, VectorStoreIndex), c["client"].check_collection_exists()]
        except Exception as e:
            print(e.__str__(), sys.stderr)
            outcome = [None, e.__str__()]
        for f in ['tests/data/test.pdf', 'tests/data/test0.pdf', 'tests/data/test1.pdf', 'tests/data/test2.pdf', 'tests/data/test3.pdf', 'tests/data/test4.pdf', 'tests/data/test5.pdf']:
            if pathlib.Path(f).is_file():
                os.remove(f)
        assert outcome == c["expected"]

def test_code_ingestion():
    test_cases = [
        {
            "id": 1,
            "files": ["tests/code/acronym.go", "tests/code/animal_magic.go", "tests/code/atbash_cipher_test.go"],
            "language": "go",
            "return_type": None,
            "chunk_size": None,
            "tokenizer": "gpt2",
            "include_nodes": True,
            "vector_store": vector_store_qdrant,
            "client": abstract_qdrant_client,
            "expected": [True, True],
        },
        {
            "id": 2,
            "files": ["tests/code/acronym.go", "tests/code/animal_magic.go", "tests/code/atbash_cipher_test.go"],
            "language": "go",
            "return_type": None,
            "chunk_size": None,
            "tokenizer": "gpt2",
            "include_nodes": True,
            "vector_store": vector_store_weaviate,
            "client": abstract_weaviate_client,
            "expected": [True, True],
        },
        {
            "id": 3,
            "files": ["tests/code/acronym.go", "tests/code/animal_magic.go", "tests/code/atbash_cipher_test.go"],
            "language": "go",
            "return_type": None,
            "chunk_size": None,
            "tokenizer": "gpt2",
            "include_nodes": True,
            "vector_store": vector_store_milvus,
            "client": abstract_milvus_client,
            "expected": [True, True],
        },
        {
            "id": 4,
            "files": ["tests/code/acrony.go", "tests/code/animal_magc.go", "tests/code/atbash_cipher_tes.go"],
            "language": "go",
            "return_type": None,
            "chunk_size": None,
            "tokenizer": "gpt2",
            "include_nodes": True,
            "vector_store": vector_store_qdrant,
            "client": abstract_qdrant_client,
            "expected": None,
        },
        {
            "id": 5,
            "files": ["tests/code/acronym.go", "tests/code/animal_magic.go", "tests/code/atbash_cipher_test.go"],
            "language": "pokemon",
            "return_type": None,
            "chunk_size": None,
            "include_nodes": None,
            "tokenizer": "gpt2",
            "vector_store": vector_store_qdrant,
            "client": abstract_qdrant_client,
            "expected": None,
        },
        {
            "id": 6,
            "files": ["tests/code/acronym.go", "tests/code/animal_magic.go", "tests/code/atbash_cipher_test.go"],
            "language": "python",
            "return_type": "tex",
            "chunk_size": None,
            "tokenizer": "gpt2",
            "include_nodes": None,
            "vector_store": vector_store_qdrant,
            "client": abstract_qdrant_client,
            "expected": None,
        },
    ]
    for c in test_cases:
        try:
            ingestor = IngestCode(vector_store=c["vector_store"])
            index = ingestor.ingest(files = c["files"], embedding_model="sentence-transformers/all-MiniLM-L6-v2", language=c["language"], return_type=c["return_type"], tokenizer=c["tokenizer"], chunk_size=c["chunk_size"], include_nodes=c["include_nodes"])
            outcome = [isinstance(index, VectorStoreIndex), c["client"].check_collection_exists()]
        except Exception:
            outcome = None
        assert outcome == c["expected"], f"Failed on case id {c['id']}"
