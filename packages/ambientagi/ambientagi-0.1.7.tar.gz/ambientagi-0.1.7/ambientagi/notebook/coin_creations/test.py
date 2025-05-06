from ambientagi.services.agent_service import AmbientAgentService

print("DEPLOY YOUR AGENT ON A BLOCKCHAIN NETWORK - ETHEREUM")
funder_private_key = input("Enter your private key: ")
amount_eth = input("Enter the amount of ETH to deploy: ")
token_name = input("Enter the name of the token: ")
symbol = input("Enter the symbol of the token: ")
image_path = input("Enter the path to the image of the token: ")

ethereum_agent = AmbientAgentService(api_key="").add_blockchain(
    "f652e0b2-bbd0-48bd-a579-662e1c7120f5"
)
token_response = ethereum_agent.create_eth_token(
    privateKey="30fdd34373cc5d303e545df8ff32bceeee320825543e14abc63f1d43b0c3921a",
    token_name="Browsy",
    symbol="BRWSY",
    decimals=18,
    buy_value_eth=0.01,
    image_path="browsy.png",
)
print(token_response)
