from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from .models.base import Base

class DBManager:
    def __init__(self, connection_string: str = "sqlite:///datagent.db"):
        self.engine = create_engine(connection_string)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def init_db(self):
        Base.metadata.create_all(bind=self.engine)

    def get_session(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

# Singleton instance
db_manager = DBManager()

def init_db(connection_string: str = None):
    # If connection string provided, we might want to re-init manager, 
    # but for simplicity we just use the default or current one.
    db_manager.init_db()
