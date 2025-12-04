from pymilvus import connections, Collection, utility
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

collection = Collection("cpl_documents_v3")

# Check load state
load_state = utility.load_state("cpl_documents_v3")
print(f"Collection load state: {load_state}")

# Load the collection
print("Loading collection...")
collection.load()
print("[SUCCESS] Collection loaded!")

# Verify
load_state = utility.load_state("cpl_documents_v3")
print(f"Collection load state after: {load_state}")

connections.disconnect("default")