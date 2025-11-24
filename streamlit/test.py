from calendar_agent.calendarapi import read_calendar, accesso
from dotenv import load_dotenv
import os

load_dotenv()
creds = os.getenv("API_KEY")

date = {
    'start': '2025-01-01',
    'end': '2025-12-31'
}

creds = accesso()

print(read_calendar(creds, date))