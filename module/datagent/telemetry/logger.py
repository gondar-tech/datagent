import logging
import sys
from typing import Optional

class Logger:
    _instance: Optional[logging.Logger] = None

    @classmethod
    def get_logger(cls, name: str = "datagent") -> logging.Logger:
        if cls._instance:
            return cls._instance
        
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        cls._instance = logger
        return logger
