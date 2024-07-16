import logging
import sys
from typing import Any, Callable, Dict, List

import coloredlogs

# Base Logging Configs
logger = logging.getLogger(__name__)  # noqa

# Coloredlogs Configs
coloredFormatter = coloredlogs.ColoredFormatter(
    fmt="[%(name)s] %(asctime)s  %(message)s",
    level_styles=dict(
        debug=dict(color="white"),
        info=dict(color="blue"),
        warning=dict(color="yellow", bright=True),
        error=dict(color="red", bold=True, bright=True),
        critical=dict(color="black", bold=True, background="red"),
    ),
    field_styles=dict(
        name=dict(color="white"),
        asctime=dict(color="white"),
        funcName=dict(color="white"),
        lineno=dict(color="white"),
    ),
)

# Console Handler Configs
ch = logging.StreamHandler(stream=sys.stdout)
ch.setFormatter(fmt=coloredFormatter)
logger.addHandler(hdlr=ch)
logger.setLevel(level=logging.CRITICAL)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def paginate(
    func: Callable[..., List[Dict[str, Any]]]
) -> Callable[..., List[Dict[str, Any]]]:
    def wrapper(*args: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        items = []
        response: List = func(*args, **kwargs, enhance=False)

        try:
            items.extend(response[0]["items"])

            while (
                "page_info" in response[0]
                and "next_page_token" in response[0]["page_info"]
            ):
                logger.debug(
                    f"Next page token: {response[0]['page_info']['next_page_token']}"
                )
                kwargs["page_token"] = response[0]["page_info"]["next_page_token"]
                response = func(*args, **kwargs, enhance=False)
                for obj in response:
                    if "items" in obj:
                        items.extend(obj["items"])
        except KeyError:
            logger.debug("KeyError")
            return response
        logger.debug("Finished fetching all pages.")
        return items

    return wrapper
