from notion_client import Client
import os
import json

# --- Config ---
DATABASE_ID = "49981d1a-216b-4c61-a40d-93680dfce770"  # or the dashless version

# verify_legacy.py
import os
from notion_client import Client

DATABASE_ID = "49981d1a-216b-4c61-a40d-93680dfce770"  # <- your DB id

notion = Client(
    auth=NOTION_TOKEN,
    notion_version="2022-06-28",  # 👈 IMPORTANT
)

db = notion.databases.retrieve(database_id=DATABASE_ID)

print("=== DATABASE INFO ===")
title_text = "".join(t["plain_text"] for t in db.get("title", []))
print("Name:", title_text)
print("ID:  ", db["id"])
print("URL: ", db["url"])

print("\n=== PARENT INFO ===")
print(db["parent"])

print("\n=== PROPERTIES ===")
for prop_name, prop in db["properties"].items():
    print(f"- {prop_name}: type={prop['type']}")
