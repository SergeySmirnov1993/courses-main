from django.db import models
from django.db.models.functions import Now
from django.utils.text import slugify


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_default=Now())
    updated_at = models.DateTimeField(auto_now=True)

    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class Course(BaseModel):
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(default="")

    def __str__(self):
        return self.title


class CoursePart(BaseModel):
    course = models.ForeignKey(Course, related_name="parts", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(default="")

    def __str__(self):
        return self.title


class CourseTopic(BaseModel):
    part = models.ForeignKey(
        CoursePart, related_name="topics", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    description = models.TextField(default="")

    def __str__(self):
        return self.title


def document_upload_to(instance, filename):
    """
    Генерирует путь для загрузки документа в структуре:
    курс/часть/тема/{документы}
    """
    # Получаем курс через topic -> part -> course
    course = instance.topic.part.course
    part = instance.topic.part
    topic = instance.topic

    # Создаем безопасные имена для директорий (убираем спецсимволы)
    course_slug = slugify(course.title)
    part_slug = slugify(part.title)
    topic_slug = slugify(topic.title)

    # Формируем путь: курс/часть/тема/имя_файла
    path = f"courses/{course_slug}/{part_slug}/{topic_slug}/{filename}"
    return path


class TopicDocument(BaseModel):
    topic = models.ForeignKey(
        CourseTopic, related_name="documents", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to=document_upload_to)
