# test_browser_firefox.py

import asyncio

from ambientagi.services.agent_service import AmbientAgentService


async def main():
    service = AmbientAgentService(api_key="sk-...")  # your OpenAI API key

    agent = service.create_agent(
        agent_name="FirefoxAgent",
        wallet_address="0xFIREFOX",
        description="Search 'AmbientAGI GitHub' and return the repo link.",
    )

    browser_agent = service.create_browser_agent(
        agent_id=agent["agent_id"],
        browser_config={
            "browser_class": "firefox",  # ✅ key line for Firefox
            "headless": False,
            "new_context_config": {
                "window_width": 1200,
                "window_height": 800,
            },
        },
    )

    result = await browser_agent.run_task(
        model="gpt-4o",
        task="Search 'AmbientAGI GitHub' and return the repository link.",
    )

    print("\n[FIREFOX RESULT]:", result.final_result())


if __name__ == "__main__":
    asyncio.run(main())
