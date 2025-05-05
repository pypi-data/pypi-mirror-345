import abc
import logging
from gllm_agents.constants import DEFAULT_AGENT_TIMEOUT as DEFAULT_AGENT_TIMEOUT
from gllm_agents.memory.base import BaseMemory as BaseMemory
from gllm_agents.tools.base import BaseTool as BaseTool
from gllm_agents.tools.nested_agent_tool import NestedAgentTool as NestedAgentTool
from gllm_agents.types import AgentProtocol as AgentProtocol
from langchain.agents import AgentExecutor as LangChainAgentExecutor
from langchain_core.language_models import BaseLanguageModel as BaseLanguageModel
from typing import Any

class Agent(AgentProtocol, metaclass=abc.ABCMeta):
    """Concrete Base class for agents.

    This class provides a basic structure and default implementations.
    Derived classes can override methods to add specific functionality.

    Attributes:
        name (str): The name of the agent.
        instruction (str): The system instruction for the agent.
        description (Optional[str]): A description of what the agent does.
        memory (Optional[BaseMemory]): The memory component for the agent.
        timeout (int): Maximum execution time in seconds.
        verbose (bool): Whether to enable verbose logging.
        logger (Any): Logger instance for the agent.
        llm (Optional[BaseLanguageModel]): The language model used by the agent.
        tools (List[BaseTool]): List of tools available to the agent.
        _nested_agent_tools (List[NestedAgentTool]): List of tools created from nested agents.
    """
    name: str
    instruction: str
    description: str | None
    memory: BaseMemory | None
    timeout: int
    verbose: bool
    logger: logging.Logger
    llm: BaseLanguageModel | None
    tools: list[BaseTool]
    def __init__(self, name: str, instruction: str = 'You are a helpful assistant.', description: str | None = None, memory: BaseMemory | None = None, timeout: int = ..., verbose: bool = False, log_level: int = ..., llm: BaseLanguageModel | None = None, tools: list[BaseTool] | None = None, agents: list[AgentProtocol] | None = None) -> None:
        """Initializes the base agent with core attributes."""
    def setup_executor(self, tools: list[BaseTool], llm: BaseLanguageModel) -> LangChainAgentExecutor:
        """Default implementation returning a standard LangChainAgentExecutor.

        Subclasses (like GLCHatAgent) should override this to provide specific executors
        (e.g., PIIAwareAgentExecutor).

        Requires tools and llm to be passed or accessible.
        """
    def run(self, query: str, tools: list[BaseTool] | None = None, llm: BaseLanguageModel | None = None) -> dict[str, Any]:
        """Run the agent with the provided query, tools, and LLM.

        Args:
            query: The query string to process.
            tools: The tools available to the agent. If None, uses self.tools.
            llm: The language model to use. If None, uses self.llm.

        Returns:
            A dictionary containing the input query and output response.
        """
    async def arun(self, query: str, tools: list[BaseTool] | None = None, llm: BaseLanguageModel | None = None) -> dict[str, Any]:
        """Run the agent asynchronously with the provided query, tools, and LLM.

        Args:
            query: The query string to process.
            tools: The tools available to the agent. If None, uses self.tools.
            llm: The language model to use. If None, uses self.llm.

        Returns:
            A dictionary containing the input query and output response.
        """
