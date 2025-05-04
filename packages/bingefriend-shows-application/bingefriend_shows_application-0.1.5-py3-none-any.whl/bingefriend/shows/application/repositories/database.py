"""Database connection for Azure SQL Database."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from bingefriend.shows.application import config

SQLALCHEMY_DATABASE_URL = config.SQLALCHEMY_CONNECTION_STRING

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("AZURE_SQL_CONNECTION_STRING is not set in the configuration.")

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
