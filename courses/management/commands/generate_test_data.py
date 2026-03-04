from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.text import slugify
from courses import models
from faker import Faker
from django_seed import Seed
import random
import shutil
from pathlib import Path


class Command(BaseCommand):
    help = "Генерирует тестовые данные для курсов. Использует faker (напрямую) или django-seed."

    def add_arguments(self, parser):
        parser.add_argument(
            "count",
            type=int,
            help="Количество тестовых данных для создания (количество курсов)",
        )
        parser.add_argument(
            "--method",
            type=str,
            choices=["faker", "seeder"],
            default="faker",
            help="Метод генерации данных: faker (напрямую через Faker) \
            или seeder (через django-seed) (по умолчанию: faker)",
        )

    def handle(self, *args, **options):
        count = options["count"]
        method = options["method"]

        self.stdout.write(
            self.style.SUCCESS(
                f"Начинаем генерацию {count} тестовых данных методом {method}..."
            )
        )

        # Создаем директорию для тестовых документов
        self.create_test_documents_dir()

        if method == "faker":
            self.generate_with_faker(count)
        elif method == "seeder":
            self.generate_with_seeder(count)

        self.stdout.write(
            self.style.SUCCESS(f"Успешно создано {count} тестовых курсов!")
        )

    def create_test_documents_dir(self):
        """Создает директорию для тестовых документов в медиа"""
        test_docs_dir = Path(settings.MEDIA_ROOT) / "seed_documents"
        test_docs_dir.mkdir(parents=True, exist_ok=True)

        # Создаем несколько тестовых файлов
        test_files = [
            "test_document_1.pdf",
            "test_document_2.docx",
            "test_document_3.txt",
            "test_document_4.xlsx",
            "test_document_5.pptx",
        ]

        for filename in test_files:
            file_path = test_docs_dir / filename
            if not file_path.exists():
                # Создаем пустой файл для тестирования
                file_path.write_text(
                    f"Тестовый документ: {filename}\nЭто тестовый файл для генерации данных."
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Создана директория для тестовых документов: {test_docs_dir}"
            )
        )

    def generate_with_faker(self, count):
        """Генерирует тестовые данные используя Faker"""
        fake = Faker("ru_RU")  # Используем русскую локаль

        for i in range(count):
            # Создаем курс
            course = models.Course.objects.create(
                title=fake.catch_phrase() + f" {i+1}",
                description=fake.text(max_nb_chars=500),
            )

            # Создаем 2-4 части для каждого курса
            num_parts = random.randint(2, 4)
            for j in range(num_parts):
                part = models.CoursePart.objects.create(
                    course=course,
                    title=fake.sentence(nb_words=3).rstrip(".") + f" {j+1}",
                    description=fake.text(max_nb_chars=300),
                )

                # Создаем 2-5 тем для каждой части
                num_topics = random.randint(2, 5)
                for k in range(num_topics):
                    topic = models.CourseTopic.objects.create(
                        part=part,
                        title=fake.sentence(nb_words=4).rstrip(".") + f" {k+1}",
                        description=fake.text(max_nb_chars=200),
                    )

                    # Создаем 1-3 документа для каждой темы
                    num_documents = random.randint(1, 3)
                    for d in range(num_documents):
                        self.create_document_with_faker(topic, fake, d)

            self.stdout.write(f"Создан курс: {course.title}")

    def generate_with_seeder(self, count):
        """Генерирует тестовые данные используя django-seed (faker из seeder, но создаем через ORM)"""
        # Используем faker из django-seed, но создаем объекты напрямую через Django ORM
        # чтобы избежать проблем с автоматическим определением полей created_at/updated_at
        seeder = Seed.seeder("ru_RU")
        fake = seeder.faker

        for i in range(count):
            # Создаем курс напрямую через ORM
            course = models.Course.objects.create(
                title=fake.catch_phrase(), description=fake.text(max_nb_chars=500)
            )

            # Создаем 2-4 части для каждого курса
            num_parts = random.randint(2, 4)
            for j in range(num_parts):
                part = models.CoursePart.objects.create(
                    course=course,
                    title=fake.sentence(nb_words=3).rstrip("."),
                    description=fake.text(max_nb_chars=300),
                )

                # Создаем 2-5 тем для каждой части
                num_topics = random.randint(2, 5)
                for k in range(num_topics):
                    topic = models.CourseTopic.objects.create(
                        part=part,
                        title=fake.sentence(nb_words=4).rstrip("."),
                        description=fake.text(max_nb_chars=200),
                    )

                    # Создаем 1-3 документа для каждой темы
                    num_documents = random.randint(1, 3)
                    for d in range(num_documents):
                        self.create_document_with_seeder(topic, d, fake)

            self.stdout.write(f"Создан курс: {course.title}")

    def create_document_with_faker(self, topic, fake, index):
        """Создает документ используя Faker"""
        # Получаем случайный тестовый файл из seed_documents
        test_docs_dir = Path(settings.MEDIA_ROOT) / "seed_documents"
        test_files = [f for f in test_docs_dir.glob("*") if f.is_file()]

        if test_files:
            source_file = random.choice(test_files)
            # Создаем уникальное имя файла
            filename = f"{fake.word()}_{index}_{source_file.name}"

            # Формируем путь назначения согласно структуре
            course_slug = slugify(topic.part.course.title)
            part_slug = slugify(topic.part.title)
            topic_slug = slugify(topic.title)
            dest_dir = (
                Path(settings.MEDIA_ROOT)
                / "courses"
                / course_slug
                / part_slug
                / topic_slug
            )
            dest_dir.mkdir(parents=True, exist_ok=True)

            # Копируем файл
            dest_file = dest_dir / filename
            shutil.copy2(source_file, dest_file)

            # Создаем документ с относительным путем
            relative_path = f"courses/{course_slug}/{part_slug}/{topic_slug}/{filename}"
            models.TopicDocument.objects.create(
                topic=topic,
                name=fake.sentence(nb_words=3).rstrip("."),
                file=relative_path,
            )
        else:
            # Если нет тестовых файлов, создаем документ без файла
            self.stdout.write(
                self.style.WARNING(f"Нет тестовых файлов в {test_docs_dir}")
            )

    def create_document_with_seeder(self, topic, index, fake):
        """Создает документ используя faker из django-seed"""
        # Получаем случайный тестовый файл из seed_documents
        test_docs_dir = Path(settings.MEDIA_ROOT) / "seed_documents"
        test_files = [f for f in test_docs_dir.glob("*") if f.is_file()]

        if test_files:
            source_file = random.choice(test_files)
            filename = f"{fake.word()}_{index}_{source_file.name}"

            # Формируем путь назначения согласно структуре
            course_slug = slugify(topic.part.course.title)
            part_slug = slugify(topic.part.title)
            topic_slug = slugify(topic.title)
            dest_dir = (
                Path(settings.MEDIA_ROOT)
                / "courses"
                / course_slug
                / part_slug
                / topic_slug
            )
            dest_dir.mkdir(parents=True, exist_ok=True)

            # Копируем файл
            dest_file = dest_dir / filename
            shutil.copy2(source_file, dest_file)

            # Создаем документ с относительным путем
            relative_path = f"courses/{course_slug}/{part_slug}/{topic_slug}/{filename}"
            models.TopicDocument.objects.create(
                topic=topic,
                name=fake.sentence(nb_words=3).rstrip("."),
                file=relative_path,
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"Нет тестовых файлов в {test_docs_dir}")
            )
