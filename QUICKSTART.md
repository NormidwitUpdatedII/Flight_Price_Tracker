# Quick Start Guide 🚀

## For the Impatient 😊

### 1️⃣ Set Up Telegram (5 minutes)

**Why Telegram?** It's FREE, instant, and works perfectly with cloud hosting!

1. Open Telegram on your phone
2. Search for `@BotFather`
3. Send: `/newbot`
4. Name it: `My Flight Monitor`
5. Username: `YourName_FlightBot` (must end with 'bot')
6. **COPY THE TOKEN** (long string with numbers and letters)
7. Search for `@userinfobot` and start it
8. **COPY YOUR CHAT ID** (a number)
9. Search for your bot and click **START**

### 2️⃣ Test Locally (Optional but Recommended)

```bash
# Install dependencies
pip install -r requirements.txt

# Edit config.json - add your Telegram info:
# "telegram": {
#   "enabled": true,
#   "bot_token": "paste-your-token-here",
#   "chat_id": "paste-your-chat-id-here"
# }

# Test the scraper
python test_scraper.py

# If test works, run the monitor
python flight_monitor.py
```

### 3️⃣ Deploy to Cloud (Free Forever!)

**Option A: Render.com** (Recommended - Easiest)

1. Go to https://render.com
2. Sign up with GitHub (free)
3. Create new repository on GitHub with your code
4. In Render: New → Web Service → Connect your repo
5. Settings:
   - Build: `pip install -r requirements.txt`
   - Start: `python flight_monitor.py`
6. Add Environment Variables:
   ```
   TELEGRAM_BOT_TOKEN = your-bot-token
   TELEGRAM_CHAT_ID = your-chat-id
   PRICE_THRESHOLD = 2000
   CHECK_INTERVAL = 60
   ```
7. Click "Create Web Service"
8. Done! It will run 24/7 🎉

**Option B: Railway.app**

1. Go to https://railway.app
2. Sign up with GitHub
3. New Project → Deploy from GitHub
4. Add same environment variables
5. Deploy!

---

## What Happens Next?

- ✅ Monitor checks prices every 60 minutes
- ✅ When price drops below 2000 TL, you get a Telegram message
- ✅ Runs 24/7 even when your laptop is off
- ✅ Completely FREE!

---

## Customize Your Settings

Edit `config.json` or set environment variables:

```json
{
  "price_threshold": 1500,  // Lower = fewer alerts, better deals
  "check_interval_minutes": 30,  // How often to check (min 30)
}
```

---

## Troubleshooting

**Not getting notifications?**
- Did you click "Start" on your Telegram bot?
- Is the bot token correct?
- Check the logs in Render/Railway

**No prices found?**
- Turkish Airlines may have bot detection
- The page structure might have changed
- Check `test_screenshot.png` to see what the bot sees

**Service stopped?**
- Free tiers have limits (750 hours/month on Render)
- Check your cloud service dashboard

---

## Important Notes

⚠️ **SMS is NOT free** - That's why we use Telegram instead!

⚠️ **Be respectful** - Don't check more than once every 30 minutes

⚠️ **Test first** - Run `test_scraper.py` before deploying

✅ **It's all FREE** - Render, Telegram, everything!

---

## Your Flight Details

- **Route**: Diyarbakır (DIY) → Istanbul (IST)
- **Dates**: Feb 4, 5, 6, 7, 2026
- **Threshold**: 2000 TL
- **Check Frequency**: Every 60 minutes

---

## Need Help?

1. Check `README.md` for detailed instructions
2. Check `DEPLOYMENT.md` for cloud deployment guide
3. Run `test_scraper.py` to debug issues
4. Look at the logs in your cloud service

---

## Pro Tips 💡

1. **Start with higher threshold** (2500 TL) to test notifications work
2. **Lower it gradually** as you see what prices look like
3. **Check logs regularly** to make sure it's working
4. **Be patient** - good deals take time!

Good luck finding a great price! ✈️🎉
