import json

from django.db import models

from users.models import UserProfile


class UserSettings(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    settings = models.TextField('Настройки', blank=True)

    name_suffix = 'ы'

    class Meta:
        verbose_name = 'настройки'
        verbose_name_plural = 'настройки'

    def __str__(self):
        return str(self.user)

    def get_settings(self):
        try:
            return json.loads(self.settings)
        except json.JSONDecodeError:
            return {}

    def update_settings(self, key, data):
        new_settings = {key: [v for v in data.values() if v]}
        settings = self.get_settings()
        settings.update(new_settings)
        self.settings = settings
        self.save()

    def save(self, *args, **kwargs):
        if isinstance(self.settings, dict):
            self.settings = json.dumps(self.settings)
        super().save(*args, **kwargs)  ###### включить
