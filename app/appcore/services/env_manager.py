"""
    This module is responsible for managing the environment variables.
    If an environment variable is not found, an error will be raised.
    DB_NAME: database name
    DB_USER: database user
    DB_PASS: database password
    DB_HOST: database host
    DB_PORT: database port
    DEBUG: debug mode
    ALLOWED_HOSTS: allowed hosts
    SECRET_KEY: secret key
    SERVICE_TOKEN: service token used to authenticate NextJS's server side calls
    CELERY_BROKER_URL: Celery broker URL
    CELERY_RESULT_BACKEND: Celery result backend
    REDIS_CACHE_URL: Redis cache URL
    AWS_ACCESS_KEY_ID: AWS access key ID
    AWS_SECRET_ACCESS_KEY: AWS secret access key
    AWS_STORAGE_BUCKET_NAME: AWS storage bucket name
    AWS_BUCKET_URL: AWS bucket URL
    AWS_S3_ENDPOINT_URL: AWS S3 endpoint URL
    FORTY_TWO_CLIENT_ID: 42 API client ID
    FORTY_TWO_CLIENT_SECRET: 42 API client secret

    IF DEPLOYENV == "build": the environment variables will checked for errors

    Usage:
        from appcore.services.env_manager import ENVS
        ENVS.get("SECRET_KEY")
"""
import os
from typing import Any

ENV_NAMES = [
    "DEPLOYENV",  # dev | prod | build
    "DB_NAME",
    "DB_USER",
    "DB_PASS",
    "DB_HOST",
    "DB_PORT",
    "DEBUG",
    "ALLOWED_HOSTS",
    "CORS_ALLOWED_ORIGINS",
    "SECRET_KEY",
    "SERVICE_TOKEN",
    "CELERY_BROKER_URL",
    "CELERY_RESULT_BACKEND",
    "REDIS_CACHE_URL",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_STORAGE_BUCKET_NAME",
    "AWS_BUCKET_URL",
    "AWS_S3_ENDPOINT_URL",
    "FORTY_TWO_CLIENT_ID",
    "FORTY_TWO_CLIENT_SECRET",
]

ENVS: dict[str, Any] = {}
errs: list[str] = []


def convert_env(env: str, value: str) -> Any:
    """Converts the environment variables to the correct type.

    Args:
        env (str): environment variable name
        value (str): environment variable value

    Returns:
        Any: converted value
    """
    match env:
        case "DEBUG":
            return value.lower() == "true"
        case "ALLOWED_HOSTS":
            return [i for i in value.split(",") if i != ""]
        case "CORS_ALLOWED_ORIGINS":
            return [i for i in value.split(",") if i != ""]
        case "DEPLOYENV":
            if value not in ["dev", "prod"]:
                raise ValueError(
                    f'Invalid value for {env}: {value} (must be of "dev", "prod")'
                )
            return value
        case _:
            return value


if not os.environ.get("DEPLOYENV") == "build":
    for env in ENV_NAMES:
        try:
            ENVS[env] = convert_env(env, os.environ[env])
        except KeyError as e:
            errs.append(str(e).strip("'"))

    if errs:
        raise EnvironmentError(f'Envs not found: {", ".join(errs)}')
