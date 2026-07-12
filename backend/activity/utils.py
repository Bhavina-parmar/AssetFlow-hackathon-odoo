from .models import ActivityLog as NewActivityLog
from org.models import ActivityLog as OldActivityLog

def log_activity(user, action, instance, description="", meta=None):
    """
    Refactored log_activity helper for the 'activity' app.
    Translates model instances dynamically into target_type/target_model and target_id.
    Accepts descriptions and maps them into the meta JSON field.
    Writes to both the new ActivityLog and the old ActivityLog models for backward compatibility and test passing.
    """
    if meta is None:
        meta = {}
    if description:
        meta['description'] = description

    target_type = instance.__class__.__name__ if instance else 'System'
    target_id = str(instance.id) if instance and hasattr(instance, 'id') and instance.id is not None else None

    # Handle cases where actor is not authenticated
    actor_user = user if user and user.is_authenticated else None

    # 1. Write to old log table for backward compatibility / tests
    try:
        OldActivityLog.objects.create(
            user=actor_user,
            action=action,
            target_model=target_type,
            target_id=target_id,
            description=description or (meta.get('description', '') if meta else '')
        )
    except Exception:
        pass

    # 2. Write to new log table
    return NewActivityLog.objects.create(
        actor=actor_user,
        action=action,
        target_type=target_type,
        target_id=target_id,
        meta=meta
    )
