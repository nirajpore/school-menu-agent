#!/usr/bin/env python3
"""
School Menu Agent for GitHub Actions - Cloud-based version
"""

import re
import os
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from typing import Dict, Optional

class SchoolMenuAgent:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.uk_holidays = self._load_uk_holidays()
        
    def _load_uk_holidays(self) -> Dict[str, str]:
        """Load UK public holidays for 2026"""
        return {
            "2026-01-01": "New Year's Day",
            "2026-04-03": "Good Friday",
            "2026-04-06": "Easter Monday",
            "2026-05-04": "Early May Bank Holiday",
            "2026-05-25": "Spring Bank Holiday", 
            "2026-08-31": "Summer Bank Holiday",
            "2026-12-25": "Christmas Day",
            "2026-12-28": "Boxing Day (substitute)"
        }
    
    def extract_text_from_pdf(self) -> str:
        """Extract text from PDF using pdfplumber"""
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(self.pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            return text
        except ImportError:
            print("pdfplumber not available, trying fallback...")
            return self._fallback_pdf_extraction()
    
    def _fallback_pdf_extraction(self) -> str:
        """Fallback PDF extraction using pdftotext"""
        try:
            import subprocess
            result = subprocess.run(['pdftotext', self.pdf_path, '-'], 
                                  capture_output=True, text=True)
            return result.stdout
        except:
            return ""
    
    def parse_menu(self, content: str) -> Dict[str, Dict[str, str]]:
        """Parse menu content into structured data"""
        lines = content.split('\n')
        menu_data = {}
        current_week = None
        
        for line in lines:
            clean_line = line.strip()
            
            if '#' in clean_line and any(month in clean_line for month in ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']):
                date_match = re.search(r'#\s+(\d+\s+[A-Za-z]+)', clean_line)
                if date_match:
                    current_week = date_match.group(1)
            elif clean_line.startswith('|') and current_week and '---' not in clean_line:
                items = clean_line.split('|')
                if len(items) >= 6 and items[1].strip() and not items[1].startswith('-'):
                    day_meals = items[1:6]
                    menu_data[current_week] = {
                        'Monday': day_meals[0],
                        'Tuesday': day_meals[1], 
                        'Wednesday': day_meals[2],
                        'Thursday': day_meals[3],
                        'Friday': day_meals[4]
                    }
        
        return menu_data
    
    def is_school_day(self, date: datetime) -> bool:
        """Check if it's a school day (Mon-Fri and not a UK holiday)"""
        if date.weekday() >= 5:  # Saturday or Sunday
            return False
            
        date_str = date.strftime('%Y-%m-%d')
        if date_str in self.uk_holidays:
            return False
            
        return True
    
    def get_tomorrows_menu(self, menu_data: Dict[str, Dict[str, str]]) -> Optional[str]:
        """Get tomorrow's menu from parsed data"""
        tomorrow = datetime.now() + timedelta(days=1)
        
        if not self.is_school_day(tomorrow):
            return None
            
        day_name = tomorrow.strftime('%A')
        
        for week_meals in menu_data.values():
            if day_name in week_meals:
                return week_meals[day_name]
        
        return "Menu not found for tomorrow"
    
    def send_email_smtp(self, menu_text: str):
        """Send email via SMTP"""
        tomorrow = datetime.now() + timedelta(days=1)
        subject = f"School Menu - {tomorrow.strftime('%A %d %B %Y')}"
        
        # Get SMTP settings from environment
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')
        email_to = os.getenv('EMAIL_TO')
        
        if not all([smtp_server, smtp_username, smtp_password, email_to]):
            print("❌ SMTP configuration missing")
            return
        
        # Create email
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = email_to
        msg['Subject'] = subject
        
        body = f"""📋 School Dinner Menu for {tomorrow.strftime('%A %d %B %Y')}

🍽️ Main Course: {menu_text}

🍎 Available Every Day:
- Crunchy colourful Salad Bar
- Jacket Potatoes with Cheese, Beans, Tuna Mayonnaise or Cheese & Beans

Note: Menu subject to change. Please check with the school for updates.
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            print("✅ Email sent successfully!")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
    
    def run_daily_check(self):
        """Main method to run the daily check"""
        print(f"🏫 School Menu Agent - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Extract and parse menu
        content = self.extract_text_from_pdf()
        if not content:
            print("❌ Could not extract menu from PDF")
            return
            
        menu_data = self.parse_menu(content)
        
        # Get tomorrow's menu
        tomorrows_menu = self.get_tomorrows_menu(menu_data)
        
        if tomorrows_menu is None:
            tomorrow = datetime.now() + timedelta(days=1)
            print(f"📅 {tomorrow.strftime('%A %d %B %Y')} - No school (weekend/holiday)")
        else:
            print(f"🍽️ Tomorrow's menu: {tomorrows_menu}")
            self.send_email_smtp(tomorrows_menu)

if __name__ == "__main__":
    # Get PDF path from environment or use default
    pdf_path = os.getenv('PDF_PATH', './menu.pdf')
    
    agent = SchoolMenuAgent(pdf_path)
    agent.run_daily_check()