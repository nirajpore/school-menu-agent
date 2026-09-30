#!/usr/bin/env python3
"""
School Menu Agent - Reads PDF menu and sends daily email notifications
"""

import re
from datetime import datetime, timedelta
import calendar
import subprocess
from typing import Dict, Optional

class SchoolMenuAgent:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.uk_holidays = self._load_uk_holidays()
        
    def _load_uk_holidays(self) -> Dict[str, str]:
        """Load UK public holidays for 2026"""
        # UK public holidays for 2026
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
    
    def extract_menu_from_pdf(self) -> str:
        """Extract text content from PDF using direct file reading"""
        try:
            # Use read_file function directly since we're in Hermes context
            from hermes_tools import read_file
            result = read_file(self.pdf_path)
            return result.get("content", "")
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""
    
    def parse_menu(self, content: str) -> Dict[str, Dict[str, str]]:
        """Parse menu content into structured data"""
        lines = content.split('\n')
        menu_data = {}
        current_week = None
        
        for line in lines:
            # Remove line numbers and pipe separators
            clean_line = re.sub(r'^\d+\|', '', line).strip()
            
            if '#' in clean_line and any(month in clean_line for month in ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']):
                # Extract date information
                date_match = re.search(r'#\s+(\d+\s+[A-Za-z]+)', clean_line)
                if date_match:
                    current_week = date_match.group(1)
            elif clean_line.startswith('|') and current_week and '---' not in clean_line:
                # This is a menu line (skip separator lines)
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
        # Check if weekend
        if date.weekday() >= 5:  # Saturday or Sunday
            return False
            
        # Check if UK public holiday
        date_str = date.strftime('%Y-%m-%d')
        if date_str in self.uk_holidays:
            return False
            
        return True
    
    def get_tomorrows_menu(self, menu_data: Dict[str, Dict[str, str]]) -> Optional[str]:
        """Get tomorrow's menu from parsed data"""
        tomorrow = datetime.now() + timedelta(days=1)
        
        if not self.is_school_day(tomorrow):
            return None
            
        # Simple lookup - in production, we'd map dates to specific weeks
        day_name = tomorrow.strftime('%A')
        
        # Find the appropriate week (this is simplified)
        for week_meals in menu_data.values():
            if day_name in week_meals:
                return week_meals[day_name]
        
        return "Menu not found for tomorrow"
    
    def send_email_notification(self, menu_text: str):
        """Send email notification using Himalaya CLI"""
        tomorrow = datetime.now() + timedelta(days=1)
        subject = f"School Menu - {tomorrow.strftime('%A %d %B %Y')}"
        
        email_content = f"""From: school-menu-agent@example.com
To: YOUR_EMAIL_HERE
Subject: {subject}

📋 School Dinner Menu for {tomorrow.strftime('%A %d %B %Y')}

🍽️ Main Course: {menu_text}

🍎 Available Every Day:
- Crunchy colourful Salad Bar
- Jacket Potatoes with Cheese, Beans, Tuna Mayonnaise or Cheese & Beans

Note: Menu subject to change. Please check with the school for updates.
"""
        
        try:
            # Send email using Himalaya
            result = subprocess.run(
                ['himalaya', 'template', 'send'],
                input=email_content,
                text=True,
                capture_output=True
            )
            
            if result.returncode == 0:
                print("✅ Email notification sent successfully!")
            else:
                print(f"❌ Failed to send email: {result.stderr}")
                
        except FileNotFoundError:
            print("❌ Himalaya CLI not found. Please install it or configure email sending.")
    
    def run_daily_check(self):
        """Main method to run the daily check"""
        print(f"🏫 School Menu Agent - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Extract and parse menu
        content = self.extract_menu_from_pdf()
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
            self.send_email_notification(tomorrows_menu)

# Configuration
PDF_PATH = "C:\\Users\\Karthika Niraj's PC\\Downloads\\2_Harris Chafford Hundred & Primary Academy Chafford Hundred_755 (1).pdf"

if __name__ == "__main__":
    agent = SchoolMenuAgent(PDF_PATH)
    agent.run_daily_check()