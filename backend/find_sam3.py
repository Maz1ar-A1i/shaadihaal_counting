from huggingface_hub import HfApi

TOKEN = os.getenv("HF_TOKEN")
api = HfApi(token=TOKEN)

print("Searching for SAM models on Hugging Face...")
try:
    # Search for models with 'sam' and 'ultralytics' or 'meta'
    models = api.list_models(search="sam", limit=20, sort="usage")
    for m in models:
        print(f"Found: {m.modelId}")
        
    print("-" * 20)
    print("Checking specific repos for 'sam 3'...")
    # Try to find 'sams'
    models_sam3 = api.list_models(search="sam 3", limit=10)
    for m in models_sam3:
        print(f"Found SAM3 candidate: {m.modelId}")

except Exception as e:
    print(f"Search failed: {e}")
