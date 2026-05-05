import os
import json
import requests
import html
from datetime import datetime

# Load credentials from environment variables
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

def load_questions(filename='questions.json'):
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data['questions']

def get_daily_question(questions):
    # Use the current date to pick a question sequentially
    # This ensures we move to the next question every day without needing a database
    
    # We set a start date (April 28, 2026) so that question 0 is selected on this day
    start_date = datetime(2026, 4, 28).toordinal()
    days_since_epoch = datetime.utcnow().toordinal()
    
    days_since_start = days_since_epoch - start_date
    question_index = days_since_start % len(questions)
    
    return questions[question_index]

def send_telegram_message(question):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # Escape special characters to avoid breaking Telegram HTML parser
    safe_title = html.escape(question['title'])
    safe_pattern = html.escape(question['pattern'])
    safe_difficulty = html.escape(question['difficulty'])
    safe_concept = html.escape(question['concept_refresher'])
    safe_mental_model = html.escape(question['mental_model'])

    # Format the message using HTML and spoiler tags
    message_text = f"""
<b>Daily NeetCode Challenge</b> 🚀

<b>Question:</b> {safe_title}
<b>Pattern:</b> {safe_pattern}
<b>Difficulty:</b> {safe_difficulty}

<a href="{question['url']}">Click here to solve</a>

<b>Concept & Mental Model (Tap to reveal):</b>
<tg-spoiler><b>Concept:</b> {safe_concept}</tg-spoiler>
<tg-spoiler><b>Mental Model:</b> {safe_mental_model}</tg-spoiler>
"""

    payload = {
        "chat_id": CHAT_ID,
        "text": message_text,
        "parse_mode": "HTML",
        # Disables link previews so the chat stays clean
        "disable_web_page_preview": True 
    }
    
    response = requests.post(url, json=payload)
    
    # Debug logging
    print(f"DEBUG - CHAT_ID: {CHAT_ID}")
    print(f"DEBUG - Response Status: {response.status_code}")
    print(f"DEBUG - Response Body: {response.text}")
    
    response.raise_for_status()
    print("Message sent successfully!")

def main():
    if not TELEGRAM_TOKEN or not CHAT_ID:
        raise ValueError("Missing Telegram credentials in environment variables.")
        
    questions = load_questions()
    daily_question = get_daily_question(questions)
    send_telegram_message(daily_question)

if __name__ == '__main__':
    main()