import logging
from functools import lru_cache

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from alumnium.drivers import BaseDriver
from alumnium.tools import ALL_TOOLS

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ActorAgent(BaseAgent):
    def __init__(self, driver: BaseDriver, llm: BaseChatModel):
        self._load_prompts()

        self.driver = driver
        llm = llm.bind_tools(list(ALL_TOOLS.values()))

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.prompts["system"]),
                ("human", self.prompts["user"]),
            ]
        )

        self.chain = prompt | self._with_retry(llm)

    def invoke(self, goal: str, step: str):
        if not step.strip():
            return

        logger.info("Starting action:")
        logger.info(f"  -> Goal: {goal}")
        logger.info(f"  -> Step: {step}")

        aria = self.driver.aria_tree
        aria_xml = aria.to_xml()
        message = self.__prompt(goal, step, aria_xml)

        logger.info(f"  <- Tools: {message.tool_calls}")
        logger.info(f"  <- Usage: {message.usage_metadata}")

        # Move to tool itself to avoid hardcoding it's parameters.
        for tool_call in message.tool_calls:
            tool = ALL_TOOLS[tool_call["name"]](**tool_call["args"])
            if "id" in tool.model_fields_set:
                tool.id = aria.cached_ids[tool.id]
            if "from_id" in tool.model_fields_set:
                tool.from_id = aria.cached_ids[tool.from_id]
            if "to_id" in tool.model_fields_set:
                tool.to_id = aria.cached_ids[tool.to_id]

            tool.invoke(self.driver)

    @lru_cache()
    def __prompt(self, goal: str, step: str, aria: str):
        return self.chain.invoke({"goal": goal, "step": step, "aria": aria})
