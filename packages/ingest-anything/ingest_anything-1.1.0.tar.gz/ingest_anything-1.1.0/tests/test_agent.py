from agent_types import FunctionAgent, ReActAgent
from agent import IngestAgent, IngestAnythingFunctionAgent, IngestAnythingReActAgent, IngestCodeFunctionAgent, IngestCodeReActAgent
from llama_index.core import Settings
from llama_index.llms.mistralai import MistralAI
import os
from dotenv import load_dotenv
import weaviate
from llama_index.vector_stores.weaviate import WeaviateVectorStore

load_dotenv()

llm = MistralAI(api_key=os.getenv("mistralai_api_key"),model="mistral-small-latest")
Settings.llm = llm

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

def addition_tool(a: int, b: int):
    """Tool useful to sum two integer numbers"""
    return a+b

async def multiplication_tool(a: int, b: int):
    """Tool useful to multiply two integer numbers"""
    return a*b

# files to ingest
anything_files = ['tests/data/test.docx', 'tests/data/test0.png', 'tests/data/test1.csv', 'tests/data/test2.json', 'tests/data/test3.md', 'tests/data/test4.xml', 'tests/data/test5.zip']
code_files = ["tests/code/acronym.go", "tests/code/animal_magic.go", "tests/code/atbash_cipher_test.go"]

def test_everything():
    ## INITIALIZATION TEST ##

    agent_1 = IngestAgent().create_agent(vector_database=vector_store_weaviate, ingestion_type="anything", agent_type="function_calling", llm=llm, tools=[addition_tool,multiplication_tool])
    agent_2 = IngestAgent().create_agent(vector_database=vector_store_weaviate, ingestion_type="anything", agent_type="react",llm=llm)
    agent_3= IngestAgent().create_agent(vector_database=vector_store_weaviate, ingestion_type="code", agent_type="function_calling",llm=llm)
    agent_4 = IngestAgent().create_agent(vector_database=vector_store_weaviate, ingestion_type="code", agent_type="react",llm=llm, tools=[addition_tool,multiplication_tool])
    assert [isinstance(agent_1, IngestAnythingFunctionAgent), isinstance(agent_2, IngestAnythingReActAgent), isinstance(agent_3, IngestCodeFunctionAgent), isinstance(agent_4, IngestCodeReActAgent)] == [True, True, True, True]

    ## AGENTS TEST ##

    # anything agents
    agent_1.ingest(
        files_or_dir = anything_files,
        embedding_model = "sentence-transformers/all-MiniLM-L6-v2",
        chunker = "token",
        tokenizer = "gpt2",
    )
    function_agent_1 = agent_1.get_agent()
    agent_2.ingest(
        files_or_dir = anything_files,
        embedding_model = "sentence-transformers/all-MiniLM-L6-v2",
        chunker = "token",
        tokenizer = "gpt2",
    )
    react_agent_1 = agent_2.get_agent()

    # code agents
    agent_3.ingest(
        files = code_files,
        language="go",
        embedding_model = "sentence-transformers/all-MiniLM-L6-v2",
        tokenizer = "gpt2",
    )
    function_agent_2 = agent_3.get_agent()
    agent_4.ingest(
        files = code_files,
        language="go",
        embedding_model = "sentence-transformers/all-MiniLM-L6-v2",
        tokenizer = "gpt2",
    )
    react_agent_2 = agent_4.get_agent()
    assert [isinstance(function_agent_1, FunctionAgent), isinstance(react_agent_1, ReActAgent), isinstance(function_agent_2, FunctionAgent), isinstance(react_agent_2, ReActAgent)] == [True, True, True, True]
