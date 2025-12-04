# Check what's actually in your Milvus collection
from pymilvus import connections, Collection

connections.connect(
    alias="default",
    host="7d599a9a-f7be-48f5-9fd1-24d47f1b9132.ct7kqd4s0l8kkd26qgo0.lakehouse.ibmappdomain.cloud",
    port=32668,
    user="ibmlhapikey_syeda.umm@northeastern.edu",
    password="oa6updVpfRktCbXRtxMwcLhYivPg4odcB8Gb03Eu8Pdt",
    secure=True
)

collection = Collection("cpl_documents_v5")
collection.load()

# Search for John Smith
results = collection.query(
    expr='student_name == "John Smith"',
    output_fields=["nuid", "student_name", "document_name", "target_course", "request_type", "text"],
    limit=3
)

for r in results:
    print(f"NUID: {r.get('nuid')}")
    print(f"Name: {r.get('student_name')}")
    print(f"Document: {r.get('document_name')}")
    print(f"Request Type: {r.get('request_type')}")
    print(f"Target Course: {r.get('target_course')}")
    print(f"Text preview: {r.get('text', '')[:200]}...")
    print("---")

connections.disconnect("default")