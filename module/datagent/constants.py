import os

# Paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS_DIR = os.path.join(os.getcwd(), "artifacts")
LOGS_DIR = os.path.join(os.getcwd(), "logs")

# Defaults
DEFAULT_SESSION_ID = "default-session"
DEFAULT_MODEL = "gpt-4-turbo"
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"

# timeouts
DEFAULT_TIMEOUT = 600 # seconds

# RAG
VECTOR_STORE_PATH = os.path.join(ARTIFACTS_DIR, "vector_store")
