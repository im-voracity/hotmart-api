import logging
import sys

import coloredlogs
import requests

# Base Logging Configs
logger = logging.getLogger(__name__)

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


class Authenticator:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        basic: str,
        log_level: int = logging.CRITICAL,
    ) -> None:
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.basic: str = basic
        self.log_level: int = log_level

        self.token_cache = None
        self.token_expires_at = None
        self.token_found_in_cache = False

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)

        self.auth_url = "https://api-sec-vlc.hotmart.com/security/oauth/token"

    def authenticate(self):
        # Checar se o token existe
        # Se existir e não tiver expirado, autenticação válida, retornar token
        # Se NÃO existir, autenticação inválida, solicitar novo token

        # Se o Token existir, mas estiver expirado, autenticação inválida, solicitar novo token

        self.logger.debug("Fetching new access token")

        headers = {
            "Content-Type": "application/json",
            "Authorization": self.basic
        }

        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        response = requests.post(url=self.auth_url, headers=headers, params=payload)
        logger.debug("Access token obtained successfully")
        logger.debug(response.json)

