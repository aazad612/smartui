# graph.py
from __future__ import annotations

from typing import Annotated, Literal, TypedDict

from langgraph.graph import StateGraph, END
from langgraph.types import StreamEvent
from langchain_openai import ChatOpenAI

from firestore_store import create_task as fs_create_task, list_tasks as fs_list_tasks


# ---------- State definition ----------

class AgentState(TypedDict, total=False):
    messages: list[dict]  # basic chat history
    last_tool_result: str


# ---------- LLM node ----------

llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.3)

async def llm_node(state: AgentState) -> AgentState:
    """
    Simple node: ask the model what to do next.
    We’ll let it decide whether to call tools via a structured prompt later.
    For now, just echo + keep basic history.
    """
    messages = state.get("messages", [])
    # Very dumb right now; we’ll beef this up
    user_msg = messages[-1]["content"] if messages else "Hello"
    resp = await llm.ainvoke([{"role": "user", "content": user_msg}])
    messages.append({"role": "assistant", "content": resp.content})
    return {"messages": messages}


# ---------- Tool nodes ----------

async def tool_create_task(state: AgentState) -> AgentState:
    """
    For now, we’ll hard-code extracting everything from the last user message.
    Later: proper parsing / tool-calling.
    """
    messages = state.get("messages", [])
    user_msg = messages[-1]["content"] if messages else ""
    # Dumb heuristic: title is the entire user message
    task_id = fs_create_task(title=user_msg, status="open", priority="P2")
    result = f"Created task '{user_msg}' with id {task_id}"
    messages.append({"role": "assistant", "content": result})
    return {"messages": messages, "last_tool_result": result}


async def tool_list_open_tasks(state: AgentState) -> AgentState:
    tasks = fs_list_tasks(status="open", limit=20)
    if not tasks:
        msg = "No open tasks found."
    else:
        lines = [
            f"- [{t['id']}] {t['title']} (priority={t.get('priority','?')})"
            for t in tasks
        ]
        msg = "Here are your open tasks:\n" + "\n".join(lines)
    messages = state.get("messages", [])
    messages.append({"role": "assistant", "content": msg})
    return {"messages": messages, "last_tool_result": msg}


# ---------- Graph wiring ----------

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("llm", llm_node)
    graph.add_node("create_task", tool_create_task)
    graph.add_node("list_open_tasks", tool_list_open_tasks)

    # For now: start at LLM, then END.
    # We’ll add real routing / tool-calling logic later.
    graph.set_entry_point("llm")
    graph.add_edge("llm", END)

    return graph.compile()


if __name__ == "__main__":
    import asyncio

    async def demo():
        app = build_graph()
        # manually drive it once for testing
        state: AgentState = {"messages": [{"role": "user", "content": "Schedule a call with Om"}]}
        async for event in app.astream(state, stream_mode="updates"):
            if isinstance(event, dict) and event.get("messages"):
                last = event["messages"][-1]
                print("ASSISTANT:", last["content"])

    asyncio.run(demo())
