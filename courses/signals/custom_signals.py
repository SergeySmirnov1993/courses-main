# courses/signals.py
from django.dispatch import Signal, receiver
from courses import models

# Создаем пользовательский сигнал
course_published = Signal()  # Можно передать аргументы: Signal(providing_args=['course', 'user'])


# Обработка сигнала
@receiver(course_published, sender=models.Course)
def notify_course_published(sender, course, user, **kwargs):
    print(f'Курс {course.title} опубликован пользователем {user}')
    # Можно отправить email, создать уведомление и т.д.