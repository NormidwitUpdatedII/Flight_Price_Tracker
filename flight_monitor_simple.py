"""
Flight Price Monitor - Simple Version for Cloud Deployment
Works without Selenium - sends Telegram updates about your flight search
"""

import time
import os
from datetime import datetime
import requests

class FlightPriceMonitor:
    def __init__(self):
        """Initialize the flight price monitor"""
        self.config = self.load_config()
        self.last_check = None
        
    def load_config(self):
        """Load configuration from environment variables"""
        print("📡 Loading configuration from environment variables...")
        return {
            'price_threshold': float(os.getenv('PRICE_THRESHOLD', 2000)),
            'check_interval_minutes': int(os.getenv('CHECK_INTERVAL', 60)),
            'origin': os.getenv('ORIGIN', 'DIY'),
            'destination': os.getenv('DESTINATION', 'IST'),
            'dates': os.getenv('DATES', '2026-02-04,2026-02-05,2026-02-06,2026-02-07').split(','),
            'telegram_bot_token': os.getenv('TELEGRAM_BOT_TOKEN', ''),
            'telegram_chat_id': os.getenv('TELEGRAM_CHAT_ID', '')
        }
    
    def send_telegram_message(self, message):
        """Send a message via Telegram"""
        try:
            bot_token = self.config.get('telegram_bot_token')
            chat_id = self.config.get('telegram_chat_id')
            
            if not bot_token or not chat_id:
                print("⚠️ Telegram not configured")
                return False
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=30)
            if response.status_code == 200:
                print("✅ Telegram message sent!")
                return True
            else:
                print(f"⚠️ Telegram error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending Telegram: {str(e)}")
            return False
    
    def get_booking_url(self, date):
        """Generate Turkish Airlines booking URL"""
        # Format: YYYY-MM-DD to DDMMYYYY
        parts = date.split('-')
        if len(parts) == 3:
            formatted_date = f"{parts[2]}{parts[1]}{parts[0]}"
        else:
            formatted_date = date.replace('.', '')
        
        origin = self.config.get('origin', 'DIY')
        dest = self.config.get('destination', 'IST')
        
        url = f"https://www.turkishairlines.com/tr-tr/ucak-bileti/arama/?adultCount=1&childCount=0&infantCount=0&departDate={formatted_date}&arrivalDate=&tripType=O&originCode={origin}&destinationCode={dest}"
        return url
    
    def check_and_notify(self):
        """Main check function - sends reminder with booking links"""
        now = datetime.now()
        
        print("=" * 60)
        print("🛫 Flight Price Monitor - Status Update")
        print("=" * 60)
        print(f"Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Route: {self.config.get('origin')} → {self.config.get('destination')}")
        print(f"Dates: {', '.join(self.config.get('dates', []))}")
        print(f"Threshold: {self.config.get('price_threshold')} TL")
        print("=" * 60)
        
        # Build message with booking links
        message = "🛫 <b>Flight Price Check Reminder</b>\n\n"
        message += f"📍 Route: <b>{self.config.get('origin')} → {self.config.get('destination')}</b>\n"
        message += f"💰 Your target: <b>{self.config.get('price_threshold')} TL</b>\n\n"
        message += "🔗 <b>Check prices now:</b>\n\n"
        
        for date in self.config.get('dates', []):
            url = self.get_booking_url(date)
            # Format date nicely
            if '-' in date:
                parts = date.split('-')
                nice_date = f"{parts[2]}.{parts[1]}.{parts[0]}"
            else:
                nice_date = date
            message += f"📅 {nice_date}\n{url}\n\n"
        
        message += "━━━━━━━━━━━━━━━\n"
        message += f"⏰ Next check in {self.config.get('check_interval_minutes', 60)} minutes\n"
        message += f"🕐 Checked: {now.strftime('%H:%M')}"
        
        # Send to Telegram
        sent = self.send_telegram_message(message)
        
        if sent:
            print("\n✅ Reminder sent to Telegram!")
        else:
            print("\n⚠️ Could not send Telegram message")
        
        print("=" * 60)
        
        return sent
    
    def run_continuous(self):
        """Run monitoring continuously"""
        check_interval = self.config.get('check_interval_minutes', 60)
        
        # Send startup message
        startup_msg = "🚀 <b>Flight Monitor Started!</b>\n\n"
        startup_msg += f"✈️ Route: {self.config.get('origin')} → {self.config.get('destination')}\n"
        startup_msg += f"📅 Dates: {', '.join(self.config.get('dates', []))}\n"
        startup_msg += f"💰 Target: {self.config.get('price_threshold')} TL\n"
        startup_msg += f"⏰ Check interval: {check_interval} minutes\n\n"
        startup_msg += "You'll receive booking links to check prices manually.\n"
        startup_msg += "Click the links to see current prices on Turkish Airlines!"
        
        self.send_telegram_message(startup_msg)
        
        print("\n🚀 Flight Monitor is running!")
        print(f"📱 Sending updates every {check_interval} minutes")
        
        while True:
            try:
                self.check_and_notify()
                
                print(f"\n⏰ Next check in {check_interval} minutes...")
                print("   (Press Ctrl+C to stop)\n")
                
                time.sleep(check_interval * 60)
                
            except KeyboardInterrupt:
                print("\n\n👋 Monitor stopped by user")
                self.send_telegram_message("👋 Flight Monitor stopped.")
                break
                
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print("⏰ Retrying in 5 minutes...")
                time.sleep(300)

if __name__ == "__main__":
    monitor = FlightPriceMonitor()
    monitor.run_continuous()
