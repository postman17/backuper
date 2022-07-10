from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

from backup.enums import BackupClientNameEnum
from backup.models import BackupClient, ServiceForBackup


class BackupClientForm(forms.ModelForm):
    client_name = forms.ChoiceField(
        choices=BackupClientNameEnum.get_choices_for_forms(),
        label=mark_safe(f"<br><br>{_('Client name')}"),
    )
    storage_name = forms.CharField(widget=forms.TextInput(
        attrs={
            'id': 'storage-name',
        }
    ))

    class Meta:
        model = BackupClient
        exclude = ("config", "status", "owner")


class ClientNameAndStorageNameFormMixin(forms.Form):
    client_name = forms.CharField(max_length=settings.DEFAULT_CHARFIELD_MAXLENGTH, widget=forms.HiddenInput())
    storage_name = forms.CharField(max_length=settings.DEFAULT_CHARFIELD_MAXLENGTH, widget=forms.HiddenInput())


class OauthClientCredentialsForm(ClientNameAndStorageNameFormMixin):
    client_id = forms.CharField(max_length=settings.DEFAULT_CHARFIELD_MAXLENGTH, label=_("Client ID"))
    client_secret = forms.CharField(
        max_length=settings.DEFAULT_CHARFIELD_MAXLENGTH,
        label=mark_safe(f"<br><br>{_('Client secret')}")
    )
    state = forms.CharField(max_length=settings.DEFAULT_CHARFIELD_MAXLENGTH, widget=forms.HiddenInput(), required=False)
    redirect_url = forms.CharField(
        max_length=settings.DEFAULT_CHARFIELD_MAXLENGTH,
        widget=forms.HiddenInput(),
        required=False,
        initial=f"{settings.SITE_URL}/backup/oauth-code/"
    )


class LocalContainerCredentialsForm(ClientNameAndStorageNameFormMixin):
    master_password = forms.CharField(max_length=settings.DEFAULT_CHARFIELD_MAXLENGTH, required=False)


class ServiceForBackupForm(forms.ModelForm):
    service_name = forms.CharField(
        max_length=settings.DEFAULT_CHARFIELD_MAXLENGTH,
        label=mark_safe(f"<br><br>{_('Service name')}"),
        widget=forms.TextInput(
            attrs={
                'id': 'service-name',
            }
        ))
    source_folder = forms.CharField(
        max_length=settings.DEFAULT_CHARFIELD_MAXLENGTH,
        label=mark_safe(f"<br><br>{_('Source folder')}"),
        widget=forms.Textarea()
    )

    class Meta:
        model = ServiceForBackup
        fields = ("service_name", "source_folder")