<div align="center">
<h1>ingest-anything</h1>
<h2>From data to vector database effortlessly</h2>
</div>
<br>
<div align="center">
    <img src="https://raw.githubusercontent.com/AstraBert/ingest-anything/main/logo.png" alt="Ingest-Anything Logo">
</div>


**`ingest-anything`** is a python package aimed at providing a smooth solution to ingest non-PDF files into vector databases, given that most ingestion pipelines are focused on PDF/markdown files. Leveraging [chonkie](https://docs.chonkie.ai/getting-started/introduction), [PdfItDown](https://github.com/AstraBert/PdfItDown), [Llamaindex](https://www.llamaindex.ai), [Sentence Transformers](https://sbert.net) embeddings and [Qdrant](https://qdrant.tech), `ingest-anything` gives you a fully-automated pipeline for document ingestion within few lines of code!

Find out more about `ingest-anything` on the [Documentation website](https://pdfitdown.eu/built-with-pdfitdown/ingest-anything)!

## Workflow

<div align="center">
    <img src="https://raw.githubusercontent.com/AstraBert/ingest-anything/main/workflow.png" alt="Ingest-Anything Workflow">
</div>

**For text files**

- The input files are converted into PDF by PdfItDown
- The PDF text is extracted using LlamaIndex Docling reader
- The text is chunked exploiting Chonkie's functionalities
- The chunks are embedded thanks to Sentence Transformers models
- The embeddings are loaded into a Qdrant vector database

**For code files**
- The text is extracted from code files using LlamaIndex SimpleDirectoryReader
- The text is chunked exploiting Chonkie's CodeChunker
- The chunks are embedded thanks to Sentence Transformers models
- The embeddings are loaded into a Qdrant vector database

## Installation and usage

`ingest-anything` can be installed using `pip` in the following way:

```bash
pip install ingest-anything
# or, for a faster installation
uv pip install ingest-anything
```

And is available in your python scripts:

- You can **initialize the interface for text-based files** like this:

```python
from qdrant_client import QdrantClient, AsyncQdrantClient
from llama_index.vector_stores.qdrant import QdrantVectorStore

client_qdrant = QdrantClient("http://localhost:6333")
aclient_qdrant = AsyncQdrantClient("http://localhost:6333")
vector_store_qdrant = QdrantVectorStore(collection_name="Test",client=client_qdrant, aclient=aclient_qdrant)
ingestor = IngestAnything(vector_store=vector_store_qdrant)
```

- And **ingest** your files:

```python
# with a list of files
ingestor.ingest(chunker="late", files_or_dir=['tests/data/test.docx', 'tests/data/test0.png', 'tests/data/test1.csv', 'tests/data/test2.json', 'tests/data/test3.md', 'tests/data/test4.xml', 'tests/data/test5.zip'], embedding_model="sentence-transformers/all-MiniLM-L6-v2")
# with a directory
ingestor.ingest(chunker="token", files_or_dir="tests/data", tokenizer="gpt2", embedding_model="sentence-transformers/all-MiniLM-L6-v2")
```

- You can also **initialize the interface for code files** 

```python
import os
from dotenv import load_dotenv
import weaviate
from llama_index.vector_stores.weaviate import WeaviateVectorStore

load_dotenv()

cluster_url = os.getenv("weaviate_cluster_url")
api_key = os.getenv("weaviate_admin_key")
client_weaviate = weaviate.connect_to_weaviate_cloud(
    cluster_url=cluster_url,
    auth_credentials=weaviate.auth.AuthApiKey(api_key),
)
vector_store_weaviate = WeaviateVectorStore(
    weaviate_client=client_weaviate, index_name="Test"
)

ingestor = IngestCode(vector_store=vector_store_qdrant)
```

- And then **ingest your code files**:

```python
os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
ingestor.ingest(files=["tests/code/acronym.go", "tests/code/animal_magic.go", "tests/code/atbash_cipher_test.go"], embedding_model="text-embedding-3-small", language="go")
```

You can find a complete reference for the package in [REFERENCE.md](https://github.com/AstraBert/ingest-anything/tree/main/REFERENCE.md)

### Contributing

Contributions are always welcome!

Find contribution guidelines at [CONTRIBUTING.md](https://github.com/AstraBert/ingest-anything/tree/main/CONTRIBUTING.md)

### License and Funding

This project is open-source and is provided under an [MIT License](https://github.com/AstraBert/ingest-anything/tree/main/LICENSE).

If you found it useful, please consider [funding it](https://github.com/sponsors/AstraBert).