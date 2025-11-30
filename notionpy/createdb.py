from notion_client import Client
import os, json

NOTION_TOKEN = os.environ.get("NOTION_API_KEY")  # or hardcode for testing
PARENT_PAGE_ID = "2ba2f5c3629680c4895bc1e6a9436c4a"  # the page where DB should live
DATABASE_ID = "49981d1a-216b-4c61-a40d-93680dfce770"


notion = Client(auth=NOTION_TOKEN)

import requests
import json

# --- You said you have this portion, just ensuring variable names match ---
# NOTION_TOKEN = "secret_..."
# PARENT_PAGE_ID = "..." 

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# The Payload defining the specific schema you requested
create_db_payload = {
    "parent": {
        "type": "page_id",
        "page_id": PARENT_PAGE_ID
    },
    "title": [
        {
            "type": "text",
            "text": {
                "content": "Master Task List"
            }
        }
    ],
    "properties": {
        "Task Name": {
            "title": {}
        },
        "Category": {
            "select": {
                "options": [
                    { "name": "Work", "color": "blue" },
                    { "name": "Home", "color": "orange" },
                    { "name": "Kids", "color": "yellow" },
                    { "name": "Health", "color": "red" },
                    { "name": "Finance", "color": "green" },
                    { "name": "Decluttering", "color": "purple" },
                    { "name": "Side Hustle", "color": "pink" },
                    { "name": "Social", "color": "brown" },
                    { "name": "Personal Dev", "color": "gray" }
                ]
            }
        },
        "Sub-Category": {
            "multi_select": {
                "options": [
                    { "name": "Dataflow" },
                    { "name": "CR" },
                    { "name": "Recruiter Call" },
                    { "name": "Cleaning" },
                    { "name": "Repairs" }
                ]
            }
        },
        "Priority": {
            "select": {
                "options": [
                    { "name": "P1 (Critical)", "color": "red" },
                    { "name": "P2 (High)", "color": "orange" },
                    { "name": "P3 (Medium)", "color": "blue" },
                    { "name": "P4 (Low)", "color": "gray" }
                ]
            }
        },
        "Status": {
            "select": {
                "options": [
                    { "name": "Open", "color": "gray" },
                    { "name": "In Progress", "color": "blue" },
                    { "name": "Waiting", "color": "yellow" },
                    { "name": "Done", "color": "green" },
                    { "name": "Canceled", "color": "red" },
                    { "name": "Deferred", "color": "purple" }
                ]
            }
        },
        "Due Date": {
            "date": {}
        },
        "Created / Logged At": {
            "created_time": {}
        },
        "Completed At": {
            "date": {}
        },
        "Context / Notes": {
            "rich_text": {}
        },
        "Location / Room": {
            "select": {
                "options": [
                    { "name": "Living Room" },
                    { "name": "Kitchen" },
                    { "name": "Garage" },
                    { "name": "Office" },
                    { "name": "Dining Room" },
                    { "name": "Bonus Room" }
                ]
            }
        },
        "Tags": {
            "multi_select": {
                "options": [
                    { "name": "Zander" },
                    { "name": "Zeev" },
                    { "name": "Grace" },
                    { "name": "Gonzalo" },
                    { "name": "Shayne" },
                    { "name": "Health" },
                    { "name": "Mood" },
                    { "name": "Dataflow" }
                ]
            }
        },
        "Recurrence": {
            "select": {
                "options": [
                    { "name": "One-time" },
                    { "name": "Daily" },
                    { "name": "Weekly" },
                    { "name": "Biweekly" },
                    { "name": "Monthly" }
                ]
            }
        },
        "Energy Level Needed": {
            "select": {
                "options": [
                    { "name": "High", "color": "red" },
                    { "name": "Medium", "color": "yellow" },
                    { "name": "Low", "color": "green" }
                ]
            }
        },
        "Estimated Time (min)": {
            "number": {
                "format": "number"
            }
        }
    }
}

# Make the request
response = requests.post(
    "https://api.notion.com/v1/databases",
    headers=headers,
    data=json.dumps(create_db_payload)
)

# Handle Response
if response.status_code == 200:
    new_db_id = response.json().get('id')
    print(f"Success! Database created.")
    print(f"New Database ID: {new_db_id}")
    print(f"URL: {response.json().get('url')}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)