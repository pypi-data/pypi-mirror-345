from typing import Dict, Any
from pydantic import BaseModel

class DatabaseConfig(BaseModel):
    default: str = "mysql"
    connections: Dict[str, Dict[str, Any]] = {
        "mysql": {
            "driver": "mysql",
            "host": "localhost",
            "port": 3306,
            "database": "masonite",
            "username": "root",
            "password": "",
            "charset": "utf8mb4",
            "collation": "utf8mb4_unicode_ci",
            "prefix": "",
            "strict": True,
            "engine": None,
        }
    }
    migrations: str = "migrations"
    seeds: str = "seeds"

# Default configuration
DATABASE = DatabaseConfig() 