
# Optional: let model be overridden by env var, otherwise default.
# This keeps you from hardcoding gemini-3 / whatever every time.
# MODEL_NAME = os.getenv("ADK_MODEL_NAME", "gemini-2.5-pro")




PARENT_PAGE_ID = "2ba2f5c3629680c4895bc1e6a9436c4a"  # the page where DB should live
DATABASE_ID = "2ba2f5c36296813e93edc66030b6759a"

import asyncio, yaml
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# --- Configuration ---
NOTION_TOKEN = os.getenv("NOTION_TOKEN") # <--- Put your token here
# DATABASE_ID = "YOUR_DATABASE_ID"   # <--- Put your DB ID here
# We define this once to ensure it matches everywhere
APP_NAME = "notion_task_manager" 

from pathlib import Path
SCRIPT_DIR = Path(__file__).resolve().parent

# 1. Load Env Vars
load_dotenv()

# --- Configuration ---
APP_NAME = "notion_task_manager"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# --- DEBUG TOOLS (With Logging) ---

def find_task_id(task_name: str) -> str:
    print(f"  [TOOL DEBUG] 🔍 Searching for task containing: '{task_name}'...") 
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    
    # FIX 1: Changed 'equals' to 'contains' for fuzzier matching
    payload = {
        "filter": {
            "property": "Task Name",
            "title": {
                "contains": task_name 
            }
        }
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        if response.status_code != 200:
            print(f"  [TOOL ERROR] Search Failed: {response.text}")
            return None
            
        data = response.json()
        if data.get("results"):
            found_title = data["results"][0]["properties"]["Task Name"]["title"][0]["text"]["content"]
            print(f"  [TOOL DEBUG] ✅ Found match: '{found_title}'")
            return data["results"][0]["id"]
            
        print(f"  [TOOL DEBUG] ❌ No task found containing '{task_name}'")
        return None
    except Exception as e:
        print(f"  [TOOL EXCEPTION] {e}")
        return None
    

def create_task(task_name: str, category: str = "Work", priority: str = "P3 (Medium)") -> str:
    print(f"  [TOOL DEBUG] 🟢 create_task triggered! Args: name='{task_name}', cat='{category}'")
    
    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Task Name": {"title": [{"text": {"content": task_name}}]},
            "Category": {"select": {"name": category}},
            "Priority": {"select": {"name": priority}},
            "Status": {"select": {"name": "Open"}},
            "Created / Logged At": {"date": {"start": datetime.now().isoformat()}}
        }
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        print(f"  [TOOL DEBUG] Notion API Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"  [TOOL DEBUG] Success! Created.")
            return f"Success: Created task '{task_name}'."
        else:
            print(f"  [TOOL ERROR] Notion Response: {response.text}")
            return f"Error creating task: {response.text}"
            
    except Exception as e:
        print(f"  [TOOL EXCEPTION] {e}")
        return f"Exception: {e}"

def update_task(
    task_name: str,
    status: str = None,
    priority: str = None,
    category: str = None,
    sub_category: list[str] = None,   # Multi-select (e.g. ["Dataflow", "CR"])
    tags: list[str] = None,           # Multi-select (e.g. ["Zander", "Health"])
    due_date: str = None,             # ISO Date string (e.g. "2025-12-01")
    location: str = None,             # Select (e.g. "Kitchen")
    energy_level: str = None,         # Select (e.g. "High", "Low")
    recurrence: str = None,           # Select (e.g. "Weekly")
    estimated_time: int = None,       # Number
    notes: str = None                 # Rich Text
) -> str:
    """
    Updates an existing task in Notion.
    
    Args:
        task_name: The name of the task to find.
        status: New status (Open, In Progress, Done, etc).
        priority: New priority (P1 (Critical), P2 (High), etc).
        category: New category (Work, Home, etc).
        sub_category: List of sub-categories.
        tags: List of tags/people involved.
        due_date: Due date in YYYY-MM-DD format.
        location: Location/Room (Kitchen, Office, etc).
        energy_level: Energy needed (High, Medium, Low).
        recurrence: Repetition (Daily, Weekly, etc).
        estimated_time: Estimated minutes (e.g. 15, 60).
        notes: Text for Context/Notes.
    """
    print(f"  [TOOL DEBUG] update_task triggered for '{task_name}'...")
    
    # 1. Find the Page ID
    page_id = find_task_id(task_name)
    if not page_id:
        return f"Error: Could not find a task named '{task_name}'."

    # 2. Build the Payload Dynamically
    properties = {}
    
    # --- Select Fields ---
    if status:
        properties["Status"] = {"select": {"name": status}}
        if status == "Done":
             properties["Completed At"] = {"date": {"start": datetime.now().isoformat()}}
    if priority:
        properties["Priority"] = {"select": {"name": priority}}
    if category:
        properties["Category"] = {"select": {"name": category}}
    if location:
        properties["Location / Room"] = {"select": {"name": location}}
    if energy_level:
        properties["Energy Level Needed"] = {"select": {"name": energy_level}}
    if recurrence:
        properties["Recurrence"] = {"select": {"name": recurrence}}

    # --- Multi-Select Fields (Requires transforming list of strings to list of objects) ---
    if sub_category:
        # Transform ["A", "B"] -> [{"name": "A"}, {"name": "B"}]
        options = [{"name": item} for item in sub_category]
        properties["Sub-Category"] = {"multi_select": options}
        
    if tags:
        options = [{"name": item} for item in tags]
        properties["Tags"] = {"multi_select": options}

    # --- Date & Numbers ---
    if due_date:
        properties["Due Date"] = {"date": {"start": due_date}}
    
    if estimated_time is not None:
        properties["Estimated Time (min)"] = {"number": estimated_time}

    # --- Text ---
    if notes:
        properties["Context / Notes"] = {"rich_text": [{"text": {"content": notes}}]}

    # Check if we actually have anything to update
    if not properties:
        return "Error: No update parameters provided."

    # 3. Send Request
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {"properties": properties}
    
    try:
        response = requests.patch(url, headers=HEADERS, json=payload)
        if response.status_code == 200:
            updates_made = ", ".join(properties.keys())
            print(f"  [TOOL DEBUG] Successfully updated: {updates_made}")
            return f"Success: Updated {updates_made} for task '{task_name}'."
        else:
            return f"Error updating task: {response.text}"
    except Exception as e:
        return f"Exception: {e}"

def delete_task(task_name: str) -> str:
    print(f"  [TOOL DEBUG] delete_task triggered for '{task_name}'...")
    page_id = find_task_id(task_name)
    if not page_id:
        return f"Error: Could not find task '{task_name}'."
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {"archived": True}
    response = requests.patch(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return f"Success: Deleted task '{task_name}'."
    return f"Error: {response.text}"

def list_tasks(
    status: str = None, 
    priority: str = None, 
    category: str = None, 
    search_text: str = None,
    sort_by: str = "last_edited_time", 
    limit: int = 20
) -> str:
    """
    Powerful search tool to list and filter tasks.
    
    Args:
        status: Filter by exact status (e.g., "Open", "Done").
        priority: Filter by exact priority (e.g., "P1 (Critical)").
        category: Filter by category (e.g., "Work", "Home").
        search_text: Filter by a keyword in the Title.
        sort_by: How to sort results. Options: "newest", "oldest", "due_date_asc", "priority", "last_edited_time".
        limit: Max results (default 20).
    """
    print(f"  [TOOL DEBUG] 📋 list_tasks triggered. Filters: Status={status}, Cat={category}, Sort={sort_by}...")
    
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    
    # 1. Build Dynamic Filters
    conditions = []
    
    if status:
        conditions.append({"property": "Status", "select": {"equals": status}})
    if priority:
        conditions.append({"property": "Priority", "select": {"equals": priority}})
    if category:
        conditions.append({"property": "Category", "select": {"equals": category}})
    if search_text:
        conditions.append({"property": "Task Name", "title": {"contains": search_text}})

    payload = {"page_size": limit}
    
    # If multiple filters, use "and"; if single, use directly; if none, no filter.
    if len(conditions) > 1:
        payload["filter"] = {"and": conditions}
    elif len(conditions) == 1:
        payload["filter"] = conditions[0]

    # 2. Build Sorting
    # Maps user-friendly sort names to Notion API structure
    sort_options = {
        "newest": [{"timestamp": "created_time", "direction": "descending"}],
        "oldest": [{"timestamp": "created_time", "direction": "ascending"}],
        "due_date_asc": [{"property": "Due Date", "direction": "ascending"}],
        "priority": [{"property": "Priority", "direction": "ascending"}], # P1 comes before P2 alphabetically
        "last_edited_time": [{"timestamp": "last_edited_time", "direction": "descending"}]
    }
    
    payload["sorts"] = sort_options.get(sort_by, sort_options["last_edited_time"])

    # 3. Execute
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        if response.status_code != 200:
            return f"Error listing tasks: {response.text}"
            
        data = response.json()
        results = data.get("results", [])
        
        if not results:
            return "No tasks found matching your criteria."

        # 4. Format Output for the Agent
        # We construct a readable string so the Agent can "see" the tasks.
        formatted_list = []
        for page in results:
            props = page["properties"]
            
            # Extract fields safely (Notion API structure is deep)
            title = props["Task Name"]["title"][0]["text"]["content"] if props["Task Name"]["title"] else "Untitled"
            
            p_status = props["Status"]["select"]["name"] if props["Status"]["select"] else "No Status"
            p_priority = props["Priority"]["select"]["name"] if props["Priority"]["select"] else "No Priority"
            p_category = props["Category"]["select"]["name"] if props["Category"]["select"] else "No Cat"
            
            # Optional: Get Due Date if it exists
            due_str = ""
            if props.get("Due Date") and props["Due Date"]["date"]:
                due_str = f" (Due: {props['Due Date']['date']['start']})"

            formatted_list.append(f"• {title} | {p_status} | {p_priority} | {p_category}{due_str}")

        return f"Found {len(formatted_list)} tasks:\n" + "\n".join(formatted_list)

    except Exception as e:
        return f"Exception in list_tasks: {e}"
    
# --- Agent Definition ---
MODEL_NAME = os.getenv("ADK_MODEL_NAME", "gemini-2.0-flash-exp") # Use a model known for good tool calling


SCRIPT_DIR = Path(__file__).resolve().parent
PROMPT_PATH = SCRIPT_DIR / "notion_prompt.yaml"

# 2. Robust Loader
def load_prompt_from_file(filepath):
    print(f"📂 Loading prompt from: {filepath}")
    default_instruction = "You are a helpful Notion assistant."
    
    try:
        with open(filepath, "r") as f:
            data = yaml.safe_load(f)
            
            # Handle empty file case
            if not data:
                print("⚠️ YAML file is empty. Using default.")
                return default_instruction
                
            # Try to fetch keys, fallback to default if missing
            instruction = data.get("instruction") or data.get("system_prompt")
            
            if instruction:
                return instruction
            else:
                print("⚠️ Keys 'instruction' or 'system_prompt' not found in YAML. Using default.")
                return default_instruction

    except FileNotFoundError:
        print(f"❌ File not found at {filepath}. Using default.")
        return default_instruction
    except Exception as e:
        print(f"❌ Error reading YAML: {e}. Using default.")
        return default_instruction

# 3. Load it
system_instruction = load_prompt_from_file(PROMPT_PATH)



root_agent = Agent(
    name="notion_agent",
    model=MODEL_NAME,
    description="Agent that can organize my Notion tasks.",
    instruction=system_instruction,
    tools=[create_task, update_task, delete_task, list_tasks]
)

    
# --- VERBOSE EXECUTION LOOP ---
async def main():
    print("--- Starting Debug Session ---")
    session_service = InMemorySessionService()

    runner = Runner(
        agent=root_agent, 
        session_service=session_service,
        app_name=APP_NAME
    )

    user_id = "johney"
    session = await session_service.create_session(app_name=APP_NAME, user_id=user_id)

    user_input = "can you update category and subcategory for the tasks in the database"
    print(f"👤 User: {user_input}")

    # Run loop
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=user_input)])
    ):
        # VERBOSE INSPECTION OF EVERY EVENT
        if hasattr(event, 'candidates') and event.candidates:
            for candidate in event.candidates:
                for part in candidate.content.parts:
                    if part.function_call:
                        print(f"🤖 [AGENT DECISION] Calling Tool: {part.function_call.name}")
                        print(f"    Args: {part.function_call.args}")
                    elif part.text:
                        print(f"🤖 [AGENT SAYS] {part.text}")
        
        # If the runner returns a tool response event (output from your function)
        if hasattr(event, 'tool_response'):
             print(f"⚙️ [SYSTEM] Tool Execution Finished. Output: {event.tool_response}")

if __name__ == "__main__":
    
    asyncio.run(main())