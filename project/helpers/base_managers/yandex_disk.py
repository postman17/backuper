"""
https://yadisk.readthedocs.io/ru/latest/intro.html
https://github.com/ivknv/yadisk
"""
import logging
import yadisk


logger = logging.getLogger(__name__)


class YandexDiskBaseManager:
    """Yandex disk clients base manager."""

    def get_oauth_code_url(self, client_id: str, state: str, redirect_url: str) -> str:
        logger.info(f"Yandex disk base manager: get oauth code url started")

        client = yadisk.YaDisk(client_id)
        url = client.get_code_url(state=state, redirect_url=redirect_url)

        logger.info(f"Yandex disk base manager: get oauth code url finished - {url}")
        return url

    def get_tokens(self, client_id: str, client_secret: str, code: str) -> dict:
        logger.info("Yandex disk base manager: get tokens started")

        client = yadisk.YaDisk(client_id, client_secret)
        response = client.get_token(code)
        fields = {
            'access_token': response.access_token,
            'refresh_token': response.refresh_token,
            'token_type': response.token_type,
            'expires_in': response.expires_in,
        }

        logger.info("Yandex disk base manager: get tokens finished")
        return fields

    def upload_file(
            self, access_token: str, source_path: str, target_path: str,
    ) -> bool:
        logger.info(f"Yandex disk base manager: upload file started")
        try:
            client = yadisk.YaDisk(token=access_token)
            client.upload(source_path, target_path, overwrite=True)
        except Exception:
            logger.error("Yandex disk base manager: upload file error", exc_info=True)

            return False

        logger.info("Yandex disk base manager: upload file finished")
        return True
