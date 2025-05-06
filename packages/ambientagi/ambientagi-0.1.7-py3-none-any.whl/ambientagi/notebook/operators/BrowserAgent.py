# pip install ambientagi
import asyncio

from ambientagi.services.agent_service import AmbientAgentService


async def main():
    # 1) Initialize AmbientAgentService
    service = AmbientAgentService(api_key="")

    # 2) Create an agent via the orchestrator
    create_resp = service.create_agent(
        agent_name="BrowserAssistant",
        description="A browser agent to help crypto enthusiasts surf the internet for market trends and news",
        wallet_address="0x123456789ABCDEF",
    )
    print("Create Agent Response:", create_resp)
    # agent_id is inside create_resp["agent"]["agent_id"]
    agent_id = create_resp["agent_id"]

    # 3) Convert the existing agent record into a BrowserAgent
    browser_agent = service.create_browser_agent(agent_id)
    print(f"BrowserAgent '{browser_agent.name}' initialized.")

    # 4) Run an async task (the agent's logic)
    #    e.g., "Go to Reddit, search for 'AI tools', return first post title."
    task = "go to octogpt https://www.google.com and get me whale trending coin"
    result = await browser_agent.run_task(task)
    print("BrowserAgent Task Result:", result)


# Execute the async main
asyncio.run(main())
