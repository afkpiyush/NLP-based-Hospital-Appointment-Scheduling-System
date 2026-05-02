"""
Database Connection Manager
Supports MongoDB and PostgreSQL
"""
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig:
    """Database configuration settings"""
    
    DB_TYPE = os.getenv("DATABASE_TYPE", "mongodb")  # mongodb or postgresql
    
    # MongoDB settings
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "healthcare_assistant")
    
    # PostgreSQL settings
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "healthcare_assistant")
    
    POSTGRES_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"


class MongoDBClient:
    """MongoDB connection manager"""
    
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            from pymongo import MongoClient
            self._client = MongoClient(DatabaseConfig.MONGODB_URL)
    
    def get_database(self):
        """Get MongoDB database instance"""
        return self._client[DatabaseConfig.MONGODB_DB_NAME]
    
    def get_collection(self, collection_name: str):
        """Get specific collection"""
        db = self.get_database()
        return db[collection_name]
    
    def close(self):
        """Close connection"""
        if self._client:
            self._client.close()
            self._client = None


class PostgreSQLClient:
    """PostgreSQL connection manager"""
    
    _instance = None
    _engine = None
    _session = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._engine is None:
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            
            self._engine = create_engine(DatabaseConfig.POSTGRES_URL)
            self._session = sessionmaker(autocommit=False, autoflush=False, bind=self._engine)
    
    def get_engine(self):
        """Get SQLAlchemy engine"""
        return self._engine
    
    def get_session(self):
        """Get database session"""
        return self._session()
    
    def close(self):
        """Close connection"""
        if self._engine:
            self._engine.dispose()
            self._engine = None


def get_db_client():
    """Get appropriate database client based on configuration"""
    if DatabaseConfig.DB_TYPE == "mongodb":
        return MongoDBClient()
    elif DatabaseConfig.DB_TYPE == "postgresql":
        return PostgreSQLClient()
    else:
        raise ValueError(f"Unsupported database type: {DatabaseConfig.DB_TYPE}")


def get_db_collection(collection_name: str):
    """Get MongoDB collection (helper function)"""
    if DatabaseConfig.DB_TYPE != "mongodb":
        raise ValueError("This function only works with MongoDB")
    client = MongoDBClient()
    return client.get_collection(collection_name)


def get_db_session():
    """Get PostgreSQL session (helper function)"""
    if DatabaseConfig.DB_TYPE != "postgresql":
        raise ValueError("This function only works with PostgreSQL")
    client = PostgreSQLClient()
    return client.get_session()
