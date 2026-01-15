"""
Turkish Airlines Flight Price Monitor - Alternative Version
Uses SerpApi (Google Flights) for reliable price monitoring
Free tier: 100 searches/month
"""

import time
import json
import os
from datetime import datetime
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
        if os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('SERPAPI_KEY'):
            print("📡 Loading configuration from environment variables...")
            return {
                'price_threshold': float(os.getenv('PRICE_THRESHOLD', 2000)),
                'check_interval_minutes': int(os.getenv('CHECK_INTERVAL', 60)),
                'origin': os.getenv('ORIGIN', 'DIY'),
                'destination': os.getenv('DESTINATION', 'IST'),
                'dates': os.getenv('DATES', '2026-02-04,2026-02-05,2026-02-06,2026-02-07').split(','),
                'serpapi_key': os.getenv('SERPAPI_KEY', ''),
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
            print(f"⚠️  Config file {config_file} not found!")
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
    
    def check_flight_with_serpapi(self, origin, destination, date):
        """
        Check flight prices using SerpApi Google Flights
        Free tier: 100 searches/month
        Sign up at: https://serpapi.com/
        """
        api_key = self.config.get('serpapi_key', '')
        if not api_key:
            print("   ⚠️ SerpApi key not configured - using mock data for demo")
            # Return mock data for demonstration
            return [{
                'price': 1850,
                'airline': 'Turkish Airlines',
                'departure_time': '08:00',
                'arrival_time': '10:15',
                'duration': '2h 15m',
                'text': '1.850 TL'
            }]
        
        try:
            # SerpApi Google Flights endpoint
            url = "https://serpapi.com/search.json"
            params = {
                'engine': 'google_flights',
                'departure_id': origin,
                'arrival_id': destination,
                'outbound_date': date,
                'currency': 'TRY',
                'hl': 'tr',
                'api_key': api_key,
                'type': '2'  # One-way
            }
            
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            
            flights = []
            
            if 'best_flights' in data:
                for flight in data['best_flights']:
                    price = flight.get('price', 0)
                    flights.append({
                        'price': price,
                        'airline': flight.get('flights', [{}])[0].get('airline', 'Unknown'),
                        'departure_time': flight.get('flights', [{}])[0].get('departure_airport', {}).get('time', ''),
                        'arrival_time': flight.get('flights', [{}])[-1].get('arrival_airport', {}).get('time', ''),
                        'duration': flight.get('total_duration', ''),
                        'text': f"{price} TL"
                    })
            
            if 'other_flights' in data:
                for flight in data['other_flights']:
                    price = flight.get('price', 0)
                    flights.append({
                        'price': price,
                        'airline': flight.get('flights', [{}])[0].get('airline', 'Unknown'),
                        'departure_time': flight.get('flights', [{}])[0].get('departure_airport', {}).get('time', ''),
                        'arrival_time': flight.get('flights', [{}])[-1].get('arrival_airport', {}).get('time', ''),
                        'duration': flight.get('total_duration', ''),
                        'text': f"{price} TL"
                    })
            
            return flights
            
        except Exception as e:
            print(f"   ❌ SerpApi error: {str(e)}")
            return []
    
    def check_flight_prices(self, date):
        """Check flight prices for a specific date"""
        print(f"\n🔍 Checking flights for {date}...")
        
        origin = self.config.get('origin', 'DIY')
        destination = self.config.get('destination', 'IST')
        
        prices = self.check_flight_with_serpapi(origin, destination, date)
        
        if prices:
            print(f"   ✅ Found {len(prices)} flights")
            for p in sorted(prices, key=lambda x: x['price'])[:5]:
                print(f"      💰 {p['text']} - {p.get('airline', '')} ({p.get('departure_time', '')})")
        else:
            print("   ⚠️ No flights found")
        
        return prices
    
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
                return False
            
            bot_token = telegram_config.get('bot_token')
            chat_id = telegram_config.get('chat_id')
            
            if not all([bot_token, chat_id]):
                print("⚠️  Telegram configuration incomplete")
                return False
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data)
            if response.status_code == 200:
                print("✅ Telegram notification sent!")
                return True
            else:
                print(f"⚠️  Telegram notification failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending Telegram: {str(e)}")
            return False
    
    def check_and_notify(self):
        """Main monitoring function"""
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
                # Find minimum price
                min_price = min(p['price'] for p in prices)
                
                # Store in history
                history_key = f"{date}_{datetime.now().strftime('%Y%m%d_%H%M')}"
                self.price_history[history_key] = {
                    'date': date,
                    'timestamp': datetime.now().isoformat(),
                    'min_price': min_price,
                    'flights': prices
                }
                
                # Check if below threshold
                low_prices = [p for p in prices if p['price'] <= threshold]
                
                if low_prices:
                    all_results.append({
                        'date': date,
                        'low_prices': low_prices,
                        'min_price': min_price,
                        'alert': True
                    })
                else:
                    all_results.append({
                        'date': date,
                        'prices': prices,
                        'min_price': min_price,
                        'alert': False
                    })
                    print(f"   📊 Lowest: {min_price} TL (threshold: {threshold} TL)")
            
            time.sleep(3)
        
        # Save history
        self.save_price_history()
        
        # Send notifications for alerts
        alerts = [r for r in all_results if r.get('alert', False)]
        if alerts:
            self.send_notifications(alerts)
        else:
            print("\n📢 No prices below threshold")
            if all_results:
                min_overall = min(r.get('min_price', float('inf')) for r in all_results if r.get('min_price'))
                if min_overall < float('inf'):
                    print(f"   💡 Lowest price across all dates: {min_overall} TL")
        
        print("\n" + "=" * 60)
        print(f"✅ Check completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        return all_results
    
    def send_notifications(self, alerts):
        """Send notifications for price alerts"""
        subject = f"🎉 Flight Price Alert - Prices below {self.config.get('price_threshold')} TL!"
        
        message_html = "<h2>✈️ Flight Price Alert!</h2>"
        message_html += f"<p>Prices below your threshold of {self.config.get('price_threshold')} TL:</p>"
        
        message_text = "✈️ Flight Price Alert!\n\n"
        message_text += f"Prices below your threshold of {self.config.get('price_threshold')} TL:\n\n"
        
        for alert in alerts:
            date = alert['date']
            message_html += f"<h3>📅 {date}</h3><ul>"
            message_text += f"📅 {date}\n"
            
            for p in sorted(alert['low_prices'], key=lambda x: x['price'])[:5]:
                msg = f"💰 {p['text']} - {p.get('airline', '')} ({p.get('departure_time', '')} → {p.get('arrival_time', '')})"
                message_html += f"<li>{msg}</li>"
                message_text += f"  {msg}\n"
            
            message_html += "</ul>"
            message_text += "\n"
        
        message_html += f"<p><small>Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small></p>"
        
        self.send_email_notification(subject, message_html)
        self.send_telegram_notification(message_text)
    
    def run_continuous(self):
        """Run monitoring continuously"""
        check_interval = self.config.get('check_interval_minutes', 60)
        
        # Send a startup notification
        startup_msg = f"🚀 Flight Monitor Started!\n\nRoute: {self.config.get('origin')} → {self.config.get('destination')}\nThreshold: {self.config.get('price_threshold')} TL\nCheck interval: {check_interval} minutes"
        self.send_telegram_notification(startup_msg)
        
        while True:
            try:
                self.check_and_notify()
                print(f"\n⏰ Next check in {check_interval} minutes...")
                time.sleep(check_interval * 60)
            except KeyboardInterrupt:
                print("\n\n👋 Monitoring stopped by user")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print(f"⏰ Retrying in 5 minutes...")
                time.sleep(300)

if __name__ == "__main__":
    monitor = FlightPriceMonitor()
    monitor.run_continuous()
