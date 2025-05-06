
# 🌟 AmbientAGI: Build Token-Rewarded AI Agents

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

## ⚡️ Why AmbientAGI?

- **Real-world agent orchestration**: Async schedulers, agent state, and custom prompts.
- **Multi-agent setups**: Plug-and-play modular agents (triage, trading, data fetchers, etc.).
- **Web UI**: Run agents visually using a Gradio-based interface with streaming feedback.
- **Social + On-Chain Output**: Agents that tweet, message, browse, or mint tokens—all from Python.

---

## 🧱 Core Features

| Feature | Description |
|--------|-------------|
| **Agent SDK** | `AmbientAgentService` for creating and managing agents via Python |
| **Async Web & Social Bots** | Telegram, Twitter, Browser, Email integration |
| **Scheduler Support** | Schedule agent tasks using APScheduler |
| **Token Minting** | Mint ETH/SOL tokens tied to agent usage |
| **NFT Media Hooks** | Attach 3D/video/NFT identity to agents |
| **WebUI** | Control and visualize browser agents from a Gradio dashboard |

---

## 💬 Agent Types

| Type | Description |
|------|-------------|
| **BrowserAgent** | Controls a headless browser via Playwright |
| **TwitterAgent** | Tweets, replies, uploads media |
| **TelegramAgent** | Posts in groups/channels, responds to mentions |
| **FirecrawlAgent** | Scrapes and crawls web content |
| **EmailAgent** | Sends messages via Gmail/SMTP |
| **BlockchainAgent** | Deploys tokens and interacts with Ethereum/Solana |

---

## 2. 🐍 Easy-to-Use Python Library

AmbientAGI provides a Python library for developers to create and manage AI agents effortlessly.

### 📦 Installation

Install the library via `pip`:

```bash
pip install ambientagi
```

### 📝 Usage Example DEFI Agent

```python
import os
import asyncio
from ambientagi.services.agent_service import AmbientAgentService

# Load API key from environment
API_KEY = os.getenv("OPENAI_API_KEY")

# 1. Initialize the AmbientAgentService
service = AmbientAgentService(api_key=API_KEY)

# 2. Create a database-tracked agent
create_resp = service.create_agent(
    agent_name="DeFiScanner",
    wallet_address="0x456DEF",
    description="A DeFi agent that monitors yield opportunities.",
)
print("Created agent:", create_resp)
agent_id = create_resp["agent_id"]

# 3. Update the agent with Twitter + specialty
update_resp = service.update_agent(
    agent_id=agent_id,
    updates={
        "twitter_handle": "defi_updates",
        "specialty": "Yield Monitoring",
    }
)
print("Updated agent:", update_resp)

# 4. Create a local OpenAI agent with DeFi logic
instructions = f"""
You are DeFiScanner, an assistant specialized in {update_resp.get('specialty', 'yield monitoring')}.
Your job is to answer questions about DeFi yield strategies, protocols like Aave, Compound, Curve, etc.
Be clear, concise, and helpful. When uncertain, suggest places the user can research.
"""
service.create_openai_agent("DeFiScanner", instructions)

# 5a. Synchronous chat with the agent
user_input = "What are the best stablecoin yield strategies right now?"
response = service.run_openai_agent("DeFiScanner", user_input, agent_id=agent_id)
print("\n[SYNC REPLY]:", response)

# 5b. Asynchronous version (optional)
async def chat_async():
    user_input = "Explain how Curve works in simple terms."
    result = await service.run_openai_agent_async("DeFiScanner", user_input, agent_id=agent_id)
    print("\n[ASYNC REPLY]:", result)

asyncio.run(chat_async())

```


### 📝 Usage Example Twitter Agent

```python
import os
from ambientagi.services.agent_service import AmbientAgentService

# 1) Initialize the core agent service
service = AmbientAgentService(api_key=os.getenv("OPENAI_API_KEY"))

# 2) Create a new generic agent (name → agent_name)
create_resp = service.create_agent(
    agent_name="TwitterAssistant",
    wallet_address="0xABCDEF1234",
    description="Agent that posts and replies on Twitter."
)
print("Create Agent Response:", create_resp)

agent_id = create_resp["agent_id"]

# 3) Attach a Twitter agent wrapper
twitter_agent = service.create_twitter_agent(agent_id)

# 4) Update Twitter credentials (replace with your actual tokens or env vars)
creds_resp = twitter_agent.update_twitter_credentials(
    twitter_handle="myTwitterBot",
    api_key=os.getenv("X_API_KEY"),
    api_secret=os.getenv("X_API_SECRET"),
    access_token=os.getenv("X_ACCESS_TOKEN"),
    access_secret=os.getenv("X_ACCESS_TOKEN_SECRET"),
)
print("Updated Twitter Credentials:", creds_resp)

# 5) Post a basic tweet
try:
    tweet_text = "Hello world from AmbientAGI Twitter agent!"
    tweet_result = twitter_agent.post_tweet(tweet_text)
    print("✅ Posted Tweet:", tweet_result)
except Exception as e:
    print("❌ Error posting tweet:", e)

# 6) (Optional) Reply to a tweet
try:
    tweet_id_to_reply = "1234567890123456789"
    reply_text = "This is a reply from our AmbientAGI agent!"
    reply_result = twitter_agent.reply_to_tweet(tweet_id_to_reply, reply_text)
    print("✅ Replied to Tweet:", reply_result)
except Exception as e:
    print("❌ Error replying to tweet:", e)

# 7) (Optional) Quote Tweet
try:
    tweet_id_to_quote = "9876543210987654321"
    quote_text = "**Tweet:** Here's a quote from a great tweet!"
    quote_result = twitter_agent.post_quote_tweet(tweet_id_to_quote, quote_text)
    print("✅ Quote Tweet Result:", quote_result)
except Exception as e:
    print("❌ Error quoting tweet:", e)

# 8) (Optional) Post tweet with media
try:
    media_id = twitter_agent.upload_media_from_url("https://example.com/some_image.jpg")
    tweet_with_media_result = twitter_agent.post_with_media(
        tweet_text="Check out this image!",
        media_url="https://example.com/some_image.jpg",
        media_type="image"
    )
    print("✅ Tweet with Media:", tweet_with_media_result)
except Exception as e:
    print("❌ Error posting tweet with media:", e)


```
---


### 📝 Usage Example Browser Agent

```python
import os
import asyncio
from ambientagi.services.agent_service import AmbientAgentService

async def main():
    # 1) Initialize AmbientAgentService with API key
    service = AmbientAgentService(api_key=os.getenv("OPENAI_API_KEY"))

    # 2) Create an agent (correct param: agent_name instead of prompt)
    create_resp = service.create_agent(
        agent_name="BrowserAssistant",
        wallet_address="0x123456789ABCDEF",
        description="An agent that uses a browser to gather information."
    )
    print("✅ Create Agent Response:", create_resp)

    # agent_id is inside create_resp["agent_id"]
    agent_id = create_resp["agent_id"]

    # 3) Create a BrowserAgent from this record
    browser_agent = service.create_browser_agent(agent_id)
    print(f"✅ BrowserAgent '{browser_agent.name}' initialized.")

    # 4) Run a browser task (headless)
    task = "Go to Reddit, search for 'AI tools', and return the first post title."
    result = await browser_agent.run_task(task)
    print("🧠 BrowserAgent Task Result:", result)

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())


```
### Scheduler Integration
```python
import os
import time
from ambientagi.services.agent_service import AmbientAgentService
from ambientagi.services.scheduler import AgentScheduler

# 1) Setup scheduler
scheduler = AgentScheduler()

# 2) Initialize AmbientAgentService with your API key and scheduler
service = AmbientAgentService(
    api_key=os.getenv("OPENAI_API_KEY"),
    scheduler=scheduler
)

# 3) Define a simple custom task
def custom_task():
    print("🕒 Running scheduled task for agent 1234 at", time.strftime("%X"))

# 4) Schedule it to run every 60 seconds
service.schedule_agent(
    agent_id="1234",
    func=custom_task,
    interval=1  # Run every 60 seconds
)

# 5) Keep the script running to allow the scheduler to trigger
print("✅ Scheduler started. Press Ctrl+C to stop.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("⏹️ Shutting down...")
    scheduler.shutdown()

```

### Scheduler with Browser Agent
```python
import os
import asyncio
import time
from ambientagi.services.agent_service import AmbientAgentService
from ambientagi.services.scheduler import AgentScheduler

# 🔧 Configurable browser settings
BROWSER_CONFIG = {
    "headless": True,  # or False
    "browser_class": "chromium",  # or "firefox", "webkit"
    "new_context_config": {
        "window_width": 1280,
        "window_height": 900,
    },
}

TASK_DESCRIPTION = "Go to Reddit, search for 'AI news', and return the first post title."

def run_browser_task(agent_id: str, task: str):
    """
    Synchronous wrapper that runs an async browser task.
    """
    service = AmbientAgentService(api_key=os.getenv("OPENAI_API_KEY"))
    browser_agent = service.create_browser_agent(
        agent_id=agent_id,
        browser_config=BROWSER_CONFIG,
    )

    async def _async_run():
        result = await browser_agent.run_task(task=task)
        print("🧠 Scheduled Browser Task Result:", result.final_result())

    asyncio.run(_async_run())

def main():
    scheduler = AgentScheduler()

    service = AmbientAgentService(
        api_key=os.getenv("OPENAI_API_KEY"),
        scheduler=scheduler
    )

    resp = service.create_agent(
        agent_name="BrowserSchedulerBot",
        wallet_address="0x123456789ABCDEF",
        description="Scheduled agent that searches Reddit for AI news.",
    )
    agent_id = resp["agent_id"]
    print("✅ Created agent:", agent_id)

    service.schedule_agent(
        agent_id=agent_id,
        func=lambda: run_browser_task(agent_id, TASK_DESCRIPTION),
        interval=60  # Every 60 seconds
    )

    print(f"📅 Browser agent {agent_id} scheduled every 60 seconds. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Shutting down...")
        scheduler.shutdown()

if __name__ == "__main__":
    main()



```

## 3. 🪙 Minting Coins on Solana or Ethereum

- **Solana**: Deploy SPL tokens tied to an agent usage .
- **Ethereum**: Deploy ERC-20 contracts with minting logic tied to agent usage.

```python
# Attach eth token to agent
import os
from ambientagi.services.agent_service import AmbientAgentService

# 1. Initialize AmbientAgentService with your OpenAI API key
service = AmbientAgentService(api_key=os.getenv("OPENAI_API_KEY"))

# 2. Create an agent to associate with the token
response = service.create_agent(
    agent_name="TokenMinter",
    wallet_address="0xDEADBEEF1234567890",
    description="Creates Ethereum tokens with metadata."
)
agent_id = response["agent_id"]
print("✅ Created agent:", agent_id)

# 3. Attach the blockchain service (for token creation)
attach_token = service.add_blockchain(agent_id)

# 4. Call create_eth_token with required metadata
creds_resp = attach_token.create_eth_token(
    privateKey=os.getenv("MY_PRIVATE_KEY"),         # ← set in your .env
    token_name="AA45 Token",
    symbol="AA45",
    buy_value_eth=0.001,                             # ETH value to buy
    image_path="mytoken.png",                        # optional local image file
    websiteUrl="https://mytoken.example.com",
    twitterUrl="https://twitter.com/mytokenbot",
    telegramUrl="https://t.me/mytokenchat"
)

# 5. Show the response from the backend
print("🪙 Token Creation Response:", creds_resp)

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

# Ensure the OPENAI_API_KEY is loaded from your environment
agent_service = AmbientAgentService(api_key=os.getenv("OPENAI_API_KEY"))
agent_id = "some-agent-id"

# Create the email agent
email_agent = agent_service.create_email_agent(
    agent_id=agent_id,
    username="xyz@gmail.com",
    password=os.getenv("GMAIL_PASSWORD"),  # Preferably use an App Password for Gmail
)

# Send the email
response = email_agent.send_email(
    to_address="xyz@gmail.com",
    subject="Hello from Gmail!",
    body="This is a test email sent from AmbientAgent.",
    cc=["xyz@gmail.com"],
    bcc=["xyz@gmail.com"],  # Corrected typo from "gmal.com"
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
---

## 📡 Supported Channels

- ✅ Telegram bots (with private group posting)
- ✅ Twitter/X integration
- ✅ Email (via SMTP)
- ✅ Headless browsing
- ✅ Custom HTTP tools, Firecrawl, function-calling

---

## 🖼️ 3D/NFT Media (Optional)

Agents can be associated with video/3D/NFT media (e.g. `.mp4`, `.glb`, `.gif`), linked to token contracts and stored on IPFS.

---

## 🔮 What Will You Build?

Create an autonomous job-hunter.
A DeFi monitoring swarm.
A market-meme whisperer.
A browser detective.
Or something weird and wonderful.

> The interface is agent. The frontier is ambient.

## 🧭 Next Steps

- 🔍 Check out example agents in `/examples/`
- 🎛️ Launch the WebUI with `WebUIAgent().launch()` for a live browser controller

---


## 📜 License
Broswer Agent was inspired from Browser Use and Browser WebUI

AmbientAGI is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
