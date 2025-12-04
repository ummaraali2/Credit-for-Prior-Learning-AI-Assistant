from ibm_watsonx_ai import APIClient, Credentials
from dotenv import load_dotenv
import os

load_dotenv()

credentials = Credentials(
    api_key=os.getenv('WATSONX_AI_APIKEY'),
    url=os.getenv('WATSONX_AI_SERVICE_URL')
)
client = APIClient(credentials)
client.set.default_project(os.getenv('WATSONX_AI_PROJECT_ID'))

print("\n[REQUEST] ========== AVAILABLE EMBEDDING MODELS IN AU-SYD ==========\n")

# Corrected method name
try:
    # Try different method names
    models = client.foundation_models.list_models(filters='function_embedding')
except:
    try:
        # Alternative API
        models = client.foundation_models.get_model_specs()
    except:
        # List all and filter
        models = client.foundation_models.get_models()

print(models)
print("\n" + "="*70)

# Also try this simpler approach
print("\n[QUERY] Trying alternative method...\n")

from ibm_watsonx_ai.foundation_models import Embeddings

# List common 768-dim models to test
test_models = [
    'intfloat/multilingual-e5-large',
    'sentence-transformers/all-mpnet-base-v2',
    'BAAI/bge-large-en-v1.5',
]

print("Testing which models work in your region:\n")

for model_id in test_models:
    try:
        test_embed = Embeddings(
            model_id=model_id,
            api_client=client
        )
        # Try to embed a test string
        result = test_embed.embed_query("test")
        print(f"[SUCCESS] {model_id} - WORKS! (dim: {len(result)})")
    except Exception as e:
        print(f"[ERROR] {model_id} - Not available")