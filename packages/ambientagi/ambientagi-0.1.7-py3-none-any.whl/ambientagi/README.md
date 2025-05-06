
# 🌟 AmbientAGI: Technical Documentation

AmbientAGI merges **AI orchestration** with **crypto token rewards**, enabling users to:

1. 🚀 **Create and deploy** specialized AI agents in a **multi-tenant** environment.
2. 💰 **Mint tokens** on major blockchains (Solana or Ethereum) to reward agent activity.
3. 🎨 **Generate 3D/visual media** for each agent, turning them into branded, interactive personas.
4. 🏆 **Earn from agent usage**, verified on-chain to ensure transparency and authenticity.
5. 🔮 **Expand** into a broad set of real-world and crypto-focused use cases: job search assistance, analyzing trending coins, whale-tracking, yield farming alerts, and more.

---

## ✨ Features

1. 🏗️ **Multi-Tenant Orchestrator**: Host and manage user agents with unified logs and a centralized database.
2. 🐍 **Python Library**: Develop custom agent behaviors with built-in schedulers and blockchain hooks.
3. 🪙 **Token Minting**: Reward users by minting tokens on Solana or Ethereum for agent usage.
4. 🖼️ **3D/Visual Media Integration**: Generate and mint unique 3D/video representations of agents as NFTs.
5. 🔗 **Crypto Integration**: Leverage DeFi, staking, and wallet integration for a seamless crypto experience.

---

## 1. 🏢 Multi-Tenant Orchestrator

### 🛠️ Architecture

- **Central Orchestrator**: Manages all agents and ensures task scheduling and execution.
- **Database**: Stores agent configurations (e.g., name, wallet address, schedule, commands).
- **Scheduler**: Handles task scheduling using tools like APScheduler or Celery.
- **On-Chain Usage**: Logs agent activities on IPFS and references them in blockchain contracts for transparency.

---

## 2. 🐍 Easy-to-Use Python Library

AmbientAGI provides a Python library for developers to create and manage AI agents effortlessly.

### 📦 Installation

Install the library via `pip`:

```bash
pip install ambientagi
```

### 📝 Usage Example Generic Agent

```python
from ambientagi.services.agent_service import AmbientAgentService

# Initialize the service
service = AmbientAgentService(api_key=os.getenv("OPENAI_API_KEY"))

# Create an agent
create_resp = service.create_agent(
    agent_name="DeFiScanner",
    description="A defi scanner"
    wallet_address="0x123..."
)
print(create_resp)

# Update the agent
update_resp = service.update_agent(
    agent_id=create_res["agent_id"],
    twitter_handle="defi_updates",
    specialty="DeFi Monitoring"
)
print(update_resp)

# Chat with the agent
chat_resp = service.chat_with_agent(
    agent_id=create_resp["agent_id"],
    message="What’s the latest DeFi yield?",
    wallet_address="0x123..."
)
print(chat_resp)
```


### 📝 Usage Example Twitter Agent

```python
from ambientagi.services.agent_service import AmbientAgentService

# 1) Initialize the core agent service
service = AmbientAgentService(api_key=os.getenv("OPENAI_API_KEY"))

# 2) Create a new generic agent
create_resp = service.create_agent(
    agent_name="TwitterAssistant",
    description="A twitter assistance"
    wallet_address="0xABCDEF1234"
)
print("Create Agent Response:", create_resp)


agent_id = create_resp["agent_id"]

# 3) Convert the existing agent to a Twitter-enabled agent
twitter_agent = service.add_twitter_agent(agent_id)

# 3) Attach a Twitter agent wrapper for the existing agent
twitter_agent = service.add_twitter_agent(agent_id)

# 4) Update Twitter credentials
#    This ensures the agent's record is updated with your keys/tokens
creds_resp = twitter_agent.update_twitter_credentials(
    twitter_handle="myTwitterBot",
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET",
    access_token="YOUR_ACCESS_TOKEN",
    access_secret="YOUR_ACCESS_SECRET"
)
print("Update Twitter Credentials Response:", creds_resp)

# 5) Post a basic tweet
try:
    tweet_text = "Hello world from AmbientAGI Twitter agent!"
    tweet_result = twitter_agent.post_tweet(tweet_text)
    print("Posted tweet:", tweet_result)
except Exception as e:
    print("Error posting tweet:", e)

# 6) (Optional) Reply to a tweet
try:
    # Suppose you have a target tweet ID to reply to
    tweet_id_to_reply = "1234567890123456789"
    reply_text = "This is a reply from our AmbientAGI agent!"
    reply_result = twitter_agent.reply_to_tweet(tweet_id_to_reply, reply_text)
    print("Reply to Tweet Result:", reply_result)
except Exception as e:
    print("Error replying to tweet:", e)

# 7) (Optional) Quote Tweet
try:
    tweet_id_to_quote = "9876543210987654321"
    quote_text = "**Tweet:** Here's a quote from a great tweet!"
    quote_result = twitter_agent.post_quote_tweet(tweet_id_to_quote, quote_text)
    print("Quote Tweet Result:", quote_result)
except Exception as e:
    print("Error quoting tweet:", e)

# 8) (Optional) Post tweet with media
try:
    media_id = twitter_agent.upload_media_from_url("https://example.com/some_image.jpg")
    tweet_with_media_result = twitter_agent.post_with_media("Check out this image!", media_id)
    print("Tweet with Media Result:", tweet_with_media_result)
except Exception as e:
    print("Error posting tweet with media:", e)

```
---


### 📝 Usage Example Browser Agent

```python
import asyncio
from ambientagi.services.agent_service import AmbientAgentService

async def main():
    # 1) Initialize AmbientAgentService
    service = AmbientAgentService(api_key=os.getenv("OPENAI_API_KEY"))

    # 2) Create an agent via the orchestrator
    create_resp = service.create_agent(
        agent_name="BrowserAssistant",
        description="a browser assistant
        wallet_address="0x123456789ABCDEF"
    )
    print("Create Agent Response:", create_resp)

    agent_id = create_resp["agent_id"]

    # 3) Convert the existing agent record into a BrowserAgent
    browser_agent = service.create_browser_agent(agent_id)
    print(f"BrowserAgent '{browser_agent["agent_name"]}' initialized.")

    # 4) Run an async task (the agent's logic)
    #    e.g., "Go to Reddit, search for 'AI tools', return first post title."
    task = "Go to Reddit, search for 'AI tools', and return the first post title."
    result = await browser_agent.run_task(task)
    print("BrowserAgent Task Result:", result)

# Execute the async main
asyncio.run(main())

```
### Scheduler Integration
```python
from ambientagi.services.agent_service import AmbientAgentService

# Initialize the service
service = AmbientAgentService(api_key=os.getenv("OPENAI_API_KEY"))

# Define a custom task function
def custom_task():
    print("Running scheduled task for agent.")

# Schedule the task
service.schedule_agent(
    agent_id="1234",
    func=custom_task,
    interval=60  # Run every 60 seconds
)
```

### Scheduler with Browser Agent
```python
import asyncio
from ambientagi.services.agent_service import AmbientAgentService

def run_browser_task(agent_id: str, task: str):
    """
    Helper function that wraps the async browser task in a synchronous call.
    """
    service = AmbientAgentService(api_key=os.getenv("OPENAI_API_KEY"))
    browser_agent = service.create_browser_agent(agent_id)

    # Use asyncio.run(...) inside the function
    async def _async_run():
        result = await browser_agent.run_task(task)
        print("Scheduled Browser Task Result:", result)

    asyncio.run(_async_run())

def main():
    service = AmbientAgentService(api_key=os.getenv("OPENAI_API_KEY"))

    # Create an agent
    resp = service.create_agent(
        agent_name="BrowserAssistant",
        description="a browser assistant
        wallet_address="0x123456789ABCDEF"
    )
    agent_id = resp["agent"]["agent_id"]

    # The actual task logic
    task = "Go to Reddit, search for 'AI news', and return the first post title."

    # Schedule it to run every 60 seconds
    service.schedule_agent(
        agent_id=agent_id,
        func=lambda: run_browser_task(agent_id, task),
        interval=60
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

```

## 3. 🪙 Minting Coins on Solana or Ethereum

- **Solana**: Deploy SPL tokens tied to an agent usage .
- **Ethereum**: Deploy ERC-20 contracts with minting logic tied to agent usage.

```python
# Attach eth token to agent
import os
agent_id = response['agent_id']
attach_token = service.create_blockchain(agent_id)

creds_resp = attach_token.create_eth_token(
        privateKey=os.getenv("MY-PRIVATE-KEY"),
        token_name="aa45",
        symbol="app",
        buy_value_eth=0.001,
        image_path="mytoken.png"
)
```
---

# AmbientAgent Email Quickstart Guide

This guide walks you through creating and configuring an **Email Agent** within AmbientAgent, using SMTP (e.g., Gmail’s SMTP service) to send messages—including optional CC and BCC.

---

## 1. Prerequisites

- **AmbientAgent**: Make sure you have the AmbientAgent SDK/code installed or available.
- **SMTP Server**:
  - For Gmail, use `smtp.gmail.com` on port `587` with TLS.
  - You can also use other providers (e.g., `smtp.office365.com`, a corporate SMTP, etc.), but settings will differ.
- **Login Credentials**:
  - If using Gmail with **2FA**, you must create an **App Password** under [Google Account Security](https://myaccount.google.com/security).
  - Otherwise, if 2FA is disabled (not recommended), you can use your normal password.

---
## Generating a Gmail App Password

If your Google account has **2-Step Verification** (2FA) turned on, you **cannot** use your regular Gmail password for SMTP. Instead, you must create an **App Password**:

1. Go to [Google Account Security](https://myaccount.google.com/security).
2. Under **"Signing in to Google"**, select **"App Passwords"**.
3. If prompted, enter your password and 2FA code.
4. In **"Select app"**, choose **Mail** (or **Other** and give it a name, like "AmbientAgent").
5. In **"Select device"**, pick your device or “Other.”
6. Click **"Generate"**.
7. Copy the **16-character** password (spaces don’t matter).
8. Use that App Password in your code, for example:
```python
   password = "abcd efgh ijkl mnop"
```

sample code
```python
from ambientagi.services.agent_service import AmbientAgentService
import os

agent_service = AmbientAgentService(api_key=os.getenv("OPENAI_API_KEY"))
agent_id = "some-agent-id"

email_agent = agent_service.create_email_agent(
    agent_id=agent_id,
    username="xyz@gmail.com",
    password=os.getenv("GMAIL_PASSWORD"),
)

response = email_agent.send_email(
    to_address="xyz@gmail.com",
    subject="Hello from Gmail!",
    body="This is a test email sent from AmbientAgent.",
    cc=["xyz@gmail.com"],
    bcc=["xyz@gmal.com"],
)

print(response)
```

# Telegram Bot Quickstart Guide

## 1. Create a Bot with BotFather

1. Open Telegram and search for **BotFather** (the official bot that manages other bots).
2. Start a chat with BotFather and send the command:

/newbot

3. Follow the prompts: choose a **name** and a unique **username** (ending in `bot`, for example, `MyTestBerryBot`).
4. After creation, BotFather gives you an **HTTP API token**, such as:

**Keep this token private**—it grants full access to your bot.

## 2. Invite Your Bot to a Private Group or Channel

1. **Create** (or open) your private group/channel in Telegram.
2. Tap the **Group/Channel Info** (usually the title at the top).
3. Choose **Add Members** (or **Add Subscribers** for a channel).
4. Search for your bot’s **username** (e.g., `@MyTestBerryBot`) and **invite** it.
5. (Optional) **Promote** the bot to admin if it needs to post messages regularly or manage the group/channel.

## 3. Post a Message

- Once your bot is in the group/channel, type a quick message (e.g. "Hi from private group!").
- This ensures Telegram has a record of the bot seeing a message, so we can detect the chat ID.

## 4. Retrieve the Numeric Chat ID (Option A: Using getUpdates)

1. In your **web browser**, go to:
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates

Replace `<YOUR_BOT_TOKEN>` with the token from BotFather (e.g. `123456789:AAExample-BotToken`).

2. Look at the **JSON** response for a section like:
```json
{
  "update_id": 123456789,
  "message": {
    "message_id": 1,
    "chat": {
      "id": -100123456789,
      "title": "My Private Group",
      "type": "supergroup"
    },
    "text": "Hi from private group!"
  }
}
```
The chat.id (e.g., -100123456789) is what you need for the private group/channel.

### 5. Use the Chat ID in Your Code
Here’s a minimal Python example using requests:
```python

from ambientagi.services.agent_service import AmbientAgentService

# Step 1: Instantiate the main service
agent_service = AmbientAgentService()

# Step 2: Assume we have an existing AmbientAgent with this ID
agent_id = "your-telegram-enabled-agent-id"

# Step 3: Create the Telegram agent (provider)
bot_token = ""  # Example token7838344151:AAFf7ds7XmiKn2taxRAg
telegram_agent = agent_service.create_telegram_agent(agent_id, bot_token)

# Step 4: Send a Telegram message
response = telegram_agent.send_message(
    chat_id="-10024",  # or a numeric ID like 123456789
    text="Hello from Ambient on Telegram!",
)

print(response)
```


## 4. 🎨 3D/Video Representation for Agents

Generate and mint 3D models or videos for agents as NFTs. These assets can be stored on IPFS and linked to the agent’s blockchain activity.

---


## 📜 License
Broswer Agent was inspired from Browser Use and Browser WebUI

AmbientAGI is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
