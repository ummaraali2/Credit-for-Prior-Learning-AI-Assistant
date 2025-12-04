#!/usr/bin/env python3
"""
Flush/Delete Milvus Collection
"""
import os
from dotenv import load_dotenv
from pymilvus import connections, utility

load_dotenv()

# Get credentials from environment
api_key = os.environ.get("IBM_API_KEY") or os.environ.get("WATSONX_AI_APIKEY")
host = os.environ.get("MILVUS_HOST")
port = os.environ.get("MILVUS_PORT", "19530")

# Collection to delete
COLLECTION_TO_DELETE = "cpl_documents_v5"

print(f"Connecting to Milvus at {host}:{port}...")

# Connect to Milvus
connections.connect(
    alias="default",
    host=host,
    port=port,
    user="ibmlhapikey",
    password=api_key,
    secure=True
)

print("Connected!\n")

# List all collections
print("Current collections:")
collections = utility.list_collections()
for c in collections:
    print(f"  - {c}")

print(f"\n--- Deleting: {COLLECTION_TO_DELETE} ---")

# Check if collection exists and delete
if utility.has_collection(COLLECTION_TO_DELETE):
    utility.drop_collection(COLLECTION_TO_DELETE)
    print(f"[SUCCESS] Deleted collection: {COLLECTION_TO_DELETE}")
else:
    print(f"[WARNING]  Collection '{COLLECTION_TO_DELETE}' does not exist")

# Show remaining collections
print("\nRemaining collections:")
collections = utility.list_collections()
for c in collections:
    print(f"  - {c}")

connections.disconnect("default")
print("\nDone!")