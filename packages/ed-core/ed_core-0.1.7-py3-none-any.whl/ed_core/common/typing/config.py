from typing import TypedDict


class CloudinaryConfig(TypedDict):
    cloud_name: str
    api_key: str
    api_secret: str
    env_variable: str


class Config(TypedDict):
    mongo_db_connection_string: str
    db_name: str
    rabbitmq_url: str
    rabbitmq_queue: str
    cloudinary: CloudinaryConfig


class TestMessage(TypedDict):
    title: str
