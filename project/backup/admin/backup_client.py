import json

from jinja2 import Template

from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from helpers.admin import CreatedAtAndUpdatedAtAdminMixin

from backup.models import BackupClient, BackupClientTemporaryState
from backup.forms import BackupClientForm
from backup.matcher import BACKUP_CLIENT_MANAGERS_MATCHER
from backup.enums import BackupClientNameEnum, BackupClientStatusEnum
from helpers.crypto import EncryptDecryptWrapper


@admin.register(BackupClient)
class BackupClientAdmin(CreatedAtAndUpdatedAtAdminMixin, admin.ModelAdmin):
    change_list_template = 'backup/create_client_change_list.html'
    list_display = ("id", "storage_name", "client_name", "status", "owner", "updated_at", "created_at")

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("choose_client/", self.choose_client_view, name="backup_client_choose_client"),
            path(
                "check_exists_storage_name/",
                self.check_exists_storage_name,
                name="backup_client_check_client_name"
            ),
            path("credentials/", self.credentials_view, name="backup_client_credentials"),
            path("final_stage/", self.final_stage_view, name="backup_client_final_stage"),
        ]
        return my_urls + urls

    def choose_client_view(self, request):
        next_step_url = reverse("admin:backup_client_credentials")
        with open("project/backup/templates/backup/jinja2_templates/check_exists_field.html") as file:
            template = Template(file.read())
            js_code = _(str(template.render(
                element_css_id="storage-name",
                url="/backup/backupclient/check_exists_storage_name/",
                field_name="storage_name",
            )))

        context = {
            "title": "Choose client",
            "opts": BackupClient._meta,
            "client_form": BackupClientForm(),
            "next_step_url": next_step_url,
            "js_code": js_code,
        }
        return render(request, 'backup/create_client.html', context=context)

    def check_exists_storage_name(self, request):
        if request.method != "POST":
            raise Exception("Something went wrong", request)

        json_data = json.loads(request.body)
        is_exists = BackupClient.objects.filter(
            storage_name=json_data.get("storage_name")
        ).exists()
        return JsonResponse({"status": is_exists})

    def credentials_view(self, request):
        if request.method != "POST":
            raise Exception("Something went wrong", request)

        backup_client_form = BackupClientForm(request.POST)
        if not backup_client_form.is_valid():
            raise Exception("Something went wrong", backup_client_form.errors)

        client_name = backup_client_form.cleaned_data.get("client_name")
        storage_name = backup_client_form.cleaned_data.get("storage_name")

        credentials_form = BACKUP_CLIENT_MANAGERS_MATCHER.get_form_by_client_name(client_name)
        credentials_form_text = BACKUP_CLIENT_MANAGERS_MATCHER.get_form_help_text_by_client_name(client_name)

        next_step_url = reverse("admin:backup_client_final_stage")
        context = {
            "title": f"Set client credentials for {BackupClientNameEnum(client_name).label}",
            "opts": BackupClient._meta,
            "client_form_description": credentials_form_text,
            "client_form": credentials_form(initial={"client_name": client_name, "storage_name": storage_name}),
            "next_step_url": next_step_url,
        }
        return render(request, 'backup/create_client.html', context=context)

    def final_stage_view(self, request):
        client_form = BackupClientForm(request.POST)
        if not client_form.is_valid():
            raise Exception(client_form.errors)

        client_name = client_form.cleaned_data.get("client_name")

        credentials_form = BACKUP_CLIENT_MANAGERS_MATCHER.get_form_by_client_name(client_name)
        credentials_form_instance = credentials_form(request.POST)
        if not credentials_form_instance.is_valid():
            raise Exception("Something went wrong")

        config = credentials_form_instance.cleaned_data.copy()
        del config["storage_name"]
        del config["client_name"]

        encrypted_config = EncryptDecryptWrapper.encrypt_sensitive_fields(config)
        is_not_confirmed_need = client_name in BackupClientNameEnum.not_need_confirm_client_names()
        backup_client_status = BackupClientStatusEnum.CREDENTIALS_NOT_CONFIRMED
        if is_not_confirmed_need:
            backup_client_status = BackupClientStatusEnum.CREDENTIALS_CONFIRMED

        backup_client = BackupClient.objects.create(
            storage_name=credentials_form_instance.cleaned_data.get("storage_name"),
            client_name=client_name,
            config=encrypted_config,
            owner=request.user,
            status=backup_client_status,
        )

        if not is_not_confirmed_need:
            state = BackupClientTemporaryState.objects.create(client=backup_client, owner=request.user)
            credentials_form_instance.cleaned_data["state"] = state.state

        ClientManager = BACKUP_CLIENT_MANAGERS_MATCHER.get_manager_by_client_name(client_name)
        manager = ClientManager()
        manager_method = getattr(manager, manager.create_client_action_method)

        attrs_for_manager_method = {
            field: credentials_form_instance.cleaned_data.get(field)
            for field in manager.create_client_action_method_fields
        }

        data = manager_method(**attrs_for_manager_method)
        context = {
            "title": f"Backup Client tuning for {BackupClientNameEnum(client_name).label}",
            "opts": BackupClient._meta,
            "text": data,
        }
        return render(request, 'backup/final_stage.html', context=context)
