from django.db import models
from django.conf import settings

class ActivityLog(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actor_activities'
    )
    action = models.CharField(max_length=255)
    target_type = models.CharField(max_length=255)
    target_id = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    meta = models.JSONField(default=dict, blank=True)

    # Backward compatibility properties for old test suites
    @property
    def user(self):
        return self.actor

    @user.setter
    def user(self, value):
        self.actor = value

    @property
    def target_model(self):
        return self.target_type

    @target_model.setter
    def target_model(self, value):
        self.target_type = value

    @property
    def description(self):
        return self.meta.get('description', '')

    @description.setter
    def description(self, value):
        if self.meta is None:
            self.meta = {}
        self.meta['description'] = value

    def __str__(self):
        return f"{self.actor} performed {self.action} on {self.target_type} {self.target_id} at {self.timestamp}"
