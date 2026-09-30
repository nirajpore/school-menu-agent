#!/usr/bin/env python3
"""
School Menu Extractor - Based on proven working logic
Extracts all menu data and saves as JSON
"""

import re
import os
import json
from datetime import datetime, timedelta

def extract_menu_data():
    """Extract menu using the working method"""
    try:
        # Use the same method that worked in our test
        import subprocess
        
        result = subprocess.run(['python', '-c', '''
from hermes_tools import read_file
import re

content = read_file("menu.pdf")["content"]
lines = content.split('\\n')
menu_data = []
current_week_start = None

for line in lines:
    clean_line = re.sub(r'^\\d+\\|', '', line).strip()
    
    # Find week starting dates
    if '#' in clean_line and any(month in clean_line for month in ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']):
        date_match = re.search(r'#\\s+(\\d+\\s+[A-Za-z]+)', clean_line)
        if date_match:
            current_week_start = date_match.group(1)
    
    # Parse menu lines
    elif clean_line.startswith('|') and current_week_start and '---' not in clean_line:
        items = clean_line.split('|')
        if len(items) >= 6 and items[1].strip() and not items[1].startswith('-'):
            day_meals = items[1:6]
            
            # Add to menu data with meal type detection
            for i, meal in enumerate(day_meals):
                meal = meal.strip()
                if meal:
                    menu_data.append({
                        'week_start': current_week_start,
                        'day_index': i,
                        'meal': meal
                    })

print(json.dumps(menu_data))
'''], capture_output=True, text=True)
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"Extraction failed: {result.stderr}")
            return []
            
    except Exception as e:
        print(f"Error: {e}")
        return []

def map_menu_to_dates(menu_data):
    """Map menu data to actual calendar dates"""
    dated_menu = []
    
    for item in menu_data:
        try:
            # Parse week start date
            date_str = item['week_start'].replace('th', '').replace('st', '').replace('nd', '').replace('rd', '')
            week_start = datetime.strptime(f"{date_str} 2026", "%d %B %Y")
            
            # Calculate actual date
            meal_date = week_start + timedelta(days=item['day_index'])
            
            dated_menu.append({
                'date': meal_date.strftime('%Y-%m-%d'),
                'day': meal_date.strftime('%A'),
                'week_start': item['week_start'],
                'meal': item['meal']
            })
        except:
            continue
    
    return dated_menu

def save_menu_data(dated_menu):
    """Save menu data to JSON file"""
    with open('menu_data.json', 'w') as f:
        json.dump(dated_menu, f, indent=2)
    print(f"✅ Menu data saved: {len(dated_menu)} items")

def main():
    print("🏫 School Menu Extractor - Creating JSON database")
    
    # Extract menu data
    menu_data = extract_menu_data()
    
    if not menu_data:
        print("❌ No menu data extracted")
        return
    
    print(f"📋 Extracted {len(menu_data)} menu items")
    
    # Map to dates
    dated_menu = map_menu_to_dates(menu_data)
    
    # Save to JSON
    save_menu_data(dated_menu)
    
    # Show sample
    print("\n📊 Sample of extracted data:")
    for item in dated_menu[:5]:
        print(f"  {item['date']} ({item['day']}): {item['meal']}")

if __name__ == "__main__":
    main()