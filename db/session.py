# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Database session management."""

from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from common.env_readers import load_yaml_with_env
from db.models import Base

# Load .env into os.environ before loading YAMLs
load_dotenv()


def get_connection_url(db_config: dict) -> str:
    """
    Build MySQL connection URL from config.
    
    Args:
        db_config: Database configuration dictionary
        
    Returns:
        SQLAlchemy connection URL (without SSL params, those go in connect_args)
    """
    host = db_config["host"]
    port = db_config.get("port", 3306)
    database = db_config["database"]
    user = db_config["user"]
    password = db_config["password"]
    
    # Build base URL without SSL params
    url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    
    return url


def get_ssl_args(db_config: dict) -> dict:
    """
    Build SSL connection arguments for PyMySQL.
    
    Args:
        db_config: Database configuration dictionary
        
    Returns:
        Dictionary with SSL connection arguments
    """
    import ssl
    import os
    
    ssl_ca = db_config.get("ssl_ca", "")
    
    if ssl_ca and ssl_ca.strip() and os.path.exists(ssl_ca):
        # SSL with certificate verification (production)
        # Azure MySQL requires SSL
        return {
            "ssl": {
                "ca": ssl_ca,
                "check_hostname": False,  # Azure usa certificados com nomes diferentes
                "verify_mode": ssl.CERT_REQUIRED,
            }
        }
    else:
        # No SSL certificate or file not found - disable verification (development only)
        # For Azure MySQL, SSL is still used but verification is disabled
        return {
            "ssl": {
                "check_hostname": False,
                "verify_mode": ssl.CERT_NONE,
            }
        }


def create_db_engine(db_config: dict):
    """
    Create SQLAlchemy engine from config with proper SSL configuration.
    
    Args:
        db_config: Database configuration dictionary
        
    Returns:
        SQLAlchemy Engine instance
    """
    url = get_connection_url(db_config)
    
    pool_size = db_config.get("pool_size", 5)
    max_overflow = db_config.get("max_overflow", 10)
    pool_timeout = db_config.get("pool_timeout", 30)
    pool_recycle = db_config.get("pool_recycle", 3600)
    echo = db_config.get("echo", False)
    
    # Get SSL configuration
    ssl_args = get_ssl_args(db_config)
    
    engine = create_engine(
        url,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_timeout=pool_timeout,
        pool_recycle=pool_recycle,
        echo=echo,
        connect_args=ssl_args,
        
    )
    
    return engine


def init_db(db_config: dict) -> None:
    """
    Initialize database schema (create tables).
    
    Args:
        db_config: Database configuration dictionary
    """
    engine = create_db_engine(db_config)
    Base.metadata.create_all(bind=engine)


class DatabaseSession:
    """Database session factory."""
    
    def __init__(self, db_config_path: str = "configs/db.yaml"):
        """
        Initialize database session factory.
        
        Args:
            db_config_path: Path to database config YAML
        """
        self.config = load_yaml_with_env(db_config_path)
        self.engine = create_db_engine(self.config)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get database session (context manager).
        
        Yields:
            SQLAlchemy Session
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

