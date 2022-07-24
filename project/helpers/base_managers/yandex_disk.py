"""
https://yadisk.readthedocs.io/ru/latest/intro.html
https://github.com/ivknv/yadisk
"""
import logging
import yadisk


base_manager_logger = logging.getLogger(__name__)


class YandexDiskBaseManager:
    """Yandex disk clients base manager."""

    def get_oauth_code_url(self, client_id: str, state: str, redirect_url: str) -> str:
        base_manager_logger.info(f"Yandex disk base manager: get oauth code url started")

        client = yadisk.YaDisk(client_id)
        url = client.get_code_url(state=state, redirect_url=redirect_url)

        base_manager_logger.info(f"Yandex disk base manager: get oauth code url finished - {url}")
        return url

    def get_tokens_from_response(self, response) -> dict:
        return {
            'access_token': response.access_token,
            'refresh_token': response.refresh_token,
            'token_type': response.token_type,
            'expires_in': response.expires_in,
        }

    def get_tokens(self, client_id: str, client_secret: str, code: str) -> dict:
        base_manager_logger.info("Yandex disk base manager: get tokens started")

        client = yadisk.YaDisk(client_id, client_secret)
        response = client.get_token(code)

        base_manager_logger.info("Yandex disk base manager: get tokens finished")
        return self.get_tokens_from_response(response)

    def check_access_token(self, access_token: str, **kwargs) -> bool:
        logger = kwargs.get("logger", base_manager_logger)
        logger.info("Yandex disk base manager: check access token started")

        client = yadisk.YaDisk(token=access_token)
        try:
            client.get_disk_info()
        except Exception:
            base_manager_logger.info("Yandex disk base manager: access token not valid")
            return False

        logger.info("Yandex disk base manager: access token valid")
        return True

    def refresh_token(self, config, **kwargs) -> dict:
        logger = kwargs.get("logger", base_manager_logger)
        logger.info("Yandex disk base manager: refresh token started")
        client = yadisk.YaDisk(id=config["client_id"], secret=config["client_secret"])
        response = client.refresh_token(config["refresh_token"])

        logger.info("Yandex disk base manager: refresh token finished")
        return self.get_tokens_from_response(response)

    def upload_file(
            self, access_token: str, source_path: str, target_path: str, **kwargs
    ) -> bool:
        logger = kwargs.get("logger", base_manager_logger)
        logger.info(f"Yandex disk base manager: upload file started")
        try:
            client = yadisk.YaDisk(token=access_token)
            client.upload(source_path, target_path, overwrite=True)
        except Exception:
            logger.error("Yandex disk base manager: upload file error", exc_info=True)

            return False

        logger.info("Yandex disk base manager: upload file finished")
        return True
