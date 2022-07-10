from typing import Any, Collection, Dict


def set_to_tuple(field, field_name):
    """Add if exists or set if not."""
    if field:
        field += (field_name,)
    else:
        field = (field_name,)
    return field


class CreatedAtAdminMixin:
    def __init__(self, *args: Collection[Any], **kwargs: Dict[str, Any]) -> None:
        super().__init__(*args, **kwargs)
        for field_name in ("readonly_fields", "list_filter"):
            target_field = getattr(self, field_name)
            setattr(self, field_name, set_to_tuple(target_field, "created_at"))


class UpdatedAtAdminMixin:
    def __init__(self, *args: Collection[Any], **kwargs: Dict[str, Any]) -> None:
        super().__init__(*args, **kwargs)
        for field_name in ("readonly_fields", "list_filter"):
            target_field = getattr(self, field_name)
            setattr(self, field_name, set_to_tuple(target_field, "updated_at"))


class CreatedAtAndUpdatedAtAdminMixin(UpdatedAtAdminMixin, CreatedAtAdminMixin):
    """Pass to admin class created at and updated at fields."""
    pass
