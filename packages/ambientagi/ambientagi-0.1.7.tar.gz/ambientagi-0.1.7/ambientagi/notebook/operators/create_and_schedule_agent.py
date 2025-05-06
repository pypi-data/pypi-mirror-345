# pip install ambientagi
import asyncio

from ambientagi.services.agent_service import AmbientAgentService


def run_browser_task(agent_id: str, task: str):
    """
    Helper function that wraps the async browser task in a synchronous call.
    """
    service = AmbientAgentService(api_key="")
    browser_agent = service.create_browser_agent(agent_id)

    # Use asyncio.run(...) inside the function
    async def _async_run():
        result = await browser_agent.run_task(task)
        print("Scheduled Browser Task Result:", result)

    asyncio.run(_async_run())


def main():
    service = AmbientAgentService()

    # Create an agent
    resp = service.create_agent(
        agent_name="BrowserAssistant",
        description="A browser agent to help crypto enthusiasts surf the internet for market trends and news",
        wallet_address="0x123456789ABCDEF",
    )
    agent_id = resp["agent_id"]

    # The actual task logic
    task = "Go to Reddit, search for 'AI news', and return the first post title."

    # Schedule it to run every 60 seconds
    service.schedule_agent(
        agent_id=agent_id, func=lambda: run_browser_task(agent_id, task), interval=60
    )
    print(f"Agent {agent_id} scheduled every 60 seconds. Press Ctrl+C to exit.")

    # Keep the script alive if your schedule runs on the same process
    try:
        while True:
            asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Stopping scheduler...")


if __name__ == "__main__":
    main()
