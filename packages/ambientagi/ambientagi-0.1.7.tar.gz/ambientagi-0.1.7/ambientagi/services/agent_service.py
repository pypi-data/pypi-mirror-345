from typing import Any, Dict, Optional, Set

from ambientagi.config.logger import setup_logger
from ambientagi.providers.email_provider import EmailProvider
from ambientagi.providers.telegram_provider import TelegramProvider
from ambientagi.services.ambient_blockchain import BlockchainService
from ambientagi.services.ambient_browser import BrowserAgent
from ambientagi.services.ambient_firecrawl import AmbientFirecrawl
from ambientagi.services.openai_agent_wrapper import OpenAIAgentWrapper
from ambientagi.services.scheduler import AgentScheduler
from ambientagi.services.twitter_service import TwitterService
from ambientagi.services.webui_agent import WebUIAgent
from ambientagi.utils.http_client import HttpClient

logger = setup_logger("Ambientlibrary.openaiwrapper")


class AmbientAgentService:
    """
    A single central service for:
      - Creating and updating agents via FastAPI.
      - Running local OpenAI-based agents with usage tracking.
    """

    DEFAULT_BASE_URL = "https://api-ambientgpt.ambientagi.ai/api/v1"

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        scheduler: Optional[AgentScheduler] = None,
    ):
        """
        Initialize the AmbientAgentService with a centralized HTTP client
        and an internal OpenAIAgentWrapper for local agent handling.
        """
        default_headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        self.client = HttpClient(
            base_url=base_url or self.DEFAULT_BASE_URL,
            default_headers=default_headers,
        )
        self.scheduler = scheduler

        # Our internal wrapper for local agent logic
        self.openai_wrapper = OpenAIAgentWrapper(
            api_key=api_key, scheduler=self.scheduler, ambient_service=self
        )

    # ------------------------------------------------------------------
    #  FastAPI-based Agent Methods (Creation, Retrieval, Updating, etc.)
    # ------------------------------------------------------------------

    def create_agent(
        self,
        agent_name: str,
        wallet_address: str,
        description: str = "",
        coin_address: Optional[str] = None,
        twitter_handle: Optional[str] = None,
        twitter_id: Optional[str] = None,
        status: str = "active",
    ) -> Dict[str, Any]:
        """
        Create an agent via POST /agent/create in your local FastAPI.
        """
        payload = {
            "agent_name": agent_name,
            "wallet_address": wallet_address,
            "description": description,
            "coin_address": coin_address,
            "twitter_handle": twitter_handle,
            "twitter_id": twitter_id,
            "status": status,
        }
        logger.info(f"Creating agent: name='{agent_name}', wallet='{wallet_address}'")
        return self.client.post("/agent/create", json=payload)

    def get_agent_info(self, agent_id: str) -> Dict[str, Any]:
        """
        GET /agent/{agent_id}
        """
        logger.info(f"Fetching agent info for agent_id={agent_id}")
        return self.client.get(f"/agent/{agent_id}")

    def update_agent(self, agent_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        PATCH /agent/{agent_id}/update
        """
        logger.info(f"Updating agent_id={agent_id} with {updates}")
        return self.client.patch(f"/agent/{agent_id}/update", json=updates)

    def _increment_usage(self, agent_id: str) -> Dict[str, Any]:
        """
        Internal method that increments usage_count in the DB via POST /agent/{agent_id}/increment.
        """
        logger.info(f"Incrementing usage for agent_id={agent_id}")
        return self.client.post(f"/agent/{agent_id}/increment")

    # ------------------------------------------------------------------
    #  Methods Exposing OpenAI Agent Logic (All in One Place)
    # ------------------------------------------------------------------

    def create_openai_agent(self, local_agent_name: str, instructions: str):
        """
        Creates a local agent (NOT the same as your DB agent). This is for local LLM usage.
        """
        return self.openai_wrapper.create_agent(local_agent_name, instructions)

    def run_openai_agent(self, local_agent_name: str, input_text: str, agent_id: str):
        """
        Runs a local openai-based agent. If agent_id is supplied, usage increments.
        """
        return self.openai_wrapper.run_agent(
            local_agent_name, input_text, agent_id=agent_id
        )

    async def run_openai_agent_async(
        self, local_agent_name: str, input_text: str, agent_id: str
    ):
        """
        Runs a local openai-based agent asynchronously.
        """
        return await self.openai_wrapper.run_agent_async(
            local_agent_name, input_text, agent_id=agent_id
        )

    def schedule_openai_agent(
        self, local_agent_name: str, input_text: str, interval: int
    ):
        """
        Schedules the local openai-based agent to run on an interval.
        """
        self.openai_wrapper.schedule_agent(local_agent_name, input_text, interval)

    # ------------------------------------------------------------------
    #  Additional Service Methods (Email, Telegram, Blockchain, etc.)
    # ------------------------------------------------------------------

    def schedule_agent(self, agent_id: str, func, interval: int, **kwargs):
        """
        Generic scheduling for any arbitrary function (non-OpenAI usage).
        """
        if self.scheduler is None:
            raise ValueError("Scheduler is not set.")

        job_id = f"agent_{agent_id}"
        logger.info(f"Scheduling agent_id={agent_id} every {interval} seconds.")
        self.scheduler.add_job(
            job_id=job_id, func=func, trigger="interval", seconds=interval, **kwargs
        )

    def create_browser_agent(
        self,
        agent_id: str,
        browser_config: Optional[dict] = None,
        context_config: Optional[dict] = None,
    ):
        agent = self.get_agent_info(agent_id)
        return BrowserAgent(
            agent,
            api_key=self.openai_wrapper.api_key,
            browser_config=browser_config,
            context_config=context_config,
        )

    def create_firecrawl_agent(self, agent_id: str):
        agent = self.get_agent_info(agent_id)
        return AmbientFirecrawl(agent)

    def add_blockchain(self, agent_id: str):
        agent = self.get_agent_info(agent_id)
        return BlockchainService(agent)

    def create_twitter_agent(self, agent_id: str):
        agent = self.get_agent_info(agent_id)
        return TwitterService(agent)

    def add_webui_agent(
        self,
        agent_id: str,
        config: Optional[Dict[str, Any]] = None,
        theme="Ocean",
        ip="127.0.0.1",
        port=7788,
    ) -> WebUIAgent:
        """
        Creates and returns a WebUIAgent for controlling the browser-based AI interface.
        """
        if config is None:
            from ambientagi.utils.webui.utils.default_config_settings import (
                default_config,
            )

            config = default_config()

        config["agent_id"] = agent_id
        return WebUIAgent(config=config, theme=theme, ip=ip, port=port)

    def create_email_agent(
        self,
        agent_id: str,
        smtp_server: str = "smtp.gmail.com",
        smtp_port: int = 587,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_tls: bool = True,
    ):
        """
        Instantiate an EmailProvider for the given agent with optional SMTP configuration.
        """
        agent_info = self.get_agent_info(agent_id)
        return EmailProvider(
            agent_info=agent_info,
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            username=username,
            password=password,
            use_tls=use_tls,
        )

    def create_telegram_agent(
        self,
        agent_id: str,
        bot_token: str,
        mentions: Optional[Set[str]] = None,
    ) -> TelegramProvider:
        """
        Instantiate a TelegramProvider for the given agent with a bot token and optional mention filters.
        """
        agent_info = self.get_agent_info(agent_id)
        return TelegramProvider(
            agent_info=agent_info, bot_token=bot_token, mentions=mentions
        )
