import os
import logging
from .settings import settings
from .constants import ARTIFACTS_DIR, LOGS_DIR
from .db.base import init_db

def bootstrap_app():
    """Initializes the application environment."""
    
    # 1. Create directories
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    # 2. Setup Logging
    logging.basicConfig(
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(LOGS_DIR, "datagent.log")),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger("datagent.bootstrap")
    logger.info(f"Bootstrapping Datagent in {settings.ENV} mode")
    
    # 3. Initialize Database
    try:
        init_db(settings.DATABASE_URL)
        logger.info("Database initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        
    logger.info("Bootstrap complete.")

if __name__ == "__main__":
    bootstrap_app()
