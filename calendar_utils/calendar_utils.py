from datetime import datetime, timedelta
import random

def get_free_slots():
    now = datetime.now()
    slots = []
    for i in range(1, 5):
        slot_time = now + timedelta(days=i, hours=random.randint(9, 17))
        slots.append({
            "start": {"dateTime": slot_time.isoformat()},
            "end": {"dateTime": (slot_time + timedelta(minutes=30)).isoformat()},
        })
    return slots

def book_meeting(start_time, end_time):
    # Just simulate a booking link
    return f"https://www.google.com/calendar/event?eid=dummyevent{random.randint(1000,9999)}"
