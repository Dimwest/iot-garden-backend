from os import environ
from typing import Dict
from src.log import logger


def get_env_vars() -> Dict[str, str]:

    """
    Gets connection parameters from environment variables, fails and logs and error message
    if one of the environment variables is missing.
    :return: a dictionary containing the connection information
    """

    try:

        return {
            "user": environ["POSTGRES_USER"],
            "password": environ["POSTGRES_PASSWORD"],
            "host": environ["POSTGRES_HOST"],
            "port": environ["POSTGRES_PORT"],
            "database": environ["POSTGRES_DB"],
            "twilio_account_sid": environ["TWILIO_ACCOUNT_SID"],
            "twilio_auth_token": environ["TWILIO_AUTH_TOKEN"],
            "twilio_supersim_sid": environ["TWILIO_SUPERSIM_SID"],
        }

    except KeyError as e:
        logger.error(
            f"Missing environment variable, make sure that "
            f"the following environment variables are defined: "
            f"POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, "
            f"POSTGRES_PORT, POSTGRES_DB, TWILIO_ACCOUNT_SID, "
            f"TWILIO_AUTH_TOKEN, TWILIO_SUPERSIM_SID"
        )
        raise e
