from django.contrib.auth.models import Group, AbstractUser
from django.db import models

from core.models import GeneralModel


class UserGroup(Group, GeneralModel):
    name_suffix = 'о'

    class Meta:
        verbose_name = 'группа'
        verbose_name_plural = 'группы'


class UserProfile(AbstractUser, GeneralModel):
    middle_name = models.CharField('Отчество', max_length=150, blank=True)

    def get_full_name(self):
        # Формирование полного имени "Фамилия Имя Отчество"
        full_name = "%s %s %s" % (self.last_name,
                                  self.first_name,
                                  self.middle_name
                                  )
        return full_name.strip()

    def get_short_name(self):
        # Формирование имени "Фамилия И.О."
        try:
            short_name = '%s %s.%s.' % (str(self.last_name).capitalize(),
                                        str(self.first_name)[0].upper(),
                                        str(self.middle_name)[0].upper(),
                                        )
        except IndexError:
            return str(self.last_name).capitalize()

        return short_name

    def save(self, *args, **kwargs):
        created = not self.pk  # Проверяем, создается ли новая запись
        super().save(*args, **kwargs)
        if created:
            # Добавление записей в формы подразделов
            for f in self._meta.related_objects:
                if isinstance(f, models.OneToOneRel):
                    model = f.related_model
                    model.objects.create(user=self)

# @receiver(m2m_changed, sender=UserGroup.permissions.through)
# @receiver(m2m_changed, sender=UserProfile.groups.through)
# @receiver(m2m_changed, sender=UserProfile.user_permissions.through)
# def update_userprofile_related(sender, instance, action, reverse, model, pk_set, **kwargs):
#     if action in ("post_add", "post_remove", "post_clear"):
#         if sender == UserGroup.permissions.through:
#             instance.group.permissions.set(instance.permissions.all())
#         elif sender == UserProfile.groups.through:
#             instance.user.groups.set(instance.groups.all())
#         elif sender == UserProfile.user_permissions.through:
#             instance.user.user_permissions.set(instance.user_permissions.all())


# @receiver(post_save, sender=UserProfile)
# def update_user_profile(sender, instance, created, **kwargs):
#     if created:  # Обработка создания
#         instance.user = User.objects.create(username=instance.username)
#         instance.user.save()
#     else:  # Обработка обновления
#         instance.user.username = instance.username
#         instance.user.save()
#         instance.user.user_permissions.set(instance.user_permissions.all())
#         instance.user.save()
#
#
# @receiver(post_save, sender=Group)
# def update_user_group(sender, instance, **kwargs):
#     try:
#         user_group = UserGroup.objects.get(group=instance)
#         user_group.name = instance.name
#         user_group.save()
#     except UserGroup.DoesNotExist:
#         pass
