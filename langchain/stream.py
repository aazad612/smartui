import streamlit as st
import os
import requests
from dotenv import load_dotenv
from datetime import datetime

# LangChain / LangGraph Imports
from langchain_google_vertexai import ChatVertexAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage

# Load Env Vars
load_dotenv()

# --- CONFIG ---
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = "2ba2f5c36296813e93edc66030b6759a" # Your DB ID
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# ==========================================
# 1. DEFINE TOOLS (Wrapped with @tool)
# ==========================================

def _find_task_id(task_name: str) -> str:
    """Internal Helper: Finds a Page ID by fuzzy title match."""
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    payload = {"filter": {"property": "Task Name", "title": {"contains": task_name}}}
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        data = response.json()
        if data.get("results"):
            return data["results"][0]["id"]
        return None
    except:
        return None

@tool
def list_tasks(status_filter: str = None, limit: int = 10) -> str:
    """
    Lists tasks from Notion. 
    Args:
        status_filter: Optional. Filter by status (e.g., 'Open', 'Done').
        limit: Max number of tasks to return.
    """
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    payload = {"page_size": limit}
    if status_filter:
        payload["filter"] = {"property": "Status", "select": {"equals": status_filter}}

    res = requests.post(url, headers=HEADERS, json=payload)
    if res.status_code != 200: return "Error fetching tasks."
    
    results = res.json().get("results", [])
    if not results: return "No tasks found."
    
    out = []
    for p in results:
        props = p["properties"]
        title = props["Task Name"]["title"][0]["text"]["content"] if props["Task Name"]["title"] else "Untitled"
        status = props["Status"]["select"]["name"] if props["Status"]["select"] else "No Status"
        priority = props["Priority"]["select"]["name"] if props["Priority"]["select"] else "No Priority"
        out.append(f"- {title} [{status}] ({priority})")
    
    return "\n".join(out)

@tool
def create_task(task_name: str, category: str = "Work", priority: str = "P3 (Medium)") -> str:
    """Creates a new task in Notion."""
    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Task Name": {"title": [{"text": {"content": task_name}}]},
            "Category": {"select": {"name": category}},
            "Priority": {"select": {"name": priority}},
            "Status": {"select": {"name": "Open"}}
        }
    }
    requests.post(url, headers=HEADERS, json=payload)
    return f"Success: Created task '{task_name}'."

@tool
def update_task(task_name: str, status: str = None, priority: str = None, notes: str = None) -> str:
    """
    Updates an existing task.
    Args:
        task_name: The text to search for in the task title.
        status: New status (Open, In Progress, Done).
        priority: New priority.
        notes: Context or notes to add.
    """
    page_id = _find_task_id(task_name)
    if not page_id: return f"Error: Could not find task containing '{task_name}'."
    
    props = {}
    if status: props["Status"] = {"select": {"name": status}}
    if priority: props["Priority"] = {"select": {"name": priority}}
    if notes: props["Context / Notes"] = {"rich_text": [{"text": {"content": notes}}]}
    
    url = f"https://api.notion.com/v1/pages/{page_id}"
    requests.patch(url, headers=HEADERS, json={"properties": props})
    return f"Success: Updated '{task_name}'."

@tool
def add_database_column(column_name: str, type_description: str) -> str:
    """Adds a new column to the database schema (e.g. 'Cost' as 'number')."""
    # ... (Simplified version for brevity, reusing your logic) ...
    # You can paste your full logic here if needed
    return "Schema update logic placeholder"

# List of tools to bind to the LLM
tools = [list_tasks, create_task, update_task, add_database_column]

# ==========================================
# 2. INITIALIZE AGENT (LangGraph)
# ==========================================

# Using Vertex AI (Gemini)
# Ensure GOOGLE_CLOUD_PROJECT is in your environment or gcloud config
llm = ChatVertexAI(model="gemini-2.0-flash-exp", temperature=0)

# Create the graph (ReAct Agent)
# This automatically creates nodes for 'agent' and 'tools' and wires them up
graph = create_react_agent(llm, tools=tools)

# ==========================================
# 3. STREAMLIT UI
# ==========================================

st.set_page_config(page_title="Notion Agent", page_icon="🤖")
st.title("🤖 Notion Task Manager")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display History
for msg in st.session_state.messages:
    # We only display user and AI messages, filtering out technical ToolMessages
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage) and msg.content:
        with st.chat_message("assistant"):
            st.markdown(msg.content)

# Input Loop
if prompt := st.chat_input("What do you want to do?"):
    # 1. Show User Message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append(HumanMessage(content=prompt))

    # 2. Run Agent
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Stream events from the graph
        # We pass the entire history so the model has context
        inputs = {"messages": st.session_state.messages}
        
        # LangGraph returns a stream of events (updates to the state)
        for event in graph.stream(inputs, stream_mode="values"):
            # We are interested in the final message from the model
            message = event["messages"][-1]
            
            if isinstance(message, AIMessage) and message.content:
                full_response = message.content
                message_placeholder.markdown(full_response)

        # 3. Save Final Response to History
        if full_response:
            st.session_state.messages.append(AIMessage(content=full_response))