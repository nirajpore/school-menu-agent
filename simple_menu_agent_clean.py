#!/usr/bin/env python3
"""
School Menu Agent - Simple JSON-based solution
Extracts menu once, stores as JSON, reads daily from JSON
"""

import re
import os
import smtplib
import json
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pdfplumber
from typing import Dict, List

class SimpleMenuAgent:
    def __init__(self):
        self.menu_data_path = "menu_data.json"
    
    def extract_full_menu(self, pdf_path: str) -> List[Dict]:
        """Extract complete menu from PDF (one-time operation)"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            
            return self._parse_menu_text(text)
        except Exception as e:
            print(f"Error extracting menu: {e}")
            return []
    
    def _parse_menu_text(self, content: str) -> List[Dict]:
        """Parse complete menu structure with all components"""
        lines = content.split('\n')
        menu_data = []
        current_week_start = None
        
        for line in lines:
            clean_line = re.sub(r'^\d+\|', '', line).strip()
            
            # Find week starting dates
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
            
            # Parse menu lines with all components
            elif clean_line.startswith('|') and current_week_start and '---' not in clean_line:
                items = clean_line.split('|')
                if len(items) >= 6 and items[1].strip() and not items[1].startswith('-'):
                    day_meals = items[1:6]
                    
                    # Map to actual dates (Monday to Friday)
                    for i, meal in enumerate(day_meals):
                        meal_date = current_week_start + timedelta(days=i)
                        
                        # Determine meal type based on content
                        meal_type = self._determine_meal_type(meal.strip(), i)
                        
                        menu_data.append({
                            'date': meal_date.strftime('%Y-%m-%d'),
                            'day': meal_date.strftime('%A'),
                            'meal': meal.strip(),
                            'type': meal_type,
                            'week_start': current_week_start.strftime('%Y-%m-%d')
                        })
        
        return menu_data
    
… omitted 143 diff line(s) across 1 additional file(s)/section(s)
