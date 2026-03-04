# courses/signals.py
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.dispatch import receiver
from courses import models

# Пример: логирование при создании курса
@receiver(post_save, sender=models.Course)
def course_created(sender, instance, created, **kwargs):
    if created:
        print(f'Создан новый курс: {instance.title}')

# Пример: очистка файлов при удалении документа
@receiver(pre_delete, sender=models.TopicDocument)
def document_deleted(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete(save=False)  # Удаляем файл с диска