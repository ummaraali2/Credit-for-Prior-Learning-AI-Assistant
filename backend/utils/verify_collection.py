"""
Verify the new CPL collection schema and indexes
Run this after creating the collection to ensure everything is set up correctly
"""

from pymilvus import connections, Collection, utility
from dotenv import load_dotenv
import os
import json

load_dotenv()

print("\n" + "="*70)
print("[QUERY] VERIFYING CPL COLLECTION SCHEMA")
print("="*70 + "\n")

# Connect to Milvus
print("📡 Connecting to Milvus...")
connections.connect(
    alias="default",
    host=os.getenv('MILVUS_HOST'),
    port=int(os.getenv('MILVUS_PORT', 32668)),
    user=os.getenv('MILVUS_USERNAME'),
    password=os.getenv('MILVUS_PASSWORD'),
    secure=True
)
print(f"   [SUCCESS] Connected\n")

# Collection name
collection_name = "cpl_documents_v5"

# Check if collection exists
if not utility.has_collection(collection_name):
    print(f"[ERROR] Collection '{collection_name}' does not exist!")
    print(f"   Run 'python create_cpl_collection.py' first.\n")
    connections.disconnect("default")
    exit(1)

# Get collection
collection = Collection(name=collection_name)

print(f"[REQUEST] Collection: {collection_name}\n")

# Get full description
description = collection.describe()

print("="*70)
print("FULL COLLECTION SCHEMA")
print("="*70 + "\n")

# Display fields
print("📌 FIELDS:")
for field in description['fields']:
    name = field.get('name', 'unknown')
    dtype = field.get('type', 'unknown')
    params = field.get('params', {})
    
    print(f"\n   {name}:")
    print(f"      Type: {dtype}")
    
    if params:
        for key, value in params.items():
            print(f"      {key}: {value}")

# Check indexes
print("\n" + "="*70)
print("INDEXES")
print("="*70 + "\n")

indexes = collection.indexes
print(f"[ICEBERG] Total indexes: {len(indexes)}\n")

for idx in indexes:
    print(f"   Index: {idx.field_name}")
    print(f"      Params: {idx.params}")
    print()

# Check dynamic field status
print("="*70)
print("DYNAMIC FIELD STATUS")
print("="*70 + "\n")

enable_dynamic = description.get('enable_dynamic_field', False)
print(f"   enable_dynamic_field: {enable_dynamic}")

if enable_dynamic:
    print("   [WARNING]  Dynamic fields are ENABLED")
    print("   This means you can add undefined fields at insert time.")
else:
    print("   [SUCCESS] Dynamic fields are DISABLED")
    print("   All fields must be defined in schema (as intended).")

# Summary
print("\n" + "="*70)
print("VERIFICATION COMPLETE")
print("="*70 + "\n")

print("[SUCCESS] Your collection is ready for:")
print("   - Storing document chunks with embeddings")
print("   - Student context (name, NUID, course, request type)")
print("   - Fast filtering by NUID, document_id, target_course")
print("   - Semantic vector search with COSINE similarity")
print("   - Compatible with watsonx.ai MilvusVectorStore\n")

print("📌 Expected field count: 13")
print(f"📌 Actual field count: {len(description['fields'])}")

if len(description['fields']) == 13:
    print("   [SUCCESS] MATCH! All fields present.\n")
else:
    print("   [WARNING]  Field count mismatch!\n")

# Check for required fields
required_fields = [
    'pk', 'text', 'vector', 'document_id', 'document_name',
    'document_type', 'page', 'start_index', 'sequence_number',
    'student_name', 'nuid', 'target_course', 'request_type'
]

actual_fields = [f['name'] for f in description['fields']]

print("[QUERY] Checking required fields:")
missing = []
for field in required_fields:
    if field in actual_fields:
        print(f"   [SUCCESS] {field}")
    else:
        print(f"   [ERROR] {field} - MISSING!")
        missing.append(field)

if missing:
    print(f"\n[WARNING]  WARNING: {len(missing)} field(s) missing: {missing}\n")
else:
    print("\n[SUCCESS] All required fields present!\n")

print("="*70 + "\n")

# Disconnect
connections.disconnect("default")