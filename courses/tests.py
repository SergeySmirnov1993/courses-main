from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from courses.models import Course, CoursePart


class CourseModelTest(TestCase):
    """Тесты модели Course."""

    def test_create_course(self):
        course = Course.objects.create(title="Test Course", description="Test description")
        self.assertEqual(course.title, "Test Course")
        self.assertEqual(course.description, "Test description")
        self.assertEqual(str(course), "Test Course")

    def test_course_unique_title(self):
        Course.objects.create(title="Unique Course", description="")
        with self.assertRaises(IntegrityError):
            Course.objects.create(title="Unique Course", description="duplicate")


class CoursePartModelTest(TestCase):
    """Тесты модели CoursePart."""

    def setUp(self):
        self.course = Course.objects.create(title="Parent Course", description="")

    def test_create_part(self):
        part = CoursePart.objects.create(course=self.course, title="Part 1", description="Part desc")
        self.assertEqual(part.course, self.course)
        self.assertEqual(part.title, "Part 1")
        self.assertIn(part, self.course.parts.all())


class CourseListViewTest(TestCase):
    """Тесты представления списка курсов."""

    def test_courses_list_empty(self):
        response = self.client.get(reverse("courses"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "course_list.html")

    def test_courses_list_with_data(self):
        Course.objects.create(title="Course A", description="Desc A")
        Course.objects.create(title="Course B", description="Desc B")
        response = self.client.get(reverse("courses"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Course A")
        self.assertContains(response, "Course B")


class CourseCreateViewTest(TestCase):
    """Тесты создания курса."""

    def test_create_course_get(self):
        response = self.client.get(reverse("create-course"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "course_form.html")

    def test_create_course_post(self):
        response = self.client.post(
            reverse("create-course"),
            {"title": "New Course", "description": "New description"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Course.objects.filter(title="New Course").exists())


class CourseDetailsViewTest(TestCase):
    """Тесты детальной страницы курса."""

    def setUp(self):
        self.course = Course.objects.create(title="Detail Course", description="Detail desc")

    def test_course_details(self):
        response = self.client.get(reverse("course-details", args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Detail Course")
