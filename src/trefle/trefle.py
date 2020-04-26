import os
from typing import List, Dict, Any
from src.log.logger import logger
from shamrock import Shamrock
from functools import lru_cache


@lru_cache(maxsize=2000)
def get_plant_info(name: str, page_size: int) -> List[Dict[str, Any]]:

    try:
        trefle_token = os.environ["TREFLE_ACCESS_TOKEN"]
        api = Shamrock(trefle_token, page_size=page_size)
    except KeyError as e:
        logger.error(
            "TREFLE_ACCESS_TOKEN environment variable not set, cannot fetch plants data"
        )
        raise e
    except Exception as e:
        logger.error(
            f"Could not create Trefle API resource due to {type(e)}, args: {e.args}"
        )
        raise e

    logger.info(f"Fetching data for plant name: {name}")

    batch = api.search(name)
    search_results = []
    for d in batch:
        plant = api.plants(d["id"])
        search_results.append(plant)

    return search_results
