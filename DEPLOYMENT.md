# Cloud Deployment Guide - 100% Free Options

This guide will help you deploy your flight price monitor to run 24/7 on free cloud services.

## 🎯 Best Option: Render.com

**Why Render?**
- ✅ Completely free tier
- ✅ 750 hours/month (enough for 24/7)
- ✅ Easy setup
- ✅ Supports Python + Selenium
- ✅ No credit card required

### Step-by-Step Render Deployment

#### 1. Prepare Your Code

First, create a GitHub repository:

```bash
cd flight-price-monitor
git init
git add .
git commit -m "Initial commit"
```

Create a GitHub account if you don't have one, then:
```bash
# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/flight-price-monitor.git
git push -u origin main
```

#### 2. Sign Up for Render

1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with GitHub (easiest)

#### 3. Create a New Web Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `flight-price-monitor`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && apt-get update && apt-get install -y chromium chromium-driver`
   - **Start Command**: `python flight_monitor.py`
   - **Instance Type**: `Free`

#### 4. Add Environment Variables

Instead of using `config.json`, add these environment variables in Render:

```
PRICE_THRESHOLD=2000
CHECK_INTERVAL=60
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

For email (optional):
```
EMAIL_ENABLED=true
EMAIL_SENDER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_RECIPIENT=your-email@gmail.com
```

#### 5. Deploy!

Click "Create Web Service" and Render will:
- Clone your repository
- Install dependencies
- Start your monitor
- Keep it running 24/7!

---

## 🔄 Alternative: Railway.app

**Free Tier**: 500 hours/month + $5 credit

### Railway Setup

1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Add environment variables (same as Render)
6. Deploy!

**Note**: Railway requires credit card for verification, but won't charge you on free tier.

---

## 🐍 Alternative: PythonAnywhere

**Free Tier**: Limited to scheduled tasks (not continuous)

### PythonAnywhere Setup

1. Go to https://www.pythonanywhere.com
2. Create free account
3. Upload your files via "Files" tab
4. Open a Bash console:
   ```bash
   pip install --user -r requirements.txt
   ```
5. Create a scheduled task:
   - Go to "Tasks" tab
   - Set to run `python flight_monitor.py` every hour

**Limitation**: Free tier only allows scheduled tasks, not continuous running.

---

## 📱 Setting Up Telegram (Recommended for Cloud)

Telegram is the best option for cloud deployment because:
- ✅ No email server configuration needed
- ✅ Instant notifications
- ✅ Works from anywhere
- ✅ 100% free

### Telegram Setup Steps

1. **Create a Bot**:
   - Open Telegram app
   - Search for `@BotFather`
   - Send: `/newbot`
   - Choose a name: "Flight Price Monitor"
   - Choose a username: "YourName_FlightBot"
   - **Copy the token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

2. **Get Your Chat ID**:
   - Search for `@userinfobot` on Telegram
   - Click "Start"
   - It will send you your chat ID (a number)

3. **Activate Your Bot**:
   - Search for your bot (the username you created)
   - Click "Start"

4. **Add to Environment Variables**:
   ```
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   TELEGRAM_CHAT_ID=123456789
   ```

---

## 🔧 Modified Code for Environment Variables

If deploying to cloud, update `flight_monitor.py` to read from environment variables:

```python
import os

# In load_config method, add:
def load_config(self, config_file):
    # Try environment variables first (for cloud deployment)
    if os.getenv('TELEGRAM_BOT_TOKEN'):
        return {
            'price_threshold': float(os.getenv('PRICE_THRESHOLD', 2000)),
            'check_interval_minutes': int(os.getenv('CHECK_INTERVAL', 60)),
            'telegram': {
                'enabled': True,
                'bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),
                'chat_id': os.getenv('TELEGRAM_CHAT_ID')
            },
            'email': {
                'enabled': os.getenv('EMAIL_ENABLED', 'false').lower() == 'true',
                'sender_email': os.getenv('EMAIL_SENDER', ''),
                'sender_password': os.getenv('EMAIL_PASSWORD', ''),
                'recipient_email': os.getenv('EMAIL_RECIPIENT', '')
            },
            'flights': [
                {'date': '04.02.2026', 'url': 'https://www.turkishairlines.com/tr-tr/ucak-bileti/rezervasyon/ic-hat-musaitlik/?cId=a7116f55-4ba3-4d67-93d5-5c7a024397a1'},
                {'date': '05.02.2026', 'url': 'https://www.turkishairlines.com/tr-tr/ucak-bileti/rezervasyon/ic-hat-musaitlik/?cId=a7116f55-4ba3-4d67-93d5-5c7a024397a1'},
                {'date': '06.02.2026', 'url': 'https://www.turkishairlines.com/tr-tr/ucak-bileti/rezervasyon/ic-hat-musaitlik/?cId=a7116f55-4ba3-4d67-93d5-5c7a024397a1'},
                {'date': '07.02.2026', 'url': 'https://www.turkishairlines.com/tr-tr/ucak-bileti/rezervasyon/ic-hat-musaitlik/?cId=a7116f55-4ba3-4d67-93d5-5c7a024397a1'}
            ]
        }
    
    # Otherwise load from config.json
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}
```

---

## 📊 Monitoring Your Cloud Service

### Render
- View logs in real-time from the dashboard
- See when prices are checked
- Get notifications when alerts are sent

### Railway
- Check logs in the deployment dashboard
- Monitor resource usage
- View deployment history

---

## ⚠️ Important Notes

1. **Free Tier Limits**:
   - Render: 750 hours/month (enough for 24/7)
   - Railway: 500 hours/month (~20 days)
   - PythonAnywhere: Scheduled tasks only

2. **Chrome/Chromium**:
   - Cloud services need special setup for Chrome
   - Use the build command provided above

3. **Check Frequency**:
   - Don't check too often (respect Turkish Airlines)
   - 60 minutes is recommended
   - More frequent = more resource usage

4. **Debugging**:
   - Check logs if not working
   - Test locally first with `test_scraper.py`
   - Verify Telegram bot is working

---

## 🎉 Success Checklist

- [ ] Code pushed to GitHub
- [ ] Render/Railway account created
- [ ] Repository connected
- [ ] Environment variables added
- [ ] Telegram bot created and started
- [ ] Service deployed
- [ ] Logs show successful price checks
- [ ] Test notification received

---

## 🆘 Troubleshooting

**Service won't start:**
- Check logs for errors
- Verify all environment variables are set
- Make sure requirements.txt is correct

**No notifications:**
- Test Telegram bot locally first
- Verify you clicked "Start" on your bot
- Check bot token and chat ID are correct

**Can't find prices:**
- Turkish Airlines may have bot detection
- Try increasing wait time in code
- Check if page structure changed

---

## 💡 Pro Tips

1. **Test Locally First**: Run `python test_scraper.py` before deploying
2. **Use Telegram**: Easier than email for cloud deployment
3. **Monitor Logs**: Check regularly to ensure it's working
4. **Adjust Threshold**: Start higher, then lower it as you see prices
5. **Be Patient**: It may take a few checks to find good prices

Good luck with your flight search! 🛫
