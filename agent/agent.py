import os
import dateparser
from datetime import datetime, timedelta
from dotenv import load_dotenv
from openai import OpenAI

from calendar_utils.calendar_utils import get_free_slots, book_meeting

# Load .env variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_datetime(user_input):
    """Parses a datetime from natural language using dateparser."""
    dt = dateparser.parse(
        user_input,
        settings={
            'PREFER_DATES_FROM': 'future',
            'RELATIVE_BASE': datetime.now()
        }
    )
    return dt

def run_agent(user_input):
    """Main agent logic that:
    - Understands time from user input
    - Checks for conflicts
    - Books a 30-minute event
    """
    print(f"🧠 User input: {user_input}")

    dt = extract_datetime(user_input)
    if not dt:
        return "❌ I couldn't understand the date/time. Please say something like 'tomorrow at 2pm'."

    start_time = dt.isoformat()
    end_time = (dt + timedelta(minutes=30)).isoformat()

    # Check for existing events at that time
    events = get_free_slots()
    for event in events:
        existing_start = event['start'].get('dateTime')
        if existing_start and existing_start.startswith(dt.strftime("%Y-%m-%dT%H:%M")):
            return "⚠️ You already have an event scheduled at that time."

    # Book the meeting
    try:
        link = book_meeting(start_time, end_time)
        return f"✅ Meeting booked for {dt.strftime('%A, %B %d at %I:%M %p')}! [View in Calendar]({link})"
    except Exception as e:
        print(f"❌ Booking error: {e}")
        return "Something went wrong while trying to book the meeting. Please try again."
