from enum import StrEnum
from typing import TypedDict


class Environment(StrEnum):
    TEST = "test"
    DEV = "development"
    STAGING = "staging"
    PROD = "prod"


class Config(TypedDict):
    mongo_db_connection_string: str
    db_name: str
    rabbitmq_url: str
    rabbitmq_queue: str
    jwt_secret: str
    jwt_algorithm: str
    password_scheme: str
    env: Environment


class TestMessage(TypedDict):
    title: str
