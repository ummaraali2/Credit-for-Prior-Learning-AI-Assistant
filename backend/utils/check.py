from pymilvus import connections, Collection
import os
from dotenv import load_dotenv

load_dotenv()

connections.connect(
    alias="default",
    host=os.getenv('MILVUS_HOST'),
    port=int(os.getenv('MILVUS_PORT', 32668)),
    user=os.getenv('MILVUS_USERNAME'),
    password=os.getenv('MILVUS_PASSWORD'),
    secure=True
)

collection = Collection("cpl_documents_v4")
collection.load()

# Get samples from PJM5900.pdf
results = collection.query(
    expr="document_name == 'PJM5900.pdf'",
    limit=3,
    output_fields=["pk", "text", "document_name"]
)

print("=== PJM5900.pdf Content ===")
for r in results:
    print(f"\n{r['text'][:200]}...")

connections.disconnect("default")