from twilio.rest import Client
from typing import Dict


def activate_watering(
    twilio_account_sid: str,
    twilio_auth_token: str,
    twilio_sim_sid: str,
    quantity_ml: int,
) -> Dict[str, str]:

    """
    Sends a watering command on a given SIM

    :param twilio_account_sid: Twilio account SID from env vars
    :param twilio_auth_token: Twilio API authentication token
    :param twilio_sim_sid: Twilio SuperSIM SID from env vars
    :param quantity_ml: water quantity to append to the command string

    :return: SuperSIM API details
    """

    client = Client(twilio_account_sid, twilio_auth_token)

    command_str = f"WATER_{quantity_ml}"

    command = client.supersim.commands.create(sim=twilio_sim_sid, command=command_str)

    return {
        "status": command.status,
        "date_created": command.date_created,
        "command": command_str,
    }
