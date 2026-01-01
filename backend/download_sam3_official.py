import os
import requests
from tqdm import tqdm

# URL from official docs
# https://huggingface.co/facebook/sam3/resolve/main/sam3.pt?download=true
MODEL_URL = "https://huggingface.co/facebook/sam3/resolve/main/sam3.pt"
TOKEN = os.getenv("HF_TOKEN") # Set this in your environment or .env file
OUTPUT_FILE = "backend/sam3.pt"

def download_file(url, token, dest_path):
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"Starting download from {url}...")
    response = requests.get(url, headers=headers, stream=True)
    
    if response.status_code == 200:
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024 # 1 Kibibyte
        t = tqdm(total=total_size, unit='iB', unit_scale=True)
        
        with open(dest_path, 'wb') as file:
            for data in response.iter_content(block_size):
                t.update(len(data))
                file.write(data)
        t.close()
        print(f"Download complete: {dest_path}")
    else:
        print(f"Download failed with status: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    download_file(MODEL_URL, TOKEN, OUTPUT_FILE)
