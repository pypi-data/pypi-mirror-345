# pip install ambientagi
import json
import os

from ambientagi.services.agent_service import AmbientAgentService

# Initialize the service
service = AmbientAgentService(api_key=os.getenv("OPENAI_API_KEY") or "")

# Create an agent
response = service.create_agent(
    agent_name="Assistant for DeFi monitoring",
    description="A browser agent to help crypto enthusiasts surf the internet for market trends and news",
    wallet_address="0x123456789ABCDEF",
)
print("Create Agent Response:")
print(json.dumps(response, indent=4))


# Attach token to agent
agent_id = response["agent_id"]
attach_token = service.add_blockchain(agent_id)

creds_resp = attach_token.create_eth_token(
    privateKey=os.getenv("MY-PRIVATE-KEY"),
    token_name="aa45",
    symbol="app",
    buy_value_eth=0.001,
    image_path="mytoken.png",
)


creds_resp = attach_token.create_solana_token(
    funder_private_key=os.getenv("SOLANA_API_KEY"),
    amount_sol=0.001,  # Required only if using a new wallet
    token_name="aa49",
    token_symbol="APP",  # 🔥 Use 'token_symbol' instead of 'symbol'
    token_description="This is a test token",
    twitter="https://twitter.com/myproject",
    telegram="https://t.me/myproject",
    website="https://myproject.com",
    image_path="mytoken.png",
    dev_buy=0.001,  # Amount of SOL for dev buy
    use_new_wallet=False,
)
