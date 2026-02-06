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

    # 4. Import all agents to register them
    import datagent.agents.planner.agent
    import datagent.agents.greeting.agent
    import datagent.agents.data_processor.agent
    import datagent.agents.extra_topic.agent
    
    # 5. Import LLMs to register them
    import datagent.llms.openai.client
    import datagent.llms.groq.client
    
    logger.info("Bootstrap complete.")

if __name__ == "__main__":
    bootstrap_app()
