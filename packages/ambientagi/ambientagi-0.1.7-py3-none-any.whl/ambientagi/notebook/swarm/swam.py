from swarms import Agent  # type: ignore
from swarms.prompts.finance_agent_sys_prompt import (  # type: ignore
    FINANCIAL_AGENT_SYS_PROMPT,
)

# Initialize the agent
agent = Agent(
    agent_name="Financial-Analysis-Agent",
    system_prompt=FINANCIAL_AGENT_SYS_PROMPT,
    model_name="gpt-4o-mini",
    max_loops=1,
    autosave=True,
    dashboard=False,
    verbose=True,
    dynamic_temperature_enabled=True,
    saved_state_path="finance_agent.json",
    user_name="swarms_corp",
    retry_attempts=1,
    context_length=200000,
    return_step_meta=False,
    output_type="string",
    streaming_on=False,
)


agent.run(
    "How can I establish a ROTH IRA to buy stocks and get a tax break? What are the criteria"
)


agent = Agent(
    agent_name="Stock-Analysis-Agent",
    model_name="gpt-4o-mini",
    max_loops="auto",
    interactive=True,
    streaming_on=True,
)

agent.run("What is the current market trend for tech stocks?")


# https://github.com/kyegomez/swarms
