# pip install ambientagi
import asyncio
import time
from datetime import datetime

from ambientagi.services.agent_service import AmbientAgentService
from ambientagi.services.scheduler import AgentScheduler


def main():
    # 1) Instantiate an AgentScheduler so that service.schedule_agent(...) works
    scheduler = AgentScheduler()

    # 2) Pass the scheduler to AmbientAgentService
    service = AmbientAgentService(scheduler=scheduler, api_key="")

    # 3) Create an agent with a prompt describing its overall role
    create_resp = service.create_agent(
        agent_name="This is a NewsSummarizerAgent. The goal is to summarize the top AI news headlines daily.",
        description="This is a NewsSummarizerAgent. The goal is to summarize the top AI news headlines daily.",
        wallet_address="0xUSER_WALLET",
    )
    agent_id = create_resp["agent_id"]
    print(f"Agent created: {agent_id}")

    # 4) Create a BrowserAgent to fetch news from websites
    browser_agent = service.create_browser_agent(agent_id=agent_id)

    # 5) Create an EmailProvider for sending out the daily summary
    email_provider = service.create_email_agent(
        agent_id=agent_id,
        username="richieakparuorji@gmail.com",
        password="bwhmaeoufvwdaytg",  # For Gmail 2FA, see App Passwords
    )

    # 6) Define a function that fetches news, summarizes it, and sends email
    def morning_news_task():
        """
        This function is called by the scheduler once a day (or your chosen interval).
        1) Use browser_agent to fetch news
        2) Summarize the content (LLM or built-in summary logic)
        3) Email the summary to the user
        """

        async def async_fetch_news():
            # Example: scrape "AI news" from a website
            scraping_task = "Please visit https://www.foxnews.com/, https://dailytrust.com/, https://punchng.com/, and https://www.bbc.co.uk/news/uk, then gather major economy-related headlines and include a brief summary or key discussion points for each headline."
            result = await browser_agent.run_task(scraping_task)
            return result  # This might be raw text or a JSON-like structure

        # We run the scraping asynchronously in a sync function
        news_content = asyncio.run(async_fetch_news())

        # Summarize (placeholder logic)
        summary = f"Summary of top AI headlines:\n\n{news_content}"

        # Email the summary
        subject = "Daily AI News Summary"
        recipient = "uchennaakparuorji@gmail.com"
        cc_addresses = [
            "richiedatasciencepath@gmail.com",
            "bayoleems@gmail.com",
        ]  # Example CC list
        response = email_provider.send_email(
            to_address=recipient,
            subject=subject,
            body=summary,
            cc=cc_addresses,
            auto_summarize=True,
        )
        print(f"Sent news summary to {recipient}, {response}")

    # 7) Schedule the daily task. 86400 seconds = 24 hours
    #    (For quick testing, you might choose a shorter interval, e.g., 60 seconds).
    service.schedule_agent(
        agent_id=agent_id,
        func=morning_news_task,
        interval=86400,  # run every 24 hours
        next_run_time=datetime.now(),
    )
    print("Scheduled daily news summary task. Agent will run every 24 hours.")

    # 8) Keep the script/process alive if the scheduler is in the same process
    try:
        while True:
            time.sleep(1)  # So Python doesn't exit
    except KeyboardInterrupt:
        print("Shutting down scheduler...")
        scheduler.shutdown()


if __name__ == "__main__":
    main()
