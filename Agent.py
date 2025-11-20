from google.adk.agents import LlmAgent
import datetime
import os
from Utils import load_markdown_content
#tools custom
from Tools import(
    tool_find_availability,
    tool_list_upcoming_events,
    tool_force_add_event,
    tool_safe_add_event
)

FLASH_MODEL="gemini-2.5-flash"
PRO_MODEL="gemini-2.5-pro"
    
#Root agent
calendar_agent=LlmAgent(
    name="CalendarManagementAgent",
    description=load_markdown_content("description.md"),
    instruction=load_markdown_content("instructions.md"),
    model=PRO_MODEL,
    tools=[
        tool_find_availability,
        tool_list_upcoming_events,
        tool_force_add_event,
        tool_safe_add_event
    ],
    sub_agents=[]
)