import logging
from functools import lru_cache

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

from alumnium.drivers import BaseDriver

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class PlannerAgent(BaseAgent):
    LIST_SEPARATOR = "%SEP%"

    def __init__(self, driver: BaseDriver, llm: BaseChatModel):
        self._load_prompts()
        self.driver = driver

        example_prompt = ChatPromptTemplate.from_messages(
            [
                ("human", self.prompts["user"]),
                ("ai", "{actions}"),
            ]
        )
        self.prompt_with_examples = FewShotChatMessagePromptTemplate(
            examples=[],
            example_prompt=example_prompt,
        )
        final_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.prompts["system"].format(separator=self.LIST_SEPARATOR)),
                self.prompt_with_examples,
                ("human", self.prompts["user"]),
            ]
        )

        self.chain = final_prompt | self._with_retry(llm)

    def add_example(self, goal: str, actions: list[str]):
        self.prompt_with_examples.examples.append(
            {
                "goal": goal,
                "aria": "",
                "actions": self.LIST_SEPARATOR.join(actions),
            }
        )

    def invoke(self, goal: str) -> list[str]:
        logger.info("Starting planning:")
        logger.info(f"  -> Goal: {goal}")

        aria = self.driver.aria_tree
        aria_xml = aria.to_xml()
        message = self.__prompt(goal, aria_xml)

        logger.info(f"  <- Result: {message.content}")
        logger.info(f"  <- Usage: {message.usage_metadata}")

        response = message.content.strip()
        response = response.removeprefix(self.LIST_SEPARATOR).removesuffix(self.LIST_SEPARATOR)

        steps = []
        for step in message.content.split(self.LIST_SEPARATOR):
            step = step.strip()
            if step and step.upper() != "NOOP":
                steps.append(step)

        return steps

    @lru_cache()
    def __prompt(self, goal: str, aria: str):
        return self.chain.invoke({"goal": goal, "aria": aria})
