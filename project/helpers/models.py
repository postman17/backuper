import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UUIDModelAbstract(models.Model):
    id = models.UUIDField(_("ID"), default=uuid.uuid4, primary_key=True, editable=False)

    class Meta:
        abstract = True


class CreatedAtAbstract(models.Model):
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)

    class Meta:
        abstract = True


class UpdatedAtAbstract(models.Model):
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True, null=True)

    class Meta:
        abstract = True


class OwnerAbstract(models.Model):
    owner = models.ForeignKey(User, verbose_name=_("Owner"), on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        abstract = True
