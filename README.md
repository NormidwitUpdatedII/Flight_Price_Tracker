# Turkish Airlines Flight Price Monitor 🛫

Monitor Turkish Airlines flight prices and get notified when prices drop below your threshold!

## Features ✨

- 🔄 **Continuous Monitoring**: Checks flight prices at regular intervals
- 💰 **Price Threshold Alerts**: Get notified when prices drop below your target
- 📧 **Email Notifications**: Receive alerts via Gmail
- 📱 **Telegram Notifications**: Get instant messages on Telegram
- 📊 **Price History**: Tracks price changes over time
- ☁️ **Cloud Deployment**: Run 24/7 on free cloud services
- 🆓 **100% Free**: Uses only free services

## Quick Start 🚀

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

You'll also need Chrome/Chromium browser installed for Selenium.

### 2. Configure Your Settings

Edit `config.json`:

```json
{
  "price_threshold": 2000,  // Set your maximum price in TL
  "check_interval_minutes": 60,  // How often to check (in minutes)
  "flights": [
    // Your flight dates are already configured!
  ],
  "email": {
    "enabled": true,  // Set to true to enable email
    "sender_email": "your-email@gmail.com",
    "sender_password": "your-app-password",  // See setup below
    "recipient_email": "your-email@gmail.com"
  },
  "telegram": {
    "enabled": true,  // Set to true to enable Telegram
    "bot_token": "YOUR_BOT_TOKEN",  // See setup below
    "chat_id": "YOUR_CHAT_ID"
  }
}
```

### 3. Run Locally (Testing)

```bash
python flight_monitor.py
```

## Notification Setup 📬

### Option 1: Email (Gmail)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Create an App Password**:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Copy the generated password
3. **Update config.json**:
   ```json
   "email": {
     "enabled": true,
     "sender_email": "youremail@gmail.com",
     "sender_password": "your-16-char-app-password",
     "recipient_email": "youremail@gmail.com"
   }
   ```

### Option 2: Telegram (Recommended - Easier!)

1. **Create a Telegram Bot**:
   - Open Telegram and search for `@BotFather`
   - Send `/newbot` and follow instructions
   - Copy the bot token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

2. **Get Your Chat ID**:
   - Search for `@userinfobot` on Telegram
   - Start a chat and it will send you your chat ID

3. **Update config.json**:
   ```json
   "telegram": {
     "enabled": true,
     "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
     "chat_id": "your-chat-id"
   }
   ```

4. **Start your bot**:
   - Find your bot on Telegram (the name you gave it)
   - Click "Start" to activate it

## Cloud Deployment (24/7 Monitoring) ☁️

To keep the monitor running even when your laptop is closed, deploy to a free cloud service:

### Option A: Render.com (Recommended)

1. **Create account** at https://render.com (free)
2. **Create a new Web Service**
3. **Connect your GitHub** (or upload files)
4. **Configure**:
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python flight_monitor.py`
5. **Add environment variables** (instead of config.json):
   - `PRICE_THRESHOLD=2000`
   - `CHECK_INTERVAL=60`
   - `TELEGRAM_BOT_TOKEN=your-token`
   - `TELEGRAM_CHAT_ID=your-chat-id`

### Option B: PythonAnywhere (Alternative)

1. **Create account** at https://www.pythonanywhere.com (free)
2. **Upload files** to your account
3. **Install dependencies**: `pip install -r requirements.txt`
4. **Create a scheduled task** to run `python flight_monitor.py`

### Option C: Railway.app

1. **Create account** at https://railway.app (free tier)
2. **Deploy from GitHub** or upload files
3. **Configure** build and start commands
4. **Add environment variables**

## How It Works 🔧

1. **Scraping**: Uses Selenium to load Turkish Airlines pages (handles JavaScript)
2. **Price Extraction**: Finds all prices on the page
3. **Comparison**: Checks if any price is below your threshold
4. **Notification**: Sends alerts via email/Telegram when prices drop
5. **History**: Saves all price checks to `price_history.json`
6. **Loop**: Waits for the configured interval and repeats

## Customization ⚙️

### Add More Dates

Edit `config.json` and add more flight entries:

```json
"flights": [
  {
    "date": "03.02.2026",
    "url": "your-turkish-airlines-url"
  }
]
```

### Change Check Frequency

```json
"check_interval_minutes": 30  // Check every 30 minutes
```

### Adjust Price Threshold

```json
"price_threshold": 1500  // Alert when price ≤ 1500 TL
```

## Troubleshooting 🔍

### "No prices found"
- The script saves `page_source_[date].html` for debugging
- Turkish Airlines may have changed their page structure
- Check if the page requires login or has bot protection

### Chrome/Selenium Issues
- Make sure Chrome is installed
- Update Chrome to the latest version
- Selenium will auto-download the correct ChromeDriver

### Notifications Not Working
- **Email**: Check app password is correct (not your regular password)
- **Telegram**: Make sure you clicked "Start" on your bot
- Check the console output for error messages

## Price History 📊

All price checks are saved to `price_history.json`:

```json
{
  "04.02.2026_20260115_1930": {
    "date": "04.02.2026",
    "timestamp": "2026-01-15T19:30:00",
    "prices": [
      {"price": 1850.50, "text": "1.850,50 TL"}
    ]
  }
}
```

## Important Notes ⚠️

- **Free SMS is not available** - SMS services require payment. Use Telegram instead (it's free and instant!)
- **Respect Turkish Airlines**: Don't set check interval too low (minimum 30 minutes recommended)
- **Cloud Free Tiers**: Have limitations (hours/month). Monitor your usage.
- **Bot Detection**: If Turkish Airlines blocks automated access, you may need to add delays or use proxies

## Support 💬

If you encounter issues:
1. Check the console output for error messages
2. Review `page_source_[date].html` files
3. Verify your notification settings
4. Test locally before deploying to cloud

## Route Information 🗺️

**Your Flight**: Diyarbakır (DIY) → Istanbul Airport (IST)  
**Dates**: February 3-7, 2026  
**Current Threshold**: 2000 TL

Good luck finding a great price! ✈️
