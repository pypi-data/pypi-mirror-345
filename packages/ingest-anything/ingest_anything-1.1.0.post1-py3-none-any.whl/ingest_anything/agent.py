try:
    from agent_types import IngestAnythingFunctionAgent, IngestAnythingReActAgent, IngestCodeFunctionAgent, IngestCodeReActAgent
except ModuleNotFoundError:
    from .agent_types import IngestAnythingFunctionAgent, IngestAnythingReActAgent, IngestCodeFunctionAgent, IngestCodeReActAgent
from llama_index.core.llms import LLM
from llama_index.core.readers.base import BaseReader
from llama_index.core.vector_stores.types import BasePydanticVectorStore
from llama_index.core.tools import BaseTool
from typing import Optional, Literal, List, Callable, Awaitable


class IngestAgent:
    """An agent factory class for creating different types of ingestion agents.

    This class provides a factory method to create various types of ingestion agents based on
    the specified parameters. It can create agents for general content ingestion or code-specific
    ingestion, using either function calling or ReAct patterns.

    Attributes:
        None

    Methods:
        create_agent: Creates and returns an ingestion agent based on specified parameters.
    """

    def __init__(self) -> None:
        pass

    def create_agent(
        self,
        vector_database: BasePydanticVectorStore,
        llm: LLM,
        reader: Optional[BaseReader] = None,
        ingestion_type: Literal["anything", "code"] = "anything",
        agent_type: Literal["function_calling", "react"] = "function_calling",
        tools: Optional[List[BaseTool | Callable | Awaitable]] = None,
        query_transform: Optional[Literal["hyde", "multi_step"]] = None,
    ) -> (
        IngestAnythingFunctionAgent
        | IngestAnythingReActAgent
        | IngestCodeFunctionAgent
        | IngestCodeReActAgent
    ):
        """Creates an agent based on the specified configuration.

        This method instantiates and returns an appropriate agent based on the ingestion type
        and agent type specified. The agent will be configured with the provided vector database,
        language model, and optional components.

        Args:
            vector_database (BasePydanticVectorStore): Vector database for storing and retrieving embeddings.
            llm (LLM): Language model instance to be used by the agent.
            reader (Optional[BaseReader]): Document reader for processing input files. Defaults to None.
            ingestion_type (Literal["anything", "code"]): Type of content to be ingested. Defaults to "anything".
            agent_type (Literal["function_calling", "react"]): Type of agent architecture. Defaults to "function_calling".
            tools (Optional[List[BaseTool | Callable | Awaitable]]): List of tools available to the agent. Defaults to None.
            query_transform (Optional[Literal["hyde", "multi_step"]]): Query transformation method. Defaults to None.

        Returns:
            Union[IngestAnythingFunctionAgent, IngestAnythingReActAgent, IngestCodeFunctionAgent, IngestCodeReActAgent]:

                An instantiated agent of the appropriate type based on the specified configuration.
                - IngestAnythingFunctionAgent: For general content with function calling
                - IngestAnythingReActAgent: For general content with ReAct architecture
                - IngestCodeFunctionAgent: For code-specific content with function calling
                - IngestCodeReActAgent: For code-specific content with ReAct architecture
        """
        if ingestion_type == "anything":
            if agent_type == "function_calling":
                return IngestAnythingFunctionAgent(
                    vector_database=vector_database,
                    reader=reader,
                    llm=llm,
                    tools=tools,
                    query_transform=query_transform,
                )
            else:
                return IngestAnythingReActAgent(
                    vector_database=vector_database,
                    reader=reader,
                    llm=llm,
                    tools=tools,
                    query_transform=query_transform,
                )
        else:
            if agent_type == "function_calling":
                return IngestCodeFunctionAgent(
                    vector_database=vector_database,
                    llm=llm,
                    tools=tools,
                    query_transform=query_transform,
                )
            else:
                return IngestCodeReActAgent(
                    vector_database=vector_database,
                    llm=llm,
                    tools=tools,
                    query_transform=query_transform,
                )
