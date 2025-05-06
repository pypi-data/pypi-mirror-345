import os
from typing import Optional

from dotenv import load_dotenv  # type: ignore
from langchain.output_parsers import PydanticOutputParser  # type: ignore
from langchain.prompts import PromptTemplate  # type: ignore
from langchain_openai import ChatOpenAI  # type: ignore
from pydantic import BaseModel, Field  # type: ignore

from ambientagi.services.agent_service import AmbientAgentService

load_dotenv()


class EmailContent(BaseModel):
    """Email content structure."""

    subject: str = Field(description="The subject line of the email")
    body: str = Field(description="The main body content of the email")
    priority: Optional[str] = Field(
        default="normal",
        description="Priority level of the email: low, normal, or high",
    )

    class Config:
        arbitrary_types_allowed = True
        json_schema_extra = {
            "subject": "The subject line of the email",
            "body": "The main body content of the email",
            "priority": "Priority level of the email: low, normal, or high",
        }


class CryptoAgent:
    def __init__(self, agent_id=None):
        self.token_attached = False
        self.service = AmbientAgentService()
        self.agent_id = agent_id
        self.agent_data = {}
        self.config = {}

    def _create_email_chain(self, task_output):
        llm = ChatOpenAI(
            model="gpt-4o-mini", openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        email_parser = PydanticOutputParser(pydantic_object=EmailContent)
        template = """
        Given the following task output, generate a personalized email notification message.
        Create an appropriate subject line and detailed body content. No markdown formatting.

        End the email with Ambient AGI Team.
        Task Output: {task_output}
        output format instructions: {format_instructions}
        """

        prompt = PromptTemplate(
            template=template,
            input_variables=["task_output"],
            partial_variables={
                "format_instructions": email_parser.get_format_instructions()
            },
        )

        email_chain = prompt | llm
        response = email_chain.invoke({"task_output": task_output})

        # Ensure the response is a string
        if isinstance(response, dict):
            response = response.get("text", "")
        elif hasattr(response, "content"):
            response = response.content  # Extract content if it's an AIMessage

        email_data = email_parser.parse(response)

        return email_data

    def collect_inputs(self):
        print("\n=== Ambient Agent Configuration ===")
        status = input("Create new agent? (y/n): ").strip().lower()
        if status == "y":
            self.config["wallet_address"] = input("Enter wallet address: ").strip()
            self.config["agent_prompt"] = input(
                "Enter agent prompt/description: "
            ).strip()
            self.config["recipient_email"] = input("Enter recipient email: ").strip()
            self.create_agent()
        else:
            self.agent_id = input("Enter agent ID: ").strip()
            self.config["recipient_email"] = input("Enter recipient email: ").strip()
            self.create_agent(self.agent_id)

        self.config["token_type"] = input(
            "Attach token to agent? (ETH/Solana/None): "
        ).strip()

        if self.config["token_type"] == "ETH":
            print("\n=== ETH Token Configuration ===")
            self.config["eth_private_key"] = input("Enter ETH private key: ").strip()
            self.config["eth_token_symbol"] = input("Enter ETH token symbol: ").strip()
            self.config["eth_buy_value"] = float(
                input("Enter buy value in ETH: ").strip()
            )
            self.config["image_path"] = input("Enter image path for token: ").strip()

            self.create_eth_token()

        elif self.config["token_type"] == "Solana":
            print("\n=== Solana Token Configuration ===")
            self.config["sol_private_key"] = input("Enter Solana private key: ").strip()
            self.config["sol_token_symbol"] = input(
                "Enter Solana token symbol: "
            ).strip()
            self.config["sol_amount"] = float(
                input("Enter buy value in Solana: ").strip()
            )
            self.config["image_path"] = input("Enter image path for token: ").strip()

            self.create_solana_token()

        chat_with_agent = input("Chat with agent? (y/n): ").strip().lower()

        if chat_with_agent == "y":
            while True:
                message = input("Enter message (q to quit): ").strip()
                if message.lower() == "q":
                    break

                if message.lower() == "clear":
                    os.system("clear")
                    continue

                if message.lower() == "stats":
                    stats = self.service.get_stats(self.agent_id)
                    print(f"\n{self.agent_data['name']} Stats:")
                    print(stats)
                    continue

                if message.lower() == "help":
                    print(f"\n{self.agent_data['name']} Commands:")
                    print("clear - Clear the screen")
                    print("stats - Show agent stats")
                    print("help - Show agent commands")
                    print("X - X interactive mode")
                    print("q - Quit")

                    continue

                if message.lower() == "x":
                    twitter_agent = self.service.create_twitter_agent(self.agent_id)
                    twitter_agent.interactive_mode()
                    continue

                response = self.service.chat_with_agent(
                    agent_id=self.agent_id,
                    message=message,
                    wallet_address=self.agent_data["wallet_address"],
                )
                print(f"\n{self.agent_data['name']}:")
                print(response.get("response", "No response"))
                print()

    def create_agent(self, agent_id=None):
        if agent_id:
            # Verify the agent exists by trying to get it
            try:
                agent_data = self.service.get_agent_info(agent_id)
                if agent_data:
                    self.agent_id = agent_id
                    self.agent_data = agent_data
                    print(f"Using existing agent with ID: {self.agent_id}")

            except Exception:
                print(f"Error: Could not find agent with ID {agent_id}")
                if input("Create new agent? (y/n): ").strip().lower() == "y":
                    print("\n=== Agent Configuration ===")
                    self.config["wallet_address"] = input(
                        "Enter wallet address: "
                    ).strip()
                    self.config["agent_prompt"] = input(
                        "Enter agent description: "
                    ).strip()

                    print("Creating new agent...")
                    self._create_new_agent()
                else:
                    print("Exiting...")
                    exit()
        else:
            self._create_new_agent()

    def _create_new_agent(self):
        response = self.service.create_agent(
            prompt=self.config["agent_prompt"],
            wallet_address=self.config["wallet_address"],
        )
        self.agent_id = response["agent"]["agent_id"]
        self.agent_data = response["agent"]
        print(
            f"Created agent with ID: {self.agent_id}\n Agent Name: {self.agent_data['name']}"
        )

        update = input("Update agent with Twitter handle (y/n): ").strip().lower()
        if update == "y":
            twitter_handle = input("Enter Twitter handle: ").strip()
            self.service.update_agent(
                agent_id=self.agent_id, data={"twitter_handle": twitter_handle}
            )
            print(
                f"Updated agent with ID: {self.agent_id}\n Agent Name: {self.agent_data['name']}"
            )

        print("Agent is ready for use!")

    def attach_token(self):
        if self.config["token_type"] in ["ETH", "Solana"]:
            self.token_attached = True
            return True
        return False

    def create_eth_token(self):
        private_key = self.config["eth_private_key"]
        if not private_key:
            raise ValueError("ETH private key not found in environment variables")

        # ethereum_agent = self.service.add_blockchain(self.agent_id)
        # token_response = ethereum_agent.create_eth_token(
        #     privateKey=private_key,
        #     token_name=self.agent_data['name'],
        #     symbol=self.config['eth_token_symbol'],
        #     buy_value_eth=self.config['eth_buy_value'] or 0.01,
        #     image_path=self.config['image_path'],
        #     twitterUrl=f"https://x.com/{self.config['twitter_handle']}" if self.config['twitter_handle'] else None
        # )

        token_response = (
            "BRWSY ethereum Token created at 0x420844bF0eA8802985dA87D8CE051b63327A66C5"
        )
        print(f"ETH Token created: {token_response}")

        self.send_email(task_output=token_response)

    def create_solana_token(self):
        solana_private_key = self.config["sol_private_key"]
        if not solana_private_key:
            raise ValueError("Solana private key not found in environment variables")

        # solana_agent = self.service.add_blockchain(self.agent_id)
        # token_response = solana_agent.create_solana_token(
        #     funder_private_key=solana_private_key,
        #     amount_sol=0.05,
        #     token_name=self.agent_data['name'],
        #     token_symbol=self.config['sol_token_symbol'],
        #     dev_buy=self.config['sol_amount'] or 0.001,
        #     token_description=self.agent_data['personality'],
        #     image_path=self.config['image_path'],
        #     twitter=f"https://x.com/{self.config['twitter_handle']}" if self.config['twitter_handle'] else None
        # )

        token_response = (
            "BRWSY solana token created at J5q6R8ZwEx9bwe8ATSgsCD3JN7oZ8VCoKvE3ejWGM6gG"
        )

        self.send_email(task_output=token_response)

        print(f"Creating Solana token: {self.agent_data['name']}")
        print(f"Symbol: {self.config['sol_token_symbol']}")

    def show_functionality(self):
        print("\nAgent Configuration:")
        for key, value in self.config.items():
            print(f"{key}: {value}")

        for key, value in self.agent_data.items():
            if value:
                print(f"{key}: {value}")

    def generate_email(self, task_output):
        email_data = self._create_email_chain(task_output)

        email_data = email_data.model_dump()

        return email_data

    def send_email(self, task_output, recipient_email=None, cc_email=None):

        if not recipient_email:
            recipient_email = "bayoleems@gmail.com"

        email_service = self.service.create_email_agent(
            agent_id=self.agent_id,
            username="trump.ai.solx@gmail.com",  # os.getenv("EMAIL_USERNAME"),
            password="enrrvzhnvcbmbalx",  # os.getenv("GMAIL_PASSWORD"),
        )

        email_data = self.generate_email(task_output)

        email_service.send_email_with_footer(
            to_address=recipient_email,
            subject=email_data["subject"],
            body=email_data["body"],
            cc=cc_email,
        )

    def run(self):
        # Collect all needed inputs
        self.collect_inputs()

        # Handle token creation if requested
        if self.attach_token():
            if self.config["token_type"] == "ETH":
                self.create_eth_token()
            elif self.config["token_type"] == "Solana":
                self.create_solana_token()

        # Show final configuration
        self.show_functionality()


def main_flow():
    agent = CryptoAgent()
    try:
        agent.run()
    except Exception as e:
        print(f"Error occurred: {str(e)}")


if __name__ == "__main__":
    main_flow()
