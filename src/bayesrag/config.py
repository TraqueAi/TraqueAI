from pathlib import Path
import os
from dotenv import load_dotenv
import uuid
load_dotenv()

DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://localhost:1234/v1")
OPENAI_API_KEY = "lm-studio"
QDRANT_HOST = os.getenv("QDRANT_HOST", "http://localhost:6333")
ID=uuid.uuid4()
# QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", f"law_doc-{ID}")

REPLAY_TOPIC = f"USER_TOPIC-{ID}"
QDRANT_COLLECTION=f"law_doc-{ID}"


# IPFS Config

IPFS_RETRY_LIMIT = 3
IPFS_RETRY_DELAY = 5

## Directory for IPFS
directory_path = f"./qdrant_data/collections/global_data"
zip_file_path = "./qdrant_data_backup.zip"

download_path = "./zipdownloaded_files/qdrant_data_backup.zip"
extract_to_path = "./qdrant_data/collections/global_data"