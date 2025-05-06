from typing import Any, Dict, Optional

from browser_use import Agent
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContextConfig
from langchain_openai import ChatOpenAI
from pydantic import SecretStr


class BrowserAgent:
    def __init__(
        self,
        agent: dict,
        api_key: Optional[str] = None,
        browser_config: Optional[Dict[str, Any]] = None,
        context_config: Optional[Dict[str, Any]] = None,
    ):
        self.name = agent["agent_name"]
        self.wallet_address = agent["wallet_address"]
        self.task = agent["description"]

        self.api_key = api_key  # ✅ store the passed-in user key

        self.browser_config = BrowserConfig(**(browser_config or {}))
        self.context_config = BrowserContextConfig(**(context_config or {}))
        self.browser_config.new_context_config = self.context_config

    async def run_task(self, task: Optional[str] = None, model: str = "gpt-4o"):
        task = task or self.task

        browser = Browser(config=self.browser_config)

        agent = Agent(
            task=task,
            llm=ChatOpenAI(
                model=model,
                api_key=SecretStr(self.api_key) if self.api_key else None,
            ),
            browser=browser,
            browser_context=await browser.new_context(config=self.context_config),
        )
        return await agent.run()
