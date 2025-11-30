# verify_datasource.py
import os
import json
import requests

DATABASE_ID = "49981d1a-216b-4c61-a40d-93680dfce770" 

BASE_URL = "https://api.notion.com/v1"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2025-09-03",  # 👈 new version
}

# 1) Retrieve database container – just to see its data_sources
db_resp = requests.get(f"{BASE_URL}/databases/{DATABASE_ID}", headers=HEADERS)
db_resp.raise_for_status()
db = db_resp.json()

print("=== DATABASE INFO ===")
print("ID:  ", db["id"])
print("URL: ", db.get("url"))
print("Data sources:", db.get("data_sources", []))

if not db.get("data_sources"):
    raise SystemExit("No data_sources found on database – nothing to inspect.")

# take the first data source for now
ds_id = db["data_sources"][0]["id"]

# 2) Retrieve the data source object to see the schema (properties)
ds_resp = requests.get(f"{BASE_URL}/data_sources/{ds_id}", headers=HEADERS)
ds_resp.raise_for_status()
ds = ds_resp.json()

print("\n=== DATA SOURCE INFO ===")
print("ID:  ", ds["id"])
print("Title:", "".join(t["text"]["content"] for t in ds.get("title", [])))

print("\n=== PROPERTIES ===")
for name, prop in ds["properties"].items():
    print(f"- {name}: type={prop['type']}")
