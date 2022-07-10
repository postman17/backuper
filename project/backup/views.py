import json

from django.views import View
from django.http import HttpResponse, HttpResponseRedirect

from backup.models import BackupClientTemporaryState
from backup.enums import BackupClientTemporaryStateEnum
from backup.matcher import BACKUP_CLIENT_MANAGERS_MATCHER
from helpers.crypto import EncryptDecryptWrapper


class OauthCodeView(View):
    """View for redirect_url for oauth clients."""

    def get(self, request):
        if request.method != "GET":
            raise Exception("Wrong http method")

        state = request.GET.get("state")
        code = request.GET.get("code")

        temp_state = BackupClientTemporaryState.objects.filter(
            state=state
        ).select_related("client").first()
        if not temp_state:
            raise Exception("Temporary state not found")

        client = temp_state.client
        client_id = EncryptDecryptWrapper.get_decrypted_value(client.config, "client_id")
        client_secret = EncryptDecryptWrapper.get_decrypted_value(client.config, "client_secret")
        if not client_id or not client_secret:
            raise Exception("Credentials not found")

        manager = BACKUP_CLIENT_MANAGERS_MATCHER.get_manager_by_client_name(
            temp_state.client.client_name
        )()
        tokens = manager.get_tokens(client_id, client_secret, code)

        encrypted_tokens = EncryptDecryptWrapper.encrypt_sensitive_fields(tokens)
        client.config.update(encrypted_tokens)
        client.save(update_fields=['config'])
        client.set_credentials_confirmed()

        temp_state.set_success()

        return HttpResponseRedirect("/")


class OauthCredsSucceedView(View):
    """View for waiting get credentials succeed."""

    def post(self, request):
        if request.method != "POST":
            raise Exception("Wrong http method")

        json_data = json.loads(request.body)
        temp_state = BackupClientTemporaryState.objects.filter(
            state=json_data.get("state")
        ).first()
        if not temp_state:
            raise Exception("State not found")

        if temp_state.status == BackupClientTemporaryStateEnum.SUCCESS:
            return HttpResponse(status=204)

        BackupClientTemporaryState.set_expired_to_all()

        return HttpResponse(status=200)
