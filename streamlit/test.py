from calendar_agent.calendarapi import read_calendar
from dotenv import load_dotenv
import os

load_dotenv()
creds = os.getenv("API_KEY")

date = {
    'start': '2025-01-01',
    'end': '2025-12-31'
}

creds = None

print(read_calendar(creds, date))