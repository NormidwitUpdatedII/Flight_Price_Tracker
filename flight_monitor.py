"""
Turkish Airlines Flight Price Monitor
Monitors flight prices and sends notifications when prices drop below threshold
"""

import time
import json
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

class FlightPriceMonitor:
    def __init__(self, config_file='config.json'):
        """Initialize the flight price monitor"""
        self.config = self.load_config(config_file)
        self.price_history = self.load_price_history()
        
    def load_config(self, config_file):
        """Load configuration from JSON file or environment variables"""
        # Try environment variables first (for cloud deployment)
        if os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('EMAIL_ENABLED'):
            print("📡 Loading configuration from environment variables...")
            return {
                'price_threshold': float(os.getenv('PRICE_THRESHOLD', 2000)),
                'check_interval_minutes': int(os.getenv('CHECK_INTERVAL', 60)),
                'telegram': {
                    'enabled': bool(os.getenv('TELEGRAM_BOT_TOKEN')),
                    'bot_token': os.getenv('TELEGRAM_BOT_TOKEN', ''),
                    'chat_id': os.getenv('TELEGRAM_CHAT_ID', '')
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
            print("📄 Loading configuration from config.json...")
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"⚠️  Config file {config_file} not found and no environment variables set!")
            return {}
    
    def load_price_history(self):
        """Load price history from file"""
        history_file = 'price_history.json'
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_price_history(self):
        """Save price history to file"""
        with open('price_history.json', 'w', encoding='utf-8') as f:
            json.dump(self.price_history, f, indent=2, ensure_ascii=False)
    
    def setup_driver(self):
        """Setup Selenium WebDriver with headless Chrome"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    
    def extract_price(self, price_text):
        """Extract numeric price from text"""
        try:
            # Remove currency symbols and convert to float
            # Turkish Airlines uses format like "1.234,56 TL"
            price_clean = price_text.replace('TL', '').replace('₺', '').replace('.', '').replace(',', '.').strip()
            return float(price_clean)
        except:
            return None
    
    def check_flight_prices(self, url, date_label):
        """Check flight prices for a specific URL"""
        driver = None
        try:
            driver = self.setup_driver()
            print(f"\n🔍 Checking prices for {date_label}...")
            print(f"URL: {url}")
            
            driver.get(url)
            
            # Wait for page to load - Turkish Airlines uses dynamic loading
            time.sleep(10)  # Initial wait for page load
            
            # Try to find flight price elements
            # These selectors may need adjustment based on actual page structure
            flight_data = []
            
            try:
                # Wait for flight cards to appear
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='flight'], [class*='Flight'], [class*='card']"))
                )
                
                # Try multiple possible selectors for prices
                price_selectors = [
                    "[class*='price']",
                    "[class*='Price']",
                    "[class*='amount']",
                    "[class*='fare']",
                    "[class*='Fare']",
                    "span[class*='TL']",
                    "div[class*='TL']"
                ]
                
                prices_found = []
                for selector in price_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        for elem in elements:
                            text = elem.text.strip()
                            if 'TL' in text or '₺' in text:
                                price = self.extract_price(text)
                                if price and price > 0:
                                    prices_found.append({
                                        'price': price,
                                        'text': text,
                                        'selector': selector
                                    })
                    except:
                        continue
                
                if prices_found:
                    # Get unique prices
                    unique_prices = {}
                    for p in prices_found:
                        if p['price'] not in unique_prices:
                            unique_prices[p['price']] = p
                    
                    flight_data = list(unique_prices.values())
                    print(f"✅ Found {len(flight_data)} unique prices")
                    for flight in flight_data:
                        print(f"   💰 {flight['text']} ({flight['price']} TL)")
                else:
                    print("⚠️  No prices found with standard selectors")
                    # Save page source for debugging
                    with open(f'page_source_{date_label}.html', 'w', encoding='utf-8') as f:
                        f.write(driver.page_source)
                    print(f"   Saved page source to page_source_{date_label}.html for debugging")
                
            except TimeoutException:
                print("⚠️  Timeout waiting for flight elements")
            
            return flight_data
            
        except Exception as e:
            print(f"❌ Error checking prices: {str(e)}")
            return []
        finally:
            if driver:
                driver.quit()
    
    def send_email_notification(self, subject, message):
        """Send email notification"""
        try:
            email_config = self.config.get('email', {})
            if not email_config.get('enabled', False):
                return
            
            sender_email = email_config.get('sender_email')
            sender_password = email_config.get('sender_password')
            recipient_email = email_config.get('recipient_email')
            
            if not all([sender_email, sender_password, recipient_email]):
                print("⚠️  Email configuration incomplete")
                return
            
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'html'))
            
            # Use Gmail SMTP
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            
            print("✅ Email notification sent!")
            
        except Exception as e:
            print(f"❌ Error sending email: {str(e)}")
    
    def send_telegram_notification(self, message):
        """Send Telegram notification"""
        try:
            telegram_config = self.config.get('telegram', {})
            if not telegram_config.get('enabled', False):
                return
            
            bot_token = telegram_config.get('bot_token')
            chat_id = telegram_config.get('chat_id')
            
            if not all([bot_token, chat_id]):
                print("⚠️  Telegram configuration incomplete")
                return
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data)
            if response.status_code == 200:
                print("✅ Telegram notification sent!")
            else:
                print(f"⚠️  Telegram notification failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Error sending Telegram: {str(e)}")
    
    def check_and_notify(self):
        """Main monitoring loop"""
        print("=" * 60)
        print("🛫 Turkish Airlines Flight Price Monitor")
        print("=" * 60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Monitoring {len(self.config.get('flights', []))} flight dates")
        print(f"Price threshold: {self.config.get('price_threshold', 0)} TL")
        print("=" * 60)
        
        all_results = []
        
        for flight in self.config.get('flights', []):
            url = flight['url']
            date_label = flight['date']
            
            prices = self.check_flight_prices(url, date_label)
            
            if prices:
                # Store in history
                history_key = f"{date_label}_{datetime.now().strftime('%Y%m%d_%H%M')}"
                self.price_history[history_key] = {
                    'date': date_label,
                    'timestamp': datetime.now().isoformat(),
                    'prices': prices
                }
                
                # Check if any price is below threshold
                threshold = self.config.get('price_threshold', float('inf'))
                low_prices = [p for p in prices if p['price'] <= threshold]
                
                if low_prices:
                    all_results.append({
                        'date': date_label,
                        'low_prices': low_prices,
                        'alert': True
                    })
                else:
                    all_results.append({
                        'date': date_label,
                        'prices': prices,
                        'alert': False
                    })
            
            # Small delay between requests
            time.sleep(5)
        
        # Save history
        self.save_price_history()
        
        # Send notifications if needed
        alerts = [r for r in all_results if r.get('alert', False)]
        if alerts:
            self.send_notifications(alerts)
        
        print("\n" + "=" * 60)
        print(f"✅ Check completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
    
    def send_notifications(self, alerts):
        """Send notifications for price alerts"""
        subject = f"🎉 Flight Price Alert - {len(alerts)} dates below threshold!"
        
        message_html = "<h2>✈️ Turkish Airlines Price Alert</h2>"
        message_html += "<p>Great news! Prices have dropped below your threshold:</p>"
        
        message_text = "✈️ Turkish Airlines Price Alert\n\n"
        message_text += "Great news! Prices have dropped below your threshold:\n\n"
        
        for alert in alerts:
            date = alert['date']
            message_html += f"<h3>📅 {date}</h3><ul>"
            message_text += f"📅 {date}\n"
            
            for price_info in alert['low_prices']:
                message_html += f"<li>💰 {price_info['text']} - {price_info['price']} TL</li>"
                message_text += f"  💰 {price_info['text']} - {price_info['price']} TL\n"
            
            message_html += "</ul>"
            message_text += "\n"
        
        message_html += f"<p><small>Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small></p>"
        
        # Send via configured channels
        self.send_email_notification(subject, message_html)
        self.send_telegram_notification(message_text)
    
    def run_continuous(self):
        """Run monitoring continuously"""
        check_interval = self.config.get('check_interval_minutes', 60)
        
        while True:
            try:
                self.check_and_notify()
                print(f"\n⏰ Next check in {check_interval} minutes...")
                time.sleep(check_interval * 60)
            except KeyboardInterrupt:
                print("\n\n👋 Monitoring stopped by user")
                break
            except Exception as e:
                print(f"\n❌ Error in monitoring loop: {str(e)}")
                print(f"⏰ Retrying in 5 minutes...")
                time.sleep(300)

if __name__ == "__main__":
    monitor = FlightPriceMonitor()
    monitor.run_continuous()
