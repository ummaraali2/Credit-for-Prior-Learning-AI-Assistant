from pymilvus import connections, Collection
from dotenv import load_dotenv
import os
import json

load_dotenv()

print("\n[QUERY] ========== INSPECTING MILVUS SCHEMA ==========\n")

# Connect to Milvus (using watsonx.data credentials)
connections.connect(
    alias="default",
    host=os.getenv('MILVUS_HOST'),
    port=os.getenv('MILVUS_PORT'),
    user=os.getenv('MILVUS_USERNAME'),
    password=os.getenv('MILVUS_PASSWORD'),
    secure=True
)

collection_name = os.getenv('MILVUS_COLLECTION_NAME')
print(f"[REQUEST] Collection: {collection_name}\n")

# Get collection
collection = Collection(name=collection_name)

# Describe the collection
description = collection.describe()

print("="*60)
print("FULL COLLECTION SCHEMA")
print("="*60)
print(json.dumps(description, indent=2))
print("="*60)

print("\n[ICEBERG] FIELD DETAILS:\n")

for field in description['fields']:
    field_name = field.get('name')
    field_type = field.get('type')
    is_primary = field.get('is_primary', False)
    auto_id = field.get('auto_id', False)
    
    print(f"Field: {field_name}")
    print(f"  Type: {field_type}")
    print(f"  Primary: {is_primary}")
    print(f"  Auto ID: {auto_id}")
    
    if 'params' in field and field['params']:
        print(f"  Params: {field['params']}")
    
    print()

print("\n[SUCCESS] REQUIRED FIELDS FOR INSERTION:\n")

required_fields = []
for field in description['fields']:
    if field.get('auto_id', False):
        print(f"  ⚪ {field['name']} (auto-generated, SKIP)")
        continue
    
    required_fields.append(field['name'])
    print(f"  [SUCCESS] {field['name']} (type: {field['type']}) - MUST INCLUDE")

print(f"\n📝 Total required fields: {len(required_fields)}")
print(f"\n🔑 Fields to include in metadata: {required_fields}")