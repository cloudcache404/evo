<div align="center">

# 🤖 EvoBot

### Your open-source AI companion for Telegram.

A fast, customizable and student-friendly AI Telegram bot built with Python.

<br>

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://telegram.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Beta-orange?style=for-the-badge)](#-project-status)

<br>

**Simple. Fast. Open.**

[Features](#-features) •
[Installation](#-installation) •
[Configuration](#-configuration) •
[Usage](#-usage) •
[Contributing](#-contributing)

</div>

---

## ✨ What is EvoBot?

**EvoBot** is an open-source AI-powered Telegram bot designed to make AI
accessible directly from Telegram.

It provides a simple conversational interface with support for multiple
AI models, customizable responses and a student-friendly experience.

Whether you're experimenting with AI, building your own Telegram bot,
or simply looking for a ready-to-use starting point, EvoBot is built to
be easy to understand and extend.

> 🚧 EvoBot is currently in **Beta**. Features and APIs may change.

---

## 🌟 Features

- 🤖 AI-powered conversations
- 🧠 Multiple AI model support
- 💬 English + Hinglish friendly responses
- ⚡ Lightweight Telegram architecture
- 🎨 Clean and aesthetic interface
- 🔄 Model selection
- 🛠️ Customizable configuration
- 🆘 Built-in support/reporting system
- 📊 Optional bot telemetry
- 🖼️ Custom bot branding
- 🔐 Configuration designed with security in mind
- 🧩 Easy to extend
- 🌍 Open source

---

## 🧠 AI Models

EvoBot is designed to support multiple AI providers/models.

The exact models available depend on your configured AI backend.

Example:

```text
┌──────────────────────────────┐
│        🧠 Choose Model       │
├──────────────────────────────┤
│ ⚡ Fast Model                │
│ 🧠 General Model             │
│ 💻 Coding Model              │
│ 🎓 Student Model             │
│ 🔬 Advanced Model            │
└──────────────────────────────┘
Note: Model availability depends on the API/provider you configure.
📱 Experience
/start
The /start command introduces EvoBot and provides access to available bot options.
Example:
🤖 Welcome to EvoBot!

Your open-source AI companion.

Choose an option below to get started.
🛠️ Tech Stack
Technology
Purpose
🐍 Python
Core bot
📱 Telegram Bot API
Telegram integration
🧠 AI APIs
AI responses
🗃️ JSON / Database
Optional storage
🌐 HTTP APIs
External services
🚀 Installation
1. Clone the repository
git clone https://github.com/YOUR_USERNAME/EvoBot.git
cd EvoBot
2. Create a virtual environment
Windows
python -m venv venv
venv\Scripts\activate
Linux / macOS
python3 -m venv venv
source venv/bin/activate
3. Install dependencies
pip install -r requirements.txt
🔐 Configuration
Create a .env file based on .env.example.
Example:
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
AI_API_KEY=your_ai_api_key
ADMIN_ID=your_telegram_user_id
⚠️ NEVER publish your real credentials.
Do not commit:
.env
bot tokens
API keys
private credentials
admin passwords
database passwords
Use environment variables instead.
▶️ Running EvoBot
Start the bot with:
python bot.py
If everything is configured correctly, EvoBot should start polling Telegram for updates.
💬 Commands
Command
Description
/start
Start EvoBot
/help
Show help
/support
Contact/report an issue
/models
View available models
Commands may change as EvoBot evolves.
🧩 Customization
EvoBot is designed to be modified.
You can customize:
Bot name
Logo
Welcome message
AI models
AI providers
Commands
Inline keyboards
Response formatting
Admin system
Support system
Telemetry
Hosting configuration
🖼️ Screenshots
�

Start Screen
�
￼
AI Chat
�
￼
Model Selection
�
￼
�

🏗️ Project Structure
EvoBot/
│
├── bot.py
├── requirements.txt
├── .env.example
├── README.md
├── LICENSE
│
├── assets/
│   └── logo.png
│
├── handlers/
├── services/
├── utils/
│
└── docs/
🌐 Hosting
EvoBot can run on any hosting environment that supports Python and allows long-running processes.
Possible options include:
VPS
Python hosting platforms
Self-hosted servers
Local computers
Development environments
Make sure your hosting provider supports the Python version and dependencies required by the project.
🛡️ Security
Security matters, especially for Telegram bots.
Never expose:
TELEGRAM_BOT_TOKEN
AI_API_KEY
ADMIN_ID
DATABASE CREDENTIALS
If you accidentally publish a bot token:
Immediately revoke/rotate it.
Remove it from the repository.
Remove it from Git history if necessary.
Replace the exposed credential.
See SECURITY.md.
🐛 Reporting Bugs
Found something broken?
Please create a GitHub issue and include:
What happened
What you expected
Steps to reproduce
Python version
Hosting environment
Relevant logs
Never include API keys or bot tokens in an issue.
💡 Feature Requests
Have an idea?
Open a feature request and explain:
What you want
Why it would be useful
How you think it could work
Creative ideas are welcome. 🚀
🤝 Contributing
Contributions are welcome!
You can contribute by:
Fixing bugs
Improving documentation
Adding features
Improving performance
Improving UI/UX
Adding tests
Reporting issues
Reviewing pull requests
Read CONTRIBUTING.md before submitting a PR.
📜 License
EvoBot is released under the MIT License.
See LICENSE for details.
⭐ Support the Project
If EvoBot is useful to you:
⭐ Star the repository
🐛 Report bugs
💡 Suggest features
🔧 Submit pull requests
📢 Share it with other developers
Every contribution helps EvoBot evolve.
�

Built with ❤️ by the EvoBot community.
EvoBot — Open. Evolving. Yours.
�
```
