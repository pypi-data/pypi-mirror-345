import os
import uuid

from dotenv import load_dotenv

from ed_auth.common.typing.config import Config, Environment


def get_new_id() -> uuid.UUID:
    return uuid.uuid4()


def get_config() -> Config:
    load_dotenv()

    return {
        "mongo_db_connection_string": os.getenv("CONNECTION_STRING") or "",
        "db_name": os.getenv("DB_NAME") or "",
        "rabbitmq_url": os.getenv("RABBITMQ_URL") or "",
        "rabbitmq_queue": os.getenv("RABBITMQ_QUEUE") or "",
        "jwt_secret": os.getenv("JWT_SECRET") or "",
        "jwt_algorithm": os.getenv("JWT_ALGORITHM") or "",
        "password_scheme": os.getenv("PASSWORD_SCHEME") or "",
        "env": Environment.PROD if os.getenv("ENV") == "prod" else Environment.DEV,
    }
