import os
from huggingface_hub import hf_hub_download

TOKEN = os.getenv("HF_TOKEN")
# WARNING: Do not commit actual token to git.
REPO_ID = "facebook/sam3" # Based on search results
FILENAME = "sam3.pt"

print(f"Attempting to download {FILENAME} from {REPO_ID}...")

try:
    # Download the model to the current directory
    file_path = hf_hub_download(
        repo_id=REPO_ID,
        filename=FILENAME,
        token=TOKEN,
        local_dir="./backend" # Download to backend folder directly
    )
    print(f"Success! Model downloaded to: {file_path}")
    
except Exception as e:
    print(f"Download failed: {e}")
    # Fallback plan: Try 'ultralytics/assets' or 'ultralytics/SAM' if facebook fails?
    # But search indicated facebook/sam3. 
