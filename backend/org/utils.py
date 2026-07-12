from org.models import ActivityLog

def log_activity(user, action, instance, description=""):
    """
    Utility function to log model state changes or explicit actions.
    """
    target_model = instance.__class__.__name__
    # Handle unsaved instances that might not have an id yet
    target_id = str(instance.id) if hasattr(instance, 'id') and instance.id is not None else None

    if not description:
        description = f"{action} action performed on {target_model}."

    return ActivityLog.objects.create(
        user=user if user and user.is_authenticated else None,
        action=action,
        target_model=target_model,
        target_id=target_id,
        description=description
    )
