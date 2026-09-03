import os

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

_client = None


def get_database():
    global _client

    if _client is None:
        mongodb_uri = os.getenv("MONGODB_URI")
        database_name = os.getenv("DATABASE_NAME")

        if not mongodb_uri:
            raise RuntimeError("MONGODB_URI is not configured")

        if not database_name:
            raise RuntimeError("DATABASE_NAME is not configured")

        _client = MongoClient(mongodb_uri)

        # Verify the connection
        _client.admin.command("ping")

    return _client[database_name]


def get_prompts_collection():
    return get_database()["prompts"]


def get_history_collection():
    return get_database()["history"]


def close_database():
    global _client

    if _client is not None:
        _client.close()
        _client = None