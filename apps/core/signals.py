# file: apps/core/signals.py
from django.db.models.signals import post_save, post_delete
from django.forms.models import model_to_dict
from .middleware import get_current_user


def _serialize(instance):
    try:
        return {k: str(v) if v is not None else None for k, v in model_to_dict(instance).items()}
    except Exception:
        return {'id': str(instance.pk)}


def _write_audit(action_type, instance, old=None, new=None):
    from .models import AuditLog
    user = get_current_user()
    try:
        AuditLog.objects.create(
            action_type  = action_type,
            performed_by = user if (user and user.is_authenticated) else None,
            target_table = f"{instance._meta.app_label}.{instance._meta.model_name}",
            target_id    = instance.pk,
            old_value    = old,
            new_value    = new,
        )
    except Exception:
        pass  # audit must never crash the main request


def _on_save(sender, instance, created, **kwargs):
    _write_audit('create' if created else 'update', instance, new=_serialize(instance))


def _on_delete(sender, instance, **kwargs):
    _write_audit('delete', instance, old=_serialize(instance))


def register_audit_signals():
    from apps.assets.models import Asset, AssetLog
    from apps.companies.models import Company, Department
    from apps.operations.models import AssetTransfer, Maintenance

    for model in [Asset, AssetLog, Company, Department, AssetTransfer, Maintenance]:
        post_save.connect(_on_save,    sender=model, weak=False)
        post_delete.connect(_on_delete, sender=model, weak=False)