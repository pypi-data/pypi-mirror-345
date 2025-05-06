import asyncio

from ambientagi.services.openai_agent_wrapper import AmbientAgentServiceExtended


async def main():
    # 1) Initialize your extended Ambient service with your OpenAI API key
    api_key = ""
    service = AmbientAgentServiceExtended(api_key=api_key, scheduler=None)

    # 2) Create our Spanish and English agents
    service.create_openai_agent(
        name="SpanishAgent", instructions="You only speak Spanish."
    )
    service.create_openai_agent(
        name="EnglishAgent", instructions="You only speak English."
    )

    # 3) Create the Triage agent
    service.create_openai_agent(
        name="TriageAgent",
        instructions="Handoff to the appropriate agent based on the language of the request.",
    )

    # 4) Assign the handoffs property on Triage agent to point to the Spanish & English agents
    #    Each call to create_openai_agent returns an Agent, but we also have them stored
    #    internally in service.openai_wrapper.agents. Let's retrieve them by name:
    triage_agent_obj = service.openai_wrapper.agents["TriageAgent"]
    spanish_agent_obj = service.openai_wrapper.agents["SpanishAgent"]
    english_agent_obj = service.openai_wrapper.agents["EnglishAgent"]

    # Now set the triage agent's handoffs
    triage_agent_obj.handoffs = [spanish_agent_obj, english_agent_obj]

    # 5) Test by running the Triage agent asynchronously
    #    We'll give it a Spanish input so it hands off to the Spanish agent:
    user_input = "hello good ebvnenig"
    result_obj = await service.run_openai_agent_async("TriageAgent", user_input)
    print("Final agent output:", result_obj)


if __name__ == "__main__":
    asyncio.run(main())
