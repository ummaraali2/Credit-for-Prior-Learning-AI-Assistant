"""
Create CPL Milvus Collection - FIXED VERSION
Uses L2 + HNSW to match watsonx.ai's expectations
"""

from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from dotenv import load_dotenv
import os

load_dotenv()

print("\n" + "="*70)
print("[UPLOADING] CREATING CPL COLLECTION - WATSONX.AI COMPATIBLE")
print("="*70 + "\n")

# ==================== STEP 1: CONNECT TO MILVUS ====================

print("📡 STEP 1: Connecting to Milvus...")

try:
    connections.connect(
        alias="default",
        host=os.getenv('MILVUS_HOST'),
        port=int(os.getenv('MILVUS_PORT', 32668)),
        user=os.getenv('MILVUS_USERNAME'),
        password=os.getenv('MILVUS_PASSWORD'),
        secure=True
    )
    print(f"   [SUCCESS] Connected to: {os.getenv('MILVUS_HOST')}:{os.getenv('MILVUS_PORT')}\n")
except Exception as e:
    print(f"   [ERROR] Connection failed: {str(e)}")
    exit(1)

# ==================== STEP 2: COLLECTION NAME ====================

COLLECTION_NAME = "cpl_documents_v5"  # ← New version

print(f"[REQUEST] STEP 2: Collection name: {COLLECTION_NAME}\n")

# Check if collection exists
if utility.has_collection(COLLECTION_NAME):
    print(f"[WARNING]  Collection '{COLLECTION_NAME}' already exists!")
    response = input("   Drop and recreate? (yes/no): ")
    
    if response.lower() == 'yes':
        utility.drop_collection(COLLECTION_NAME)
        print(f"   [SUCCESS] Dropped existing collection\n")
    else:
        print("   [ERROR] Aborted\n")
        connections.disconnect("default")
        exit(0)

# ==================== STEP 3: DEFINE SCHEMA ====================

print("📐 STEP 3: Defining schema...")
print("   Matching watsonx.ai's expected field types\n")

fields = [
    # PRIMARY KEY
    FieldSchema(
        name="pk",
        dtype=DataType.VARCHAR,
        is_primary=True,
        auto_id=False,
        max_length=65535  # ← Match watsonx.ai
    ),
    
    # CONTENT FIELD
    FieldSchema(
        name="text",
        dtype=DataType.VARCHAR,
        max_length=65535  # ← Match watsonx.ai
    ),
    
    # VECTOR FIELD
    FieldSchema(
        name="vector",
        dtype=DataType.FLOAT_VECTOR,
        dim=768
    ),
    
    # DOCUMENT METADATA
    FieldSchema(
        name="document_id",
        dtype=DataType.VARCHAR,
        max_length=65535  # ← Match watsonx.ai
    ),
    
    FieldSchema(
        name="document_name",
        dtype=DataType.VARCHAR,
        max_length=65535  # ← Match watsonx.ai
    ),
    
    FieldSchema(
        name="document_type",
        dtype=DataType.VARCHAR,
        max_length=500
    ),
    
    # CHUNK METADATA - Using INT64 to match watsonx.ai
    FieldSchema(
        name="page",
        dtype=DataType.INT64  # ← Changed from INT32
    ),
    
    FieldSchema(
        name="start_index",
        dtype=DataType.INT64  # ← Changed from INT32
    ),
    
    FieldSchema(
        name="sequence_number",
        dtype=DataType.INT64  # ← Changed from INT32
    ),
    
    # STUDENT CONTEXT
    FieldSchema(
        name="student_name",
        dtype=DataType.VARCHAR,
        max_length=500
    ),
    
    FieldSchema(
        name="nuid",
        dtype=DataType.VARCHAR,
        max_length=100
    ),
    
    FieldSchema(
        name="target_course",
        dtype=DataType.VARCHAR,
        max_length=500
    ),
    
    FieldSchema(
        name="request_type",
        dtype=DataType.VARCHAR,
        max_length=200
    ),
]

schema = CollectionSchema(
    fields=fields,
    description="CPL documents - watsonx.ai compatible (L2 + HNSW)",
    enable_dynamic_field=False
)

print("   [SUCCESS] Schema defined with 13 fields")
print("   [SUCCESS] Using INT64 for numeric fields (matches watsonx.ai)")
print("   [SUCCESS] Using max_length=65535 for key VARCHAR fields\n")

# ==================== STEP 4: CREATE COLLECTION ====================

print(f"🔨 STEP 4: Creating collection '{COLLECTION_NAME}'...")

collection = Collection(
    name=COLLECTION_NAME,
    schema=schema,
    using='default'
)

print(f"   [SUCCESS] Collection created!\n")

# ==================== STEP 5: CREATE INDEXES ====================

print("[QUERY] STEP 5: Creating indexes...")

# Vector index - MATCHING WATSONX.AI's SETTINGS
print("   Creating vector index (L2 + HNSW)...")
vector_index_params = {
    "metric_type": "L2",              # ← CRITICAL: Match watsonx.ai
    "index_type": "HNSW",             # ← CRITICAL: Match watsonx.ai
    "params": {"M": 8, "efConstruction": 64}
}

collection.create_index(
    field_name="vector",
    index_params=vector_index_params
)
print("      [SUCCESS] Vector index created (L2 + HNSW)\n")

# ==================== STEP 6: LOAD COLLECTION ====================

print("[MILVUS] STEP 6: Loading collection...")
collection.load()
print("   [SUCCESS] Collection loaded into memory\n")

# ==================== STEP 7: VERIFY ====================

print("[SUCCESS] STEP 7: Verifying collection...")

print(f"   Collection: {COLLECTION_NAME}")
print(f"   Total fields: {len(collection.schema.fields)}")

print("\n   [REQUEST] Index Configuration:")
for index in collection.indexes:
    print(f"      Field: {index.field_name}")
    print(f"      Params: {index.params}")

print("\n" + "="*70)
print("[SUCCESS] SUCCESS! COLLECTION CREATED WITH WATSONX.AI-COMPATIBLE SETTINGS")
print("="*70)
print("\nKey changes from v3:")
print("   • metric_type: L2 (was COSINE)")
print("   • index_type: HNSW (was IVF_FLAT)")
print("   • INT64 for numeric fields (was INT32)")
print("   • max_length: 65535 for key fields")
print("\nNext steps:")
print(f"   1. Update watson_upload.py to use '{COLLECTION_NAME}'")
print("   2. Re-upload your documents")
print("   3. Create new vector index in watsonx.ai")
print("   4. Test in Prompt Lab")
print("="*70 + "\n")

connections.disconnect("default")
print("[DISCONNECTED] Disconnected from Milvus\n")