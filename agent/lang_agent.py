import os
import dateparser
from datetime import datetime, timedelta
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from calendar_utils.calendar_utils import get_free_slots, book_meeting
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 1. Intent classification node
def classify_intent(state: dict) -> dict:
    user_input = state.get("user_input", "").lower()
    print("🔍 [classify_intent] Input:", user_input)

    try:
        system_prompt = (
            "Classify the user's intent as one of: "
            "'book_meeting', 'check_availability', or 'unknown'. "
            "Only respond with one of those options."
        )

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )
        intent = completion.choices[0].message.content.strip()
    except Exception as e:
        print("⚠️ GPT failed. Falling back. Error:", e)
        # Fallback rule-based classification
        if "free" in user_input or "available" in user_input:
            intent = "check_availability"
        elif "book" in user_input or "schedule" in user_input:
            intent = "book_meeting"
        else:
            intent = "unknown"

    state["intent"] = intent
    return state

# 2. Parse natural language time
import re
def parse_time(state: dict) -> dict:
    raw_input = state.get("user_input", "")
    cleaned_input = raw_input.strip().replace("“", "").replace("”", "").replace('"', '')
    print("🧩 [parse_time] Cleaned input:", cleaned_input)

    # Extract date phrases like 'tomorrow', 'next friday', etc.
    day_match = re.search(r"(today|tomorrow|next\s+\w+|\bmonday\b|\btuesday\b|\bwednesday\b|\bthursday\b|\bfriday\b|\bsaturday\b|\bsunday\b)", cleaned_input, re.IGNORECASE)
    
    # Extract time like '4pm' or 'at 4:30 pm'
    time_match = re.search(r"\b\d{1,2}(:\d{2})?\s*(am|pm)\b", cleaned_input, re.IGNORECASE)

    if day_match and time_match:
        time_phrase = f"{day_match.group()} at {time_match.group()}"
    elif time_match:
        time_phrase = time_match.group()
    elif day_match:
        time_phrase = day_match.group()
    else:
        time_phrase = cleaned_input  # fallback

    print("🕒 [parse_time] Extracted time phrase:", time_phrase)

    dt = dateparser.parse(time_phrase, settings={
        "PREFER_DATES_FROM": "future",
        "RELATIVE_BASE": datetime.now()
    })

    if not dt:
        state["error"] = f"❌ I couldn't understand the date/time from: '{time_phrase}'"
        return state

    state["datetime"] = dt
    print("✅ [parse_time] Parsed datetime:", dt)
    return state


# 3. Check availability
def check_availability(state: dict) -> dict:
    dt = state.get("datetime")
    if dt is None:
        state["error"] = "❌ No valid datetime to check availability."
        return state

    events = get_free_slots()
    for event in events:
        start = event.get("start", {}).get("dateTime", "")
        if start.startswith(dt.strftime("%Y-%m-%dT%H:%M")):
            state["error"] = "⚠️ You're already booked at that time."
            return state

    return state

# 4. Book the meeting
def book(state: dict) -> dict:
    dt = state.get("datetime")
    if dt is None:
        state["error"] = "❌ Cannot book meeting. No valid time provided."
        return state

    try:
        start_time = dt.isoformat()
        end_time = (dt + timedelta(minutes=30)).isoformat()
        link = book_meeting(start_time, end_time)

        state["response"] = f"✅ Meeting booked for {dt.strftime('%A, %B %d at %I:%M %p')}! [View in Calendar]({link})"
    except Exception as e:
        state["error"] = f"❌ Failed to book meeting: {str(e)}"

    print("✅ [book] Booking done.")
    return state

# 5. Respond with suggested free times
def respond_with_slots(state: dict) -> dict:
    print("📅 [respond_with_slots] Fetching available times...")
    user_input = state.get("user_input", "").lower()

    try:
        slots = get_free_slots()
        suggestions = []

        for event in slots:
            dt_raw = event.get("start", {}).get("dateTime", "")
            if not dt_raw:
                continue

            dt = dateparser.parse(dt_raw)
            if not dt:
                continue

            # 🧠 If user asked for "friday", filter for Friday only
            if "friday" in user_input:
                if dt.strftime("%A").lower() != "friday":
                    continue

            # Add formatted time
            suggestions.append(dt.strftime("%A at %I:%M %p"))

            # Limit to top 3 matching results
            if len(suggestions) >= 3:
                break

        if suggestions:
            state["response"] = f"🗓️ Here are some free times: {', '.join(suggestions)}"
        else:
            state["response"] = "⚠️ No free slots found for your request."

    except Exception as e:
        state["error"] = f"❌ Couldn't fetch calendar availability: {str(e)}"

    return state


# 6. Final response node
def respond(state: dict) -> dict:
    print("🧩 [respond] Final state:", state)
    return state

# Build LangGraph flow
builder = StateGraph(dict)

builder.add_node("classify_intent", classify_intent)
builder.add_node("parse_time", parse_time)
builder.add_node("check_availability", check_availability)
builder.add_node("book", book)
builder.add_node("respond_with_slots", respond_with_slots)
builder.add_node("respond", respond)

builder.set_entry_point("classify_intent")

builder.add_conditional_edges("classify_intent", lambda s: s.get("intent", "unknown"), {
    "book_meeting": "parse_time",
    "check_availability": "respond_with_slots",
    "unknown": "respond"
})

builder.add_edge("parse_time", "check_availability")
builder.add_edge("check_availability", "book")
builder.add_edge("book", "respond")
builder.add_edge("respond_with_slots", "respond")
builder.add_edge("respond", END)

graph = builder.compile()

# Entry function
def run_agent_with_langgraph(user_input: str) -> str:
    # Clean curly quotes and extra spaces at the source
    cleaned = user_input.strip().replace("“", "").replace("”", "").replace('"', '')

    state = {"user_input": cleaned}
    print("🚀 [run_agent] Starting LangGraph with:", cleaned)

    final_state = graph.invoke(state)
    print("🔁 [run_agent] Final LangGraph result:", final_state)

    if not isinstance(final_state, dict):
        return "❌ Internal error: LangGraph returned no result."

    return final_state.get("response") or final_state.get("error", "❌ No output generated.")
