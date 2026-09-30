#!/usr/bin/env python3
"""
School Menu Emailer - Reads from JSON and sends daily email
"""

import os
import json
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def load_menu_data():
    """Load menu data from JSON file"""
    try:
        with open('menu_data_final_correct.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading menu_data_final_correct.json: {e}")
        return []

def get_tomorrows_menu(menu_data):
    """Get tomorrow's complete menu"""
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    tomorrows_meals = [item for item in menu_data if item['date'] == tomorrow]
    
    # Organize by meal type
    organized = {
        'vegetarian': [],
        'halal': [],
        'vegetables': [],
        'pasta': [],
        'dessert': []
    }
    
    for meal in tomorrows_meals:
        meal_text = meal['meal'].lower()
        
        if any(word in meal_text for word in ['halal', 'beef', 'chicken', 'fish', 'turkey']):
            organized['halal'].append(meal['meal'])
        elif any(word in meal_text for word in ['vegetable', 'vegan', 'bean', 'cauliflower', 'quorn']):
            organized['vegetarian'].append(meal['meal'])
        elif any(word in meal_text for word in ['carrot', 'pea', 'broccoli', 'cabbage', 'salad']):
            organized['vegetables'].append(meal['meal'])
        elif 'pasta' in meal_text:
            organized['pasta'].append(meal['meal'])
        elif any(word in meal_text for word in ['biscuit', 'brownie', 'jelly', 'crumble', 'custard', 'yoghurt', 'cake']):
            organized['dessert'].append(meal['meal'])
    
    return organized

def send_menu_email(menu_data):
    """Send email with tomorrow's menu"""
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    email_to = os.getenv('EMAIL_TO')
    
    if not all([smtp_server, smtp_username, smtp_password, email_to]):
        print("❌ Email configuration missing")
        return
    
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%A %d %B %Y')
    menu = get_tomorrows_menu(menu_data)
    
    if not any(menu.values()):  # No meals found
        print(f"📅 {tomorrow} - No school")
        return
    
    # Build email body
    body = f"🍽️ School Dinner Menu for {tomorrow}\n\n"
    
    for category, meals in menu.items():
        if meals:
            if category == 'vegetarian':
                body += "🌱 Vegetarian Options:\n"
            elif category == 'halal':
                body += "☪️ Halal Options:\n"
            elif category == 'vegetables':
                body += "🥦 Vegetables:\n"
            elif category == 'pasta':
                body += "🍝 Pasta Options:\n"
            elif category == 'dessert':
                body += "🍰 Desserts:\n"
            
            for meal in meals:
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
    print("📧 School Menu Emailer - Sending daily update")
    
    # Load menu data from JSON
    menu_data = load_menu_data()
    
    if not menu_data:
        print("❌ No menu data found in menu_data.json")
        return
    
    print(f"📋 Loaded {len(menu_data)} menu items from JSON")
    send_menu_email(menu_data)

if __name__ == "__main__":
    main()