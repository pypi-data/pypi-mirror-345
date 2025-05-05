import json
import os
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
import aiohttp
from bs4 import BeautifulSoup
import urllib

from dhisana.utils.assistant_tool_tag import assistant_tool
from dhisana.utils.cache_output_tools import cache_output, retrieve_output
from dhisana.utils.web_download_parse_tools import fetch_html_content

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_serp_api_access_token(tool_config: Optional[List[Dict]] = None) -> str:
    """
    Retrieves the SERPAPI_KEY access token from the provided tool configuration.

    Args:
        tool_config (list): A list of dictionaries containing the tool configuration. 
                            Each dictionary should have a "name" key and a "configuration" key,
                            where "configuration" is a list of dictionaries containing "name" and "value" keys.

    Returns:
        str: The SERPAPI_KEY access token.

    Raises:
        ValueError: If the access token is not found in the tool configuration or environment variable.
    """
    logger.info("Entering get_serp_api_access_token")
    SERPAPI_KEY = None

    if tool_config:
        logger.debug(f"Tool config provided: {tool_config}")
        serpapi_config = next(
            (item for item in tool_config if item.get("name") == "serpapi"), None
        )
        if serpapi_config:
            config_map = {
                item["name"]: item["value"]
                for item in serpapi_config.get("configuration", [])
                if item
            }
            SERPAPI_KEY = config_map.get("apiKey")
        else:
            logger.warning("No 'serpapi' config item found in tool_config.")
    else:
        logger.debug("No tool_config provided or it's None.")

    SERPAPI_KEY = SERPAPI_KEY or os.getenv("SERPAPI_KEY")
    if not SERPAPI_KEY:
        logger.error("SERPAPI_KEY not found in configuration or environment.")
        raise ValueError("SERPAPI_KEY access token not found in tool_config or environment variable")

    logger.info("Retrieved SERPAPI_KEY successfully.")
    return SERPAPI_KEY


@assistant_tool
async def search_google_serpai(
    query: str,
    number_of_results: int = 10,
    offset: int = 0,  
    tool_config: Optional[List[Dict]] = None,
    as_oq: Optional[str] = None  # <-- NEW PARAM for optional keywords
) -> List[str]:
    """
    Search Google using SERP API, supporting pagination and an explicit 'offset'
    parameter to start from a specific result index. 
    Now also supports 'as_oq' for optional query terms in SERP API.
    
    Parameters:
    - query (str): The search query.
    - number_of_results (int): The total number of results to return. Default is 10.
    - offset (int): The starting index for the first result returned (Google pagination).
    - tool_config (Optional[List[Dict]]): Configuration containing SERP API token, etc.
    - as_oq (Optional[str]): Optional query terms for SerpAPI (if supported).
    
    Returns:
    - List[str]: A list of organic search results, each serialized as a JSON string.
    """
    logger.info("Entering search_google")
    if not query:
        logger.warning("Empty query string provided.")
        return []

    # Use 'as_oq' in the cache key too, so different optional terms don't conflict
    cache_key = f"{query}_{number_of_results}_{offset}_{as_oq or ''}"
    cached_response = retrieve_output("search_google_serp", cache_key)
    if cached_response is not None:
        logger.info("Cache hit for search_google.")
        return cached_response

    SERPAPI_KEY = get_serp_api_access_token(tool_config)
    url = "https://serpapi.com/search"

    page_size = 100
    all_results: List[Dict[str, Any]] = []
    start_index = offset

    logger.debug(f"Requesting up to {number_of_results} results for '{query}' starting at offset {offset}.")

    async with aiohttp.ClientSession() as session:
        while len(all_results) < number_of_results:
            to_fetch = min(page_size, number_of_results - len(all_results))
            params = {
                "q": query,
                "num": to_fetch,
                "start": start_index,
                "api_key": SERPAPI_KEY,
                "engine": "google",
                "location": "United States"
            }

            # If we have optional terms, add them
            if as_oq:
                params["as_oq"] = as_oq

            logger.debug(f"SERP API GET request with params: {params}")

            try:
                async with session.get(url, params=params) as response:
                    logger.debug(f"Received response status: {response.status}")
                    if response.status != 200:
                        try:
                            error_content = await response.json()
                        except Exception:
                            error_content = await response.text()
                        logger.warning(f"Non-200 response from SERP API: {error_content}")
                        return [json.dumps({"error": error_content})]

                    result = await response.json()
            except Exception as e:
                logger.exception("Exception during SERP API request.")
                return [json.dumps({"error": str(e)})]

            organic_results = result.get('organic_results', [])
            if not organic_results:
                logger.debug("No more organic results returned; stopping.")
                break

            all_results.extend(organic_results)
            start_index += to_fetch

            if len(all_results) >= number_of_results:
                break

    all_results = all_results[:number_of_results]
    logger.info(f"Found {len(all_results)} results for query '{query}'.")

    serialized_results = [json.dumps(item) for item in all_results]
    cache_output("search_google_serp", cache_key, serialized_results)
    return serialized_results