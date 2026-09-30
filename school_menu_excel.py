#!/usr/bin/env python3
"""
School Menu Agent with Excel Mapping
"""

import re
import os
import smtplib
import pandas as pd
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pdfplumber

class ExcelMenuAgent:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        
    def extract_text_from_pdf(self) -> str:
        try:
            text = ""
            with pdfplumber.open(self.pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""
    
    def parse_menu_with_dates(self, content: str):
        lines = content.split('\n')
        menu_data = []
        current_week_start = None
        
        for line in lines:
            clean_line = line.strip()
            
            if '#' in clean_line and any(month in clean_line for month in 
                ['January', 'February', 'March', 'April', 'May', 'June', 
                 'July', 'August', 'September', 'October', 'November', 'December']):
                
                date_match = re.search(r'#\s+(\d+\s+[A-Za-z]+)', clean_line)
                if date_match:
                    try:
                        date_str = date_match.group(1).replace('th', '').replace('st', '').replace('nd', '').replace('rd', '')
                        current_week_start = datetime.strptime(f"{date_str} 2026", "%d %B %Y")
                    except:
                        current_week_start = datetime.strptime(f"{date_str} {datetime.now().year}", "%d %B %Y")
            
            elif clean_line.startswith('|') and current_week_start and '---' not in clean_line:
                items = clean_line.split('|')
                if len(items) >= 6 and items[1].strip() and not items[1].startswith('-'):
                    day_meals = items[1:6]
                    
                    for i, meal in enumerate(day_meals):
                        meal_date = current_week_start + timedelta(days=i)
                        menu_data.append({
                            'date': meal_date.strftime('%Y-%m-%d'),
                            'day': meal_date.strftime('%A'),
                            'meal': meal.strip()
                        })
        
        return menu_data
    
    def create_excel_spreadsheet(self, menu_data):
        df = pd.DataFrame(menu_data)
        df.to_excel('school_menu_calendar.xlsx', index=False)
        print("✅ Excel spreadsheet created")
        return df
    
    def get_tomorrows_menu_from_excel(self):
        try:
            df = pd.read_excel('school_menu_calendar.xlsx')
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            tomorrow_menu = df[df['date'] == tomorrow]
            if not tomorrow_menu.empty:
                return tomorrow_menu.iloc[0]['meal']
            return None
        except:
            return None
    
    def send_email_smtp(self, menu_text: str):
        tomorrow = datetime.now() + timedelta(days=1)
        subject = f"School Menu - {tomorrow.strftime('%A %d %B %Y')}"
        
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')
        email_to = os.getenv('EMAIL_TO')
        
        if not all([smtp_server, smtp_username, smtp_password, email_to]):
            print("❌ Email configuration missing")
            return
        
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = email_to
        msg['Subject'] = subject
        
        body = f"""📋 School Dinner Menu for {tomorrow.strftime('%A %d %B %Y')}

🍽️ Main Course: {menu_text}

🍎 Available Every Day:
- Crunchy colourful Salad Bar
- Jacket Potatoes with Cheese, Beans, Tuna Mayonnaise or Cheese & Beans

Note: Menu subject to change.
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
        print(f"🏫 School Menu Agent - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        content = self.extract_text_from_pdf()
        if not content:
            print("❌ Could not extract menu from PDF")
            return
            
        menu_data = self.parse_menu_with_dates(content)
        self.create_excel_spreadsheet(menu_data)
        
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrows_menu = self.get_tomorrows_menu_from_excel()
        
        if tomorrows_menu:
            print(f"🍽️ Tomorrow's menu: {tomorrows_menu}")
            self.send_email_smtp(tomorrows_menu)
        else:
            print("📅 No school tomorrow")

if __name__ == "__main__":
    pdf_path = os.getenv('PDF_PATH', './menu.pdf')
    agent = ExcelMenuAgent(pdf_path)
    agent.run_daily_check()
