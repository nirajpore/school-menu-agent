#!/usr/bin/env python3
"""
Complete School Menu Agent - Extracts all meal components
"""

import re
import os
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pdfplumber

def parse_menu_from_pdf(pdf_path):
    """Extract and parse all menu components from PDF"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or "" + "\n"
        
        # Parse the menu structure
        lines = text.split('\n')
        menu_data = []
        current_week = None
        
        for line in lines:
            clean_line = re.sub(r'^\d+\|', '', line).strip()
            
            # Find week starting dates
            if '#' in clean_line and any(month in clean_line for month in 
                ['January', 'February', 'March', 'April', 'May', 'June', 
                 'July', 'August', 'September', 'October', 'November', 'December']):
                
                date_match = re.search(r'#\s+(\d+\s+[A-Za-z]+)', clean_line)
                if date_match:
                    current_week = date_match.group(1)
            
            # Parse menu lines
            elif clean_line.startswith('|') and current_week and '---' not in clean_line:
                items = clean_line.split('|')
                if len(items) >= 6 and items[1].strip() and not items[1].startswith('-'):
                    day_meals = items[1:6]
                    
                    # Add to menu data with meal type detection
                    for i, meal in enumerate(day_meals):
                        meal = meal.strip()
                        if meal:
                            meal_type = 'main'
                            meal_lower = meal.lower()
                            
                            if any(word in meal_lower for word in ['halal', 'beef', 'chicken', 'fish', 'turkey']):
                                meal_type = 'halal'
                            elif any(word in meal_lower for word in ['vegetable', 'vegan', 'bean', 'cauliflower', 'quorn']):
                                meal_type = 'vegetarian'
                            elif any(word in meal_lower for word in ['carrot', 'pea', 'broccoli', 'cabbage', 'salad']):
                                meal_type = 'vegetables'
                            elif 'pasta' in meal_lower:
                                meal_type = 'pasta'
                            elif any(word in meal_lower for word in ['biscuit', 'brownie', 'jelly', 'crumble', 'custard', 'yoghurt', 'cake']):
                                meal_type = 'dessert'
                            
                            menu_data.append({
                                'week': current_week,
                                'day_index': i,
                                'meal': meal,
                                'type': meal_type
                            })
        
        return menu_data
        
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return []

def get_tomorrows_menu(menu_data):
    """Get tomorrow's menu from parsed data"""
    tomorrow = datetime.now() + timedelta(days=1)
    day_index = tomorrow.weekday()  # Monday=0, Friday=4
    
    if day_index >= 5:  # Weekend
        return None
    
    # Filter for tomorrow's meals
    tomorrows_meals = [meal for meal in menu_data if meal['day_index'] == day_index]
    
    # Organize by type
    organized = {
        'vegetarian': [],
        'halal': [],
        'vegetables': [],
        'pasta': [],
        'dessert': []
    }
    
    for meal in tomorrows_meals:
        if meal['type'] in organized:
            organized[meal['type']].append(meal['meal'])
    
    return organized

def send_menu_email(menu_data):
    """Send email with tomorrow's menu"""
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    email_to = os.getenv('EMAIL_TO')
    
    if not all([smtp_server, smtp_username, smtp_password, email_to]):
        print("Email configuration missing")
        return
    
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%A %d %B %Y')
    menu = get_tomorrows_menu(menu_data)
    
    if not menu:
        print("No school tomorrow")
        return
    
    # Build email body
    body = f"🍽️ School Dinner Menu for {tomorrow}\n\n"
    
    if menu['vegetarian']:
        body += "🌱 Vegetarian Options:\n"
        for meal in menu['vegetarian']:
            body += f"• {meal}\n"
        body += "\n"
    
    if menu['halal']:
        body += "☪️ Halal Options:\n"
        for meal in menu['halal']:
            body += f"• {meal}\n"
        body += "\n"
    
    if menu['vegetables']:
        body += "🥦 Vegetables:\n"
        for meal in menu['vegetables']:
            body += f"• {meal}\n"
        body += "\n"
    
    if menu['pasta']:
        body += "🍝 Pasta Options:\n"
        for meal in menu['pasta']:
            body += f"• {meal}\n"
        body += "\n"
    
    if menu['dessert']:
        body += "🍰 Desserts:\n"
        for meal in menu['dessert']:
            body += f"• {meal}\n"
        body += "\n"
    
    body += "🍎 Available Every Day:\n"
    body += "• Crunchy colourful Salad Bar\n"
    body += "• Jacket Potatoes with Cheese, Beans, Tuna Mayonnaise or Cheese & Beans\n\n"
    body += "Note: Menu subject to change. Please check with the school for updates."
    
    # Send email
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = email_to
    msg['Subject'] = f"School Menu - {tomorrow}"
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        print("✅ Menu email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def main():
    print("🏫 School Menu Agent - Starting...")
    
    pdf_path = os.getenv('PDF_PATH', './menu.pdf')
    
    if not os.path.exists(pdf_path):
        print("❌ PDF file not found")
        return
    
    print("📄 Extracting menu from PDF...")
    menu_data = parse_menu_from_pdf(pdf_path)
    
    if not menu_data:
        print("❌ No menu data extracted")
        return
    
    print(f"✅ Extracted {len(menu_data)} menu items")
    send_menu_email(menu_data)

if __name__ == "__main__":
    main()