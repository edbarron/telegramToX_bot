### 📄 `README.md` (para `pulsobot`)

```markdown
# Telegram to X (Twitter) Bot

A Python bot that listens to a specific Telegram channel and automatically reposts messages (text, photos, or videos) to an X (Twitter) account using OAuth.

## Features

- **Text & Media Support:** Reposts text, photos, and videos from Telegram.
- **Rate Limit Management:** Tracks daily API usage to avoid hitting Twitter's rate limits.
- **OAuth Authentication:** Uses Twitter API v2 with OAuth 1.0a for secure posting.
- **Error Handling:** Handles common errors like rate limits, forbidden access, and missing media.
- **Local Storage:** Keeps a JSON counter file to track daily request usage.

## Tech Stack

- **Python 3.10+**
- **python-telegram-bot** (Telegram API)
- **tweepy** (Twitter API)
- **python-dotenv** (Environment variables)
- **Logging** (Built-in Python module)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/pulsobot.git
   cd pulsobot
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory and add your credentials:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   TELEGRAM_CHANNEL_ID=-1001234567890
   TWITTER_BEARER_TOKEN=your_twitter_bearer_token
   TWITTER_API_KEY=your_twitter_api_key
   TWITTER_API_SECRET=your_twitter_api_secret
   TWITTER_ACCESS_TOKEN=your_twitter_access_token
   TWITTER_ACCESS_SECRET=your_twitter_access_secret
   ```

   > **Note:** The bot also accepts `TWITTER_CONSUMER_KEY` and `TWITTER_CONSUMER_SECRET` as aliases for the API key and secret.

5. Run the bot:
   ```bash
   python telegram_to_x_bot.py
   ```

## Usage

1. Add the bot to your Telegram channel as an administrator.
2. Send any message (text, photo, or video) to the channel.
3. The bot will automatically repost it to your X (Twitter) account.

## Configuration

The bot reads the following environment variables:

| Variable | Description |
| :--- | :--- |
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token (from BotFather). |
| `TELEGRAM_CHANNEL_ID` | The ID of the Telegram channel to monitor (can be negative). |
| `TWITTER_BEARER_TOKEN` | Your Twitter API bearer token. |
| `TWITTER_API_KEY` | Your Twitter API key (or consumer key). |
| `TWITTER_API_SECRET` | Your Twitter API secret (or consumer secret). |
| `TWITTER_ACCESS_TOKEN` | Your Twitter access token. |
| `TWITTER_ACCESS_SECRET` | Your Twitter access token secret. |

## How It Works

1. **Telegram Listener:** The bot uses `python-telegram-bot` to listen for new messages in the specified channel.
2. **Media Handling:** If the message contains a photo or video, it downloads the media temporarily.
3. **Twitter Posting:** It uses `tweepy` to upload media (if any) and post the message as a tweet.
4. **Rate Limit Control:** It tracks the number of requests made in the last 24 hours and stops if the limit is reached.

## File Structure

```text
pulsobot/
│
├── telegram_to_x_bot.py   # Main bot logic
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not tracked by git)
├── .gitignore             # Files to ignore
├── contador.json          # Request counter (auto-generated)
└── README.md
```

## License

This project is open-source. Modify and expand it as needed.

---

**Connect with me:** [PxlCode Studio](https://pxlcode.xyz) | [GitHub](https://github.com/edbarron)
```