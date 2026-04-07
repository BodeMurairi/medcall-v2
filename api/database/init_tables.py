#!/usr/bin/env python3

from .base import Base
from .create_session import engine

from models import database_models

def create_tables():
    print("Creating database tables...")
    print("Registered tables:", Base.metadata.tables.keys())
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    create_tables()
