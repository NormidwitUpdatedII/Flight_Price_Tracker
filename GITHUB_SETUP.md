# GitHub Setup Guide

## Quick Steps to Push Your Code to GitHub

### Step 1: Create GitHub Repository (Web Browser)

1. **Go to GitHub**: https://github.com/new
2. **Log in** if you haven't already
3. **Fill in the details**:
   - Repository name: `flight-price-monitor`
   - Description: `Turkish Airlines flight price monitoring with notifications`
   - Visibility: **Public** (required for free cloud hosting)
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
4. **Click "Create repository"**

### Step 2: Get Your Repository URL

After creating, GitHub will show you a URL like:
```
https://github.com/YOUR_USERNAME/flight-price-monitor.git
```

**Copy this URL!**

### Step 3: Push Your Code (Run in Terminal)

Replace `YOUR_USERNAME` with your actual GitHub username:

```bash
cd C:\Users\asus\.gemini\antigravity\scratch\flight-price-monitor

git remote add origin https://github.com/YOUR_USERNAME/flight-price-monitor.git

git branch -M main

git push -u origin main
```

You'll be asked for your GitHub credentials:
- **Username**: Your GitHub username
- **Password**: Use a **Personal Access Token** (not your password!)

### Step 4: Create Personal Access Token (if needed)

If you don't have a token:

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name: `Flight Monitor`
4. Select scopes: Check **repo** (all sub-items)
5. Click "Generate token"
6. **COPY THE TOKEN** (you won't see it again!)
7. Use this token as your password when pushing

### Alternative: Use GitHub Desktop

If you prefer a GUI:

1. Download GitHub Desktop: https://desktop.github.com/
2. Install and log in
3. File → Add Local Repository
4. Select: `C:\Users\asus\.gemini\antigravity\scratch\flight-price-monitor`
5. Click "Publish repository"

---

## ✅ Verification

After pushing, go to:
```
https://github.com/YOUR_USERNAME/flight-price-monitor
```

You should see all your files!

---

## Next: Deploy to Cloud

Once your code is on GitHub, we can deploy to Render.com (see DEPLOYMENT.md)
