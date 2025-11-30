# Johney Agentic LLM Hub 

I extensively use OpenAI, Perplexity, Gemini, and using them through the UI and not being able to share the info even with the same LLM is very frustrating. Its evolving at the moment and things are pretty fluid. 

# Milestone 0 - Cloud Run interface
If you have a use case for building a CloudRun web app using rest APIs this one is highly reusable by design. currently on hold.

# Milestone 1 - Gemini Agent sending tasks to Notion
First concrete spot I have reached is building an agent with Google's Agent Deployment Kit to send my tasks into a master notion database. Working with Notion programmatically is painful and very inflexible but the human interfaces are great to work with. 

## How to creation notion database 
./notionpy/createdb.py - uses 2022 version

## Agent code
./adk/agents/agent.py - working version 
- list_tasks
- create_task
- update_task
- delete_task 
- notion_prompt.yaml - modify to your needs as this one is very specify to my life. 

# Milestone 2 - Gemini Agent updating Google Drive artifacts 
# Milestone 3 - Centralizing prompts and responses into a Firestore database





