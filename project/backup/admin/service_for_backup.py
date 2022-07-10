import json

from jinja2 import Template

from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _

from backup.models import ServiceForBackup
from helpers.admin import CreatedAtAndUpdatedAtAdminMixin
from backup.forms import ServiceForBackupForm
from backup.managers import LocalContainerManager


@admin.register(ServiceForBackup)
class ServiceForBackupAdmin(CreatedAtAndUpdatedAtAdminMixin, admin.ModelAdmin):
    change_list_template = 'backup/create_service_change_list.html'
    list_display = ("id", "service_name", "source_folder", "owner", "updated_at", "created_at")

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "choose_service/",
                self.choose_service_view,
                name="backup_service_choose_service",
            ),
            path(
                "check_exists_service_name/",
                self.check_exists_service_name,
                name="backup_client_check_service_name",
            ),
            path("final_stage/", self.final_stage_view, name="backup_service_final_stage"),
        ]
        return my_urls + urls

    def choose_service_view(self, request):
        next_step_url = reverse("admin:backup_service_final_stage")
        with open("project/backup/templates/backup/jinja2_templates/check_exists_field.html") as file:
            template = Template(file.read())
            js_code = _(str(template.render(
                element_css_id="service-name",
                url="/backup/serviceforbackup/check_exists_service_name/",
                field_name="service_name",
            )))

        context = {
            "title": "Choose service",
            "opts": ServiceForBackup._meta,
            "service_form": ServiceForBackupForm(),
            "next_step_url": next_step_url,
            "js_code": js_code,
        }
        return render(request, 'backup/create_service.html', context=context)

    def check_exists_service_name(self, request):
        if request.method != "POST":
            raise Exception("Something went wrong", request)

        json_data = json.loads(request.body)
        is_exists = ServiceForBackup.objects.filter(
            service_name=json_data.get("service_name")
        ).exists()
        return JsonResponse({"status": is_exists})

    def final_stage_view(self, request):
        form = ServiceForBackupForm(request.POST)
        if not form.is_valid():
            raise Exception("Something went wrong")

        form.cleaned_data["owner"] = request.user

        result_text = _(
            '<p style="color: red; '
            'font-size: 15px;">'
            'Service for backup created error. '
            'Source folder does not exists.</p>'
        )
        manager = LocalContainerManager()

        is_path_exists = manager.check_path(form.cleaned_data['source_folder'])
        if is_path_exists:
            result_text = _(
                '<p style="color: green; '
                'font-size: 15px;">'
                'Service for backup created successfully</p>'
            )
            service = form.save()
            service.owner = request.user
            service.save(update_fields=["owner"])

        context = {
            "title": f"Service for backup",
            "opts": ServiceForBackup._meta,
            "text": result_text,
        }
        return render(request, 'backup/final_stage.html', context=context)
