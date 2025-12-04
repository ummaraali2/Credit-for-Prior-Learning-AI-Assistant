from pymilvus import connections, Collection
from dotenv import load_dotenv
import os

load_dotenv()

# Connect to Milvus
connections.connect(
    alias="default",
    host=os.getenv('MILVUS_HOST'),
    port=os.getenv('MILVUS_PORT'),
    user=os.getenv('MILVUS_USERNAME'),
    password=os.getenv('MILVUS_PASSWORD'),
    secure=True
)

collection_name = os.getenv('MILVUS_COLLECTION_NAME')
collection = Collection(name=collection_name)

# Load collection (required before querying)
collection.load()

print(f"\n[ICEBERG] Collection: {collection_name}")
print(f"Total entities: {collection.num_entities}")

# Query recent documents
results = collection.query(
    expr="document_name == 'sample_resume.pdf'",
    output_fields=["pk", "document_id", "document_name", "page", "sequence_number"],
    limit=10
)

print(f"\n[QUERY] Found {len(results)} chunks for 'sample_resume.pdf':\n")

for result in results:
    print(f"  Document ID: {result['document_id']}")
    print(f"  File: {result['document_name']}")
    print(f"  Chunk: {result['sequence_number']}, Page: {result['page']}")
    print(f"  PK: {result['pk']}")
    print()

print("[SUCCESS] Data verification complete!")