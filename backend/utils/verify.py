#!/usr/bin/env python3
"""
Verify Milvus Collection Contents
Shows what's actually stored in your vector index
"""
import os
from dotenv import load_dotenv
from pymilvus import connections, Collection, utility

load_dotenv()

# Configuration
COLLECTION_NAME = "cpl_documents_v5"

# Connect to Milvus
print(f"Connecting to Milvus...")
connections.connect(
    alias="default",
    host=os.environ.get("MILVUS_HOST"),
    port=os.environ.get("MILVUS_PORT", "19530"),
    user=os.environ.get("MILVUS_USERNAME", "ibmlhapikey"),
    password=os.environ.get("MILVUS_PASSWORD") or os.environ.get("IBM_API_KEY"),
    secure=True
)
print("Connected!\n")

# Check if collection exists
if not utility.has_collection(COLLECTION_NAME):
    print(f"[ERROR] Collection '{COLLECTION_NAME}' does not exist!")
    exit(1)

# Load collection
collection = Collection(COLLECTION_NAME)
collection.load()

# Get stats
num_entities = collection.num_entities
print(f"{'='*70}")
print(f"[ICEBERG] COLLECTION: {COLLECTION_NAME}")
print(f"{'='*70}")
print(f"Total chunks stored: {num_entities}")
print()

# Query all documents to see what's there
print(f"{'='*70}")
print(f"[DOCUMENT] DOCUMENTS IN COLLECTION")
print(f"{'='*70}")

# First, let's see the schema (all fields)
print("\n[REQUEST] COLLECTION SCHEMA (all fields):")
schema = collection.schema
for field in schema.fields:
    print(f"   - {field.name}: {field.dtype}")

# Get ALL fields from the collection
all_fields = [field.name for field in schema.fields if field.name != "vector"]  # exclude vector for readability

print(f"\n[ICEBERG] QUERYING DATA WITH ALL METADATA FIELDS...")

results = collection.query(
    expr="pk != ''",
    output_fields=all_fields,
    limit=100
)

# Group by document
docs = {}
for r in results:
    doc_name = r.get('document_name', 'Unknown')
    if doc_name not in docs:
        docs[doc_name] = []
    docs[doc_name].append(r)

print(f"\nFound {len(docs)} unique documents:\n")

for doc_name, chunks in sorted(docs.items()):
    print(f"{'='*70}")
    print(f"[DOCUMENT] {doc_name}")
    print(f"{'='*70}")
    print(f"   Chunks: {len(chunks)}")
    
    # Show first chunk's FULL metadata
    if chunks:
        first = chunks[0]
        print(f"\n   [REQUEST] METADATA (from first chunk):")
        for key, value in first.items():
            if key != 'text':  # Skip text content for brevity
                print(f"      {key}: {value}")
        
        # Show text preview
        text_preview = first.get('text', '')[:150]
        print(f"\n   📝 Text preview: {text_preview}...")
    print()

# Search test
print(f"{'='*70}")
print(f"[QUERY] SEARCH TEST")
print(f"{'='*70}")

test_queries = [
    "course learning outcomes PJM 6005",
    "project management fundamentals",
    "stakeholder analysis"
]

from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models.embeddings import Embeddings

# Initialize embeddings for search
credentials = Credentials(
    api_key=os.environ.get("IBM_API_KEY"),
    url=os.environ.get("WATSONX_AI_SERVICE_URL", "https://us-south.ml.cloud.ibm.com")
)
client = APIClient(credentials)
embedding_model = Embeddings(
    model_id='ibm/slate-125m-english-rtrvr-v2',
    api_client=client
)

for query in test_queries:
    print(f"\n🔎 Query: '{query}'")
    
    # Generate embedding
    query_embedding = embedding_model.embed_query(query)
    
    # Search
    search_results = collection.search(
        data=[query_embedding],
        anns_field="vector",
        param={"metric_type": "L2", "params": {"ef": 64}},
        limit=3,
        output_fields=["document_name", "text"]
    )
    
    for i, hit in enumerate(search_results[0]):
        doc_name = hit.entity.get('document_name', 'Unknown')
        text_preview = hit.entity.get('text', '')[:200]
        print(f"\n   Result {i+1} (score: {hit.distance:.4f})")
        print(f"   Document: {doc_name}")
        print(f"   Text: {text_preview}...")

print(f"\n{'='*70}")
print(f"[SUCCESS] Verification complete!")
print(f"{'='*70}")

connections.disconnect("default")