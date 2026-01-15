"""
Turkish Airlines Flight Price Monitor - Using Search Flow
Monitors flight prices by navigating the actual booking flow
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
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import re

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
                'origin': os.getenv('ORIGIN', 'DIY'),  # Diyarbakır
                'destination': os.getenv('DESTINATION', 'IST'),  # Istanbul
                'dates': os.getenv('DATES', '04.02.2026,05.02.2026,06.02.2026,07.02.2026').split(','),
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
                }
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
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    
    def extract_price(self, price_text):
        """Extract numeric price from text"""
        try:
            # Remove currency symbols and convert to float
            # Turkish Airlines uses format like "1.234,56 TL"
            price_clean = price_text.replace('TL', '').replace('₺', '').replace('.', '').replace(',', '.').strip()
            # Extract just the number
            match = re.search(r'[\d.]+', price_clean)
            if match:
                return float(match.group())
            return None
        except:
            return None
    
    def search_flights(self, driver, origin, destination, date):
        """Search for flights using Turkish Airlines website"""
        try:
            print(f"\n🔍 Searching flights: {origin} → {destination} on {date}")
            
            # Go to Turkish Airlines homepage
            driver.get("https://www.turkishairlines.com/tr-tr/")
            time.sleep(5)
            
            # Wait for page to load
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Handle any cookie consent popups
            try:
                cookie_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Kabul') or contains(text(), 'Accept')]")
                for btn in cookie_buttons:
                    if btn.is_displayed():
                        btn.click()
                        time.sleep(1)
                        break
            except:
                pass
            
            # Look for the flight search form
            # Try to find and fill origin field
            origin_selectors = [
                "input[placeholder*='Nereden']",
                "input[aria-label*='Nereden']",
                "#origin",
                "input[name*='origin']",
                "[data-testid*='origin']"
            ]
            
            origin_filled = False
            for selector in origin_selectors:
                try:
                    origin_field = driver.find_element(By.CSS_SELECTOR, selector)
                    origin_field.clear()
                    origin_field.send_keys(origin)
                    time.sleep(2)
                    origin_field.send_keys(Keys.ENTER)
                    origin_filled = True
                    print(f"   ✓ Origin set: {origin}")
                    break
                except:
                    continue
            
            if not origin_filled:
                print("   ⚠️ Could not find origin field")
                # Save screenshot for debugging
                driver.save_screenshot(f"debug_origin_{date.replace('.', '-')}.png")
            
            time.sleep(2)
            
            # Fill destination field
            dest_selectors = [
                "input[placeholder*='Nereye']",
                "input[aria-label*='Nereye']",
                "#destination",
                "input[name*='destination']",
                "[data-testid*='destination']"
            ]
            
            dest_filled = False
            for selector in dest_selectors:
                try:
                    dest_field = driver.find_element(By.CSS_SELECTOR, selector)
                    dest_field.clear()
                    dest_field.send_keys(destination)
                    time.sleep(2)
                    dest_field.send_keys(Keys.ENTER)
                    dest_filled = True
                    print(f"   ✓ Destination set: {destination}")
                    break
                except:
                    continue
            
            if not dest_filled:
                print("   ⚠️ Could not find destination field")
            
            time.sleep(2)
            
            # Note: Date selection in Turkish Airlines is complex
            # For now, we'll try to get current prices and extract date info
            
            # Click search button
            search_selectors = [
                "button[type='submit']",
                "button[class*='search']",
                "button[class*='Search']",
                "#searchButton",
                "button[data-testid*='search']"
            ]
            
            search_clicked = False
            for selector in search_selectors:
                try:
                    search_btn = driver.find_element(By.CSS_SELECTOR, selector)
                    if search_btn.is_displayed():
                        search_btn.click()
                        search_clicked = True
                        print("   ✓ Search button clicked")
                        break
                except:
                    continue
            
            if search_clicked:
                # Wait for results to load
                print("   ⏳ Waiting for results...")
                time.sleep(15)
                return True
            else:
                print("   ⚠️ Could not find/click search button")
                driver.save_screenshot(f"debug_search_{date.replace('.', '-')}.png")
                return False
                
        except Exception as e:
            print(f"   ❌ Error during search: {str(e)}")
            return False
    
    def extract_prices_from_page(self, driver, date):
        """Extract all prices from the current page"""
        prices = []
        
        try:
            # Get all text from page
            body_text = driver.find_element(By.TAG_NAME, "body").text
            
            # Find all TL amounts
            price_pattern = r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*(?:TL|₺)'
            matches = re.findall(price_pattern, body_text)
            
            for match in matches:
                price = self.extract_price(match + " TL")
                if price and price > 100 and price < 50000:  # Reasonable flight price range
                    prices.append({
                        'price': price,
                        'text': f"{match} TL",
                        'date': date
                    })
            
            # Remove duplicates
            unique_prices = {}
            for p in prices:
                if p['price'] not in unique_prices:
                    unique_prices[p['price']] = p
            
            prices = list(unique_prices.values())
            
            if prices:
                print(f"   ✅ Found {len(prices)} unique prices:")
                for p in sorted(prices, key=lambda x: x['price'])[:5]:  # Show lowest 5
                    print(f"      💰 {p['text']}")
            else:
                print("   ⚠️ No prices found on page")
                # Save page for debugging
                driver.save_screenshot(f"debug_prices_{date.replace('.', '-')}.png")
                with open(f"debug_page_{date.replace('.', '-')}.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                    
        except Exception as e:
            print(f"   ❌ Error extracting prices: {str(e)}")
        
        return prices
    
    def check_flight_prices(self, date):
        """Check flight prices for a specific date"""
        driver = None
        try:
            driver = self.setup_driver()
            
            origin = self.config.get('origin', 'DIY')
            destination = self.config.get('destination', 'IST')
            
            if self.search_flights(driver, origin, destination, date):
                prices = self.extract_prices_from_page(driver, date)
                return prices
            else:
                # Try alternative: direct URL to booking page
                print("   🔄 Trying alternative approach...")
                driver.get(f"https://www.turkishairlines.com/tr-tr/ucak-bileti/arama/")
                time.sleep(10)
                prices = self.extract_prices_from_page(driver, date)
                return prices
            
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
        print(f"Route: {self.config.get('origin', 'DIY')} → {self.config.get('destination', 'IST')}")
        print(f"Monitoring {len(self.config.get('dates', []))} dates")
        print(f"Price threshold: {self.config.get('price_threshold', 0)} TL")
        print("=" * 60)
        
        all_results = []
        threshold = self.config.get('price_threshold', float('inf'))
        
        for date in self.config.get('dates', []):
            prices = self.check_flight_prices(date.strip())
            
            if prices:
                # Store in history
                history_key = f"{date}_{datetime.now().strftime('%Y%m%d_%H%M')}"
                self.price_history[history_key] = {
                    'date': date,
                    'timestamp': datetime.now().isoformat(),
                    'prices': prices
                }
                
                # Check if any price is below threshold
                low_prices = [p for p in prices if p['price'] <= threshold]
                
                if low_prices:
                    all_results.append({
                        'date': date,
                        'low_prices': low_prices,
                        'min_price': min(p['price'] for p in low_prices),
                        'alert': True
                    })
                else:
                    min_price = min(p['price'] for p in prices)
                    all_results.append({
                        'date': date,
                        'prices': prices,
                        'min_price': min_price,
                        'alert': False
                    })
                    print(f"   📊 Lowest price: {min_price} TL (threshold: {threshold} TL)")
            
            # Small delay between date checks
            time.sleep(5)
        
        # Save history
        self.save_price_history()
        
        # Send notifications if needed
        alerts = [r for r in all_results if r.get('alert', False)]
        if alerts:
            self.send_notifications(alerts)
        else:
            print("\n📢 No prices below threshold found")
            # Send summary anyway every few runs
            if len(all_results) > 0:
                min_overall = min(r.get('min_price', float('inf')) for r in all_results if r.get('min_price'))
                if min_overall < float('inf'):
                    print(f"   💡 Current lowest price across all dates: {min_overall} TL")
        
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
