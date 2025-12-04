"""
Check if your Milvus collection supports dynamic fields
If it does, we can add student metadata without schema changes!
"""

from pymilvus import connections, Collection
from dotenv import load_dotenv
import os
import json

load_dotenv()

print("\n[QUERY] ========== CHECKING DYNAMIC SCHEMA SUPPORT ==========\n")

# Connect to Milvus
connections.connect(
    alias="default",
    host=os.getenv('MILVUS_HOST'),
    port=int(os.getenv('MILVUS_PORT', 19530)),
    user=os.getenv('MILVUS_USERNAME'),
    password=os.getenv('MILVUS_PASSWORD'),
    secure=True
)

collection_name = os.getenv('MILVUS_COLLECTION_NAME', 'wx_pjmysyllabicollection')
print(f"[REQUEST] Collection: {collection_name}\n")

# Get collection
collection = Collection(name=collection_name)

# Get full schema description
description = collection.describe()

print("="*60)
print("FULL COLLECTION DESCRIPTION")
print("="*60)
print(json.dumps(description, indent=2, default=str))
print("="*60 + "\n")

# Check for dynamic field support
enable_dynamic = description.get('enable_dynamic_field', False)

print("[QUERY] DYNAMIC FIELD STATUS:")
print(f"   enable_dynamic_field: {enable_dynamic}\n")

if enable_dynamic:
    print("[SUCCESS] GREAT NEWS! Dynamic fields are ENABLED!")
    print("\nThis means you can add student metadata WITHOUT schema changes!")
    print("The metadata will automatically go into the $meta field.\n")
    print("Your current code will work - student_name, nuid, etc. will be")
    print("stored in $meta automatically.\n")
    print("="*60)
    print("NEXT STEP: Just use your existing watson_upload.py")
    print("="*60)
    print("The fields will be stored in $meta.student_name, $meta.nuid, etc.")
    print("You can query them like: collection.query(expr='$meta[\"nuid\"] == \"N12345678\"')")
else:
    print("[ERROR] Dynamic fields are DISABLED")
    print("\nThis means we need to either:")
    print("  1. Create a NEW collection with all fields defined upfront")
    print("  2. Store student context in a separate database (PostgreSQL/MongoDB)")
    print("  3. Use only the existing fields and store student data elsewhere\n")
    print("="*60)
    print("RECOMMENDATION: Create new collection")
    print("="*60)

print("\n[DISCONNECTED] Disconnected from Milvus\n")